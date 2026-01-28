# Multi-stage build for optimized image size
FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY ndaversis_requirements.txt* requirements.txt* ./
RUN if [ -f ndaversis_requirements.txt ]; then \
        pip install --no-cache-dir -r ndaversis_requirements.txt; \
    elif [ -f requirements.txt ]; then \
        pip install --no-cache-dir -r requirements.txt; \
    fi

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Copy Python packages from base stage
COPY --from=base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=base /usr/local/bin /usr/local/bin

# Copy application files
COPY . .

# Create directories for persistent data
RUN mkdir -p /app/state /app/logs

# Expose port for GUI (if running in web mode)
EXPOSE 8080

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Default command - run GUI
CMD ["python", "ndaversis.py"]
