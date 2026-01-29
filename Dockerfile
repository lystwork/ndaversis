# Multi-stage build for optimized image size
FROM python:3.11-slim AS base

# Set working directory
WORKDIR /app

# Install system dependencies for GUI
RUN apt-get update && apt-get install -y \
    git \
    libgl1 \
    libegl1 \
    libxrandr2 \
    libxss1 \
    libxcursor1 \
    libxcomposite1 \
    libasound2 \
    libxi6 \
    libxtst6 \
    libdbus-1-3 \
    libxkbcommon-x11-0 \
    xvfb \
    x11-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY ndaversis_requirements.txt* ./
RUN if [ -f ndaversis_requirements.txt ]; then \
        pip install --no-cache-dir -r ndaversis_requirements.txt; \
    fi

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies in production stage as well
RUN apt-get update && apt-get install -y \
    git \
    libgl1 \
    libegl1 \
    libxrandr2 \
    libxss1 \
    libxcursor1 \
    libxcomposite1 \
    libasound2 \
    libxi6 \
    libxtst6 \
    libdbus-1-3 \
    libxkbcommon-x11-0 \
    xvfb \
    x11-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from base stage
COPY --from=base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=base /usr/local/bin /usr/local/bin

# Copy application files
COPY . .

# Create directories for persistent data
RUN mkdir -p /app/state /app/logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DISPLAY=:99

# Create startup script for GUI
RUN echo '#!/bin/bash\n\
# Start virtual display\n\
Xvfb :99 -screen 0 1024x768x24 &\n\
# Wait a moment for display to start\n\
sleep 2\n\
# Run the application\n\
python ndaversis.py' > /app/start.sh && chmod +x /app/start.sh

# Default command - run GUI with virtual display
CMD ["/app/start.sh"]
