"""
Ndaversis: Agentic Semantic Version Information System.

This module provides a self-contained, monolithic solution for managing
semantic versioning, generating comprehensive README documentation, and leveraging
AI for intelligent content creation. It is designed to be used as an agentic
module, capable of self-development and providing both a command-line interface
(CLI) and a graphical user interface (GUI).

The script can analyze a Python codebase, generate summaries of changes,
and dynamically update the README.md file with detailed information, including
Use Cases, User Stories, and diagrams in Mermaid syntax. It supports multiple
AI providers (such as Google Gemini, OpenAI's ChatGPT, Anthropic's Claude, and
DeepSeek) for content generation, which can be configured through a `config.json`
file.

Core features include:
- Automated semantic versioning (major, minor, patch).
- Dynamic README.md generation with AI-powered content.
- Generation of UML Use Case and BPMN diagrams in Mermaid syntax.
- CLI and GUI for user interaction.
- Health checks to ensure the environment is correctly configured.
- A pre-commit hook to automate version and README updates.
"""
import os
import re
import argparse
import sys
import ast
import json
import datetime
import getpass
from typing import Optional

# Flet for modern GUI
try:
    import flet as ft
except ImportError:
    ft = None

# import google.generativeai as genai
# import openai
# import anthropic
# from deepseek import DeepSeekAPI

import difflib

# Import version history module
try:
    import ndaversis_version_history as version_history
except ImportError:
    version_history = None

# --- Constants ---
# Dual README system
USER_README_FILE = "readme.md"  # User's unified repository
NDAVERSIS_README_FILE = "ndaversis_readme.md"  # Ndaversis-specific info
README_FILE = NDAVERSIS_README_FILE  # Default for backward compatibility

CONFIG_FILE = "config.json"
STATE_FILE = "ndaversis_state.json"
LOGS_FILE = "ndaversis_logs.py"
VERSION_HISTORY_FILE = "ndaversis_version_history.py"
PRIVACY_POLICY_FILE = "ndaversis_privacy_policy.md"
LICENSE_FILE = "LICENSE_ndaversis"
REQUIREMENTS_FILE = "ndaversis_requirements.txt"
CONTACT_EMAIL = "n@ndaotec.com"
COPYRIGHT_HOLDER = "Nikita Andreevich Drozdov"
REPOSITORY_ADDRESS = "https://github.com/lystwork/ndaversis"
COPYRIGHT_TEXT = (
    "ndaotec.com. @ All rights reserved - Nikita Andreevich Drozdov. "
    "All rights belong to their respective owners."
)
__version__ = "0.0.66"

# --- AI Service Classes ---
import time
from collections import deque

class RateLimiter:
    """
    Rate limiter using sliding window algorithm.
    Limits requests globally across all AI providers.
    """
    def __init__(self, max_requests: int = 4, time_window: int = 60) -> None:
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum number of requests allowed in time window
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()
    
    def can_proceed(self) -> bool:
        """Check if a new request can proceed without exceeding rate limit."""
        now = time.time()
        # Remove requests outside the time window
        while self.requests and self.requests[0] < now - self.time_window:
            self.requests.popleft()
        
        return len(self.requests) < self.max_requests
    
    def wait_if_needed(self) -> None:
        """Wait if rate limit is exceeded."""
        while not self.can_proceed():
            now = time.time()
            if self.requests:
                wait_time = self.time_window - (now - self.requests[0])
                if wait_time > 0:
                    print(f"Rate limit exceeded. Waiting {wait_time:.1f} seconds...")
                    time.sleep(min(wait_time + 0.1, 1.0))  # Sleep in small increments
            else:
                break
    
    def record_request(self) -> None:
        """Record a new request."""
        self.requests.append(time.time())


class AIServiceManager:
    """
    Manages multiple AI service providers with automatic fallback.
    Implements rate limiting and error handling.
    """
    def __init__(self, config: dict) -> None:
        """
        Initialize AI service manager.
        
        Args:
            config: Configuration dictionary with provider settings
        """
        self.config = config
        self.providers = {}
        self.fallback_chain = []
        
        # Initialize rate limiter
        rate_config = config.get("ai_providers", {}).get("rate_limit", {})
        max_requests = rate_config.get("max_requests", 4)
        time_window = rate_config.get("time_window_seconds", 60)
        self.rate_limiter = RateLimiter(max_requests, time_window)
        
        # Initialize providers
        self._initialize_providers()
    
    def _initialize_providers(self) -> None:
        """Initialize all configured AI providers."""
        ai_config = self.config.get("ai_providers", {})
        primary = ai_config.get("primary", "gemini")
        fallback_chain = ai_config.get("fallback_chain", [])
        providers_config = ai_config.get("providers", {})
        
        # Build complete chain: primary + fallbacks
        self.fallback_chain = [primary] + fallback_chain
        
        # Service class mapping
        service_map = {
            "gemini": GeminiService,
            "chatgpt": ChatGPTService,
            "claude": ClaudeService,
            "deepseek": DeepSeekService,
            "groq": GroqService,
            "openrouter": OpenRouterService,
            "mistral": MistralService,
            "qwen": QwenService,
            "llama": LlamaService,
            "openai_compatible": OpenAICompatibleService,
        }
        
        # Initialize each provider in the chain
        for provider_name in self.fallback_chain:
            api_key_env = f"{provider_name.upper()}_API_KEY"
            api_key = os.getenv(api_key_env)
            
            if not api_key:
                continue  # Skip providers without API keys
            
            service_class = service_map.get(provider_name)
            if not service_class:
                continue
            
            try:
                # Get provider-specific config
                provider_cfg = providers_config.get(provider_name, {})
                model = provider_cfg.get("model") or os.getenv(f"{provider_name.upper()}_MODEL")
                api_base = provider_cfg.get("api_base") or os.getenv(f"{provider_name.upper()}_API_BASE")
                
                # Initialize service based on requirements
                if provider_name == "openai_compatible":
                    if api_base:
                        self.providers[provider_name] = service_class(api_key, api_base, model or "gpt-3.5-turbo")
                elif provider_name == "llama":
                    if model and api_base:
                        self.providers[provider_name] = service_class(api_key, model, api_base)
                    elif model:
                        self.providers[provider_name] = service_class(api_key, model)
                    else:
                        self.providers[provider_name] = service_class(api_key)
                elif model:
                    self.providers[provider_name] = service_class(api_key, model)
                else:
                    self.providers[provider_name] = service_class(api_key)
                    
                print(f"Initialized AI provider: {provider_name}")
            except Exception as e:
                print(f"Failed to initialize {provider_name}: {e}")
    
    def generate_content(self, prompt: str, analysis_data: dict) -> str:
        """
        Generate content using available providers with fallback.
        
        Args:
            prompt: The prompt for content generation
            analysis_data: Code analysis data
            
        Returns:
            Generated content string
        """
        # Wait if rate limit is exceeded
        self.rate_limiter.wait_if_needed()
        
        # Try each provider in the fallback chain
        for provider_name in self.fallback_chain:
            if provider_name not in self.providers:
                continue
            
            try:
                print(f"Attempting to use AI provider: {provider_name}")
                service = self.providers[provider_name]
                
                # Record request for rate limiting
                self.rate_limiter.record_request()
                
                # Generate content
                result = service.generate_content(prompt, analysis_data)
                print(f"Successfully generated content using: {provider_name}")
                return result
                
            except Exception as e:
                error_msg = str(e).lower()
                print(f"Provider {provider_name} failed: {e}")
                
                # Check for insufficient balance
                if "insufficient" in error_msg or "balance" in error_msg or "quota" in error_msg:
                    print(f"Provider {provider_name} has insufficient balance, trying next provider...")
                    continue
                
                # Check for rate limit errors
                if "rate" in error_msg or "limit" in error_msg:
                    print(f"Provider {provider_name} rate limited, trying next provider...")
                    continue
                
                # Other errors - try next provider
                continue
        
        # All providers failed - return empty string or fallback message
        print("All AI providers failed. Using offline mode.")
        return ""


class AIService:
    """
    Abstract base class for AI services.

    This class defines the interface for different AI service implementations,
    providing a common structure for generating content based on a prompt and
    code analysis data.
    """

    def __init__(self) -> None:
        """Initializes the AIService."""

    def _create_full_prompt(self, prompt: str, analysis_data: dict) -> str:
        """
        Creates the full prompt with code analysis data.

        Args:
            prompt (str): The base prompt for the AI service.
            analysis_data (dict): A dictionary containing codebase
                                            analysis data.

        Returns:
            str: The complete prompt including the analysis data.
        """
        return f"{prompt}\n\nCode Analysis:\n{json.dumps(analysis_data, indent=2)}"

    def generate_content(self, prompt: str, analysis_data: dict) -> str:
        """
        Generate content using the AI service.

        This method must be implemented by subclasses.

        Args:
            prompt (str): The prompt to send to the AI service.
            analysis_data (dict): The code analysis data.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.

        Returns:
            str: The generated content from the AI service.
        """
        raise NotImplementedError("This method must be implemented by a subclass.")

class GeminiService(AIService):
    """
    An AI service that uses the Google Gemini API.

    This class interacts with the Google Gemini API to generate content based on
    prompts and codebase analysis. It requires a valid API key for
    authentication.
    """

    def __init__(self, api_key: str) -> None:
        """
        Initializes the GeminiService.

        Args:
            api_key (str): The API key for the Google Gemini service.
        """
        super().__init__()
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-pro")

    def generate_content(self, prompt: str, analysis_data: dict) -> str:
        """
        Generates content using the Google Gemini API.

        Args:
            prompt (str): The prompt to send to the Gemini API.
            analysis_data (dict): The code analysis data.

        Returns:
            str: The generated content from the Gemini API.
        """
        full_prompt = self._create_full_prompt(prompt, analysis_data)
        response = self.model.generate_content(full_prompt)
        return response.text

class ChatGPTService(AIService):
    """An AI service that uses the OpenAI ChatGPT API."""
    def __init__(self, api_key):
        super().__init__()
        self.client = openai.OpenAI(api_key=api_key)

    def generate_content(self, prompt, analysis_data):
        full_prompt = self._create_full_prompt(prompt, analysis_data)
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo", messages=[{"role": "user", "content": full_prompt}]
        )
        return response.choices[0].message.content

class ClaudeService(AIService):
    """
    An AI service that uses the Anthropic Claude API.

    This class interacts with the Anthropic Claude API to generate content.
    It requires a valid API key for authentication.
    """

    def __init__(self, api_key: str) -> None:
        """
        Initializes the ClaudeService.

        Args:
            api_key (str): The API key for the Anthropic service.
        """
        super().__init__()
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate_content(self, prompt: str, analysis_data: dict) -> str:
        """
        Generates content using the Anthropic Claude API.

        Args:
            prompt (str): The prompt to send to the Claude API.
            analysis_data (dict): The code analysis data.

        Returns:
            str: The generated content from the Claude API.
        """
        full_prompt = self._create_full_prompt(prompt, analysis_data)
        message = self.client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1024,
            messages=[{"role": "user", "content": full_prompt}],
        )
        if message.content:
            return message.content[0].text
        return ""

class DeepSeekService(AIService):
    """
    An AI service that uses the DeepSeek API.

    This class interacts with the DeepSeek API to generate content.
    It requires a valid API key for authentication.
    """

    def __init__(self, api_key: str) -> None:
        """
        Initializes the DeepSeekService.

        Args:
            api_key (str): The API key for the DeepSeek service.
        """
        super().__init__()
        self.client = DeepSeekAPI(api_key=api_key)

    def generate_content(self, prompt: str, analysis_data: dict) -> str:
        """
        Generates content using the DeepSeek API.

        Args:
            prompt (str): The prompt to send to the DeepSeek API.
            analysis_data (dict): The code analysis data.

        Returns:
            str: The generated content from the DeepSeek API.
        """
        full_prompt = self._create_full_prompt(prompt, analysis_data)
        response = self.client.chat.completions.create(
            model="deepseek-chat", messages=[{"role": "user", "content": full_prompt}]
        )
        return response.choices[0].message.content

class GroqService(AIService):
    """
    An AI service that uses the Groq API.
    """
    def __init__(self, api_key: str, model: str = "mixtral-8x7b-32768") -> None:
        super().__init__()
        import openai
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        self.model = model

    def generate_content(self, prompt: str, analysis_data: dict) -> str:
        full_prompt = self._create_full_prompt(prompt, analysis_data)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": full_prompt}]
        )
        return response.choices[0].message.content

class OpenRouterService(AIService):
    """
    An AI service that uses the OpenRouter API.
    """
    def __init__(self, api_key: str, model: str = "anthropic/claude-3-haiku") -> None:
        super().__init__()
        import openai
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        self.model = model

    def generate_content(self, prompt: str, analysis_data: dict) -> str:
        full_prompt = self._create_full_prompt(prompt, analysis_data)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": full_prompt}]
        )
        return response.choices[0].message.content

class MistralService(AIService):
    """
    An AI service that uses the Mistral API.
    """
    def __init__(self, api_key: str, model: str = "mistral-small-latest") -> None:
        super().__init__()
        import openai
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.mistral.ai/v1"
        )
        self.model = model

    def generate_content(self, prompt: str, analysis_data: dict) -> str:
        full_prompt = self._create_full_prompt(prompt, analysis_data)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": full_prompt}]
        )
        return response.choices[0].message.content

class QwenService(AIService):
    """
    An AI service that uses the Qwen API (Alibaba Cloud).
    """
    def __init__(self, api_key: str, model: str = "qwen-turbo") -> None:
        super().__init__()
        import openai
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        self.model = model

    def generate_content(self, prompt: str, analysis_data: dict) -> str:
        full_prompt = self._create_full_prompt(prompt, analysis_data)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": full_prompt}]
        )
        return response.choices[0].message.content

class LlamaService(AIService):
    """
    An AI service that uses Llama models via Together AI or similar providers.
    """
    def __init__(self, api_key: str, model: str = "meta-llama/Llama-3-70b-chat-hf", base_url: str = "https://api.together.xyz/v1") -> None:
        super().__init__()
        import openai
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.model = model

    def generate_content(self, prompt: str, analysis_data: dict) -> str:
        full_prompt = self._create_full_prompt(prompt, analysis_data)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": full_prompt}]
        )
        return response.choices[0].message.content

class OpenAICompatibleService(AIService):
    """
    An AI service compatible with the OpenAI API (e.g., for on-premise LLMs, LocalAI, RAG).
    """
    def __init__(self, api_key: str, base_url: str, model: str = "gpt-3.5-turbo") -> None:
        super().__init__()
        import openai
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    def generate_content(self, prompt: str, analysis_data: dict) -> str:
        full_prompt = self._create_full_prompt(prompt, analysis_data)
        response = self.client.chat.completions.create(
            model=self.model, messages=[{"role": "user", "content": full_prompt}]
        )
        return response.choices[0].message.content

# --- Version Class ---
class Version:
    """
    A class to represent a semantic version.

    Attributes:
        major (int): The major version number.
        minor (int): The minor version number.
        patch (int): The patch version number.
    """

    def __init__(self, major: int = 0, minor: int = 0, patch: int = 0) -> None:
        """
        Initializes the Version object.

        Args:
            major (int): The major version number.
            minor (int): The minor version number.
            patch (int): The patch version number.
        """
        self.major: int = major
        self.minor: int = minor
        self.patch: int = patch

    def __str__(self) -> str:
        """
        Returns the string representation of the version.

        Returns:
            str: The version string in "major.minor.patch" format.
        """
        return f"{self.major}.{self.minor}.{self.patch}"

    def increment_major(self) -> None:
        """Increments the major version and resets minor and patch versions."""
        self.major += 1
        self.minor = 0
        self.patch = 0

    def increment_minor(self) -> None:
        """Increments the minor version and resets the patch version."""
        self.minor += 1
        self.patch = 0

    def increment_patch(self) -> None:
        """Increments the patch version."""
        self.patch += 1

# --- Repository Metrics Class ---
class RepositoryMetrics:
    """
    Comprehensive repository evaluation system.
    Analyzes repository across 15 key metrics with AI-powered summaries.
    """
    
    def __init__(self, ndaversis_instance) -> None:
        """Initialize metrics analyzer with reference to main Ndaversis instance."""
        self.ndaversis = ndaversis_instance
        self.metrics_cache = {}
        self.cache_timestamp = None
        self.cache_ttl = 1800  # 30 minutes cache
    
    def _get_ai_summary(self, metric_name: str, data: dict) -> str:
        """Generate AI summary for a metric."""
        if not self.ndaversis.ai_service:
            return f"AI summary unavailable. {metric_name} calculated based on code analysis."
        
        prompt = (
            f"Provide a brief 2-3 sentence summary of the {metric_name} metric for this repository. "
            f"Be specific and actionable. Data: {json.dumps(data, indent=2)}"
        )
        
        try:
            return self.ndaversis.ai_service.generate_content(prompt, data)
        except:
            return f"AI summary generation failed. {metric_name} score: {data.get('score', 0)}%"
    
    def calculate_code_quality(self) -> dict:
        """
        Evaluate code quality based on docstrings, type hints, and complexity.
        Returns score (0-100%) and AI summary.
        """
        features, _ = self.ndaversis._analyze_codebase()
        
        total_functions = len(features["functions"])
        total_classes = len(features["classes"])
        total_items = total_functions + total_classes
        
        if total_items == 0:
            return {"score": 50, "summary": "No Python code to analyze", "details": {}}
        
        # Count documented items
        documented = 0
        for func_data in features["functions"].values():
            if func_data.get("docstring"):
                documented += 1
        
        for class_data in features["classes"].values():
            if class_data.get("docstring"):
                documented += 1
        
        doc_coverage = (documented / total_items) * 100 if total_items > 0 else 0
        
        # Calculate score (weighted: 70% docstrings, 30% code/comment ratio)
        metrics = features["metrics"]
        total_lines = metrics["code_lines"] + metrics["comment_lines"]
        comment_ratio = (metrics["comment_lines"] / total_lines * 100) if total_lines > 0 else 0
        
        score = int((doc_coverage * 0.7) + (min(comment_ratio, 30) * 0.3))
        
        details = {
            "docstring_coverage": f"{doc_coverage:.1f}%",
            "comment_ratio": f"{comment_ratio:.1f}%",
            "documented_items": f"{documented}/{total_items}"
        }
        
        summary = self._get_ai_summary("Code Quality", {"score": score, **details})
        return {"score": score, "summary": summary, "details": details}
    
    def calculate_code_size(self) -> dict:
        """Evaluate code size and distribution."""
        features, _ = self.ndaversis._analyze_codebase()
        metrics = features["metrics"]
        
        total_lines = metrics["total_lines"]
        code_lines = metrics["code_lines"]
        
        # Score based on reasonable size (sweet spot: 1000-10000 lines)
        if code_lines < 100:
            score = 30
        elif code_lines < 1000:
            score = 50 + int((code_lines / 1000) * 30)
        elif code_lines <= 10000:
            score = 90
        else:
            score = max(50, 90 - int((code_lines - 10000) / 1000))
        
        details = {
            "total_lines": total_lines,
            "code_lines": code_lines,
            "comment_lines": metrics["comment_lines"],
            "blank_lines": metrics["blank_lines"]
        }
        
        summary = self._get_ai_summary("Code Size", {"score": score, **details})
        return {"score": score, "summary": summary, "details": details}
    
    def calculate_security(self) -> dict:
        """Evaluate security practices."""
        features, code = self.ndaversis._analyze_codebase()
        
        # Check for common security issues
        issues = []
        score = 100
        
        # Check for hardcoded secrets (simple patterns)
        if re.search(r'(password|secret|api_key)\s*=\s*["\'][^"\']+["\']', code, re.IGNORECASE):
            issues.append("Potential hardcoded secrets detected")
            score -= 30
        
        # Check for eval/exec usage
        if 'eval(' in code or 'exec(' in code:
            issues.append("Use of eval/exec detected (security risk)")
            score -= 20
        
        # Check for SQL injection risks (basic check)
        if re.search(r'execute\(["\'].*%s.*["\']\s*%', code):
            issues.append("Potential SQL injection vulnerability")
            score -= 25
        
        # Check for proper error handling
        if 'except:' in code or 'except Exception:' in code:
            issues.append("Broad exception handling detected")
            score -= 10
        
        score = max(0, score)
        
        details = {
            "issues_found": len(issues),
            "issues": issues if issues else ["No major security issues detected"]
        }
        
        summary = self._get_ai_summary("Security", {"score": score, **details})
        return {"score": score, "summary": summary, "details": details}
    
    def calculate_applicability(self) -> dict:
        """Evaluate applicability and use case coverage."""
        features, _ = self.ndaversis._analyze_codebase()
        
        # Score based on number of public functions/classes
        public_functions = sum(1 for name in features["functions"].keys() if not name.startswith('_'))
        public_classes = sum(1 for name in features["classes"].keys() if not name.startswith('_'))
        
        total_public = public_functions + public_classes
        
        if total_public < 5:
            score = 40
        elif total_public < 15:
            score = 60
        elif total_public < 30:
            score = 80
        else:
            score = 95
        
        details = {
            "public_functions": public_functions,
            "public_classes": public_classes,
            "total_public_api": total_public
        }
        
        summary = self._get_ai_summary("Applicability", {"score": score, **details})
        return {"score": score, "summary": summary, "details": details}
    
    def calculate_platform_compatibility(self) -> dict:
        """Evaluate cross-platform compatibility."""
        features, code = self.ndaversis._analyze_codebase()
        
        score = 100
        issues = []
        
        # Check for OS-specific code
        if 'platform.system()' in code or 'os.name' in code:
            score = 90  # Good - handles platform differences
        
        # Check for Windows-specific paths
        if re.search(r'[A-Z]:\\\\', code):
            issues.append("Windows-specific paths detected")
            score -= 15
        
        # Check for Unix-specific features
        if 'os.fork()' in code or '/dev/' in code:
            issues.append("Unix-specific features detected")
            score -= 15
        
        # Bonus for using pathlib
        if 'pathlib' in features["imports"] or 'Path' in code:
            score = min(100, score + 10)
        
        score = max(0, score)
        
        details = {
            "estimated_compatibility": f"{score}%",
            "issues": issues if issues else ["Good cross-platform practices"]
        }
        
        summary = self._get_ai_summary("Platform Compatibility", {"score": score, **details})
        return {"score": score, "summary": summary, "details": details}
    
    def calculate_quantity(self) -> dict:
        """Evaluate quantity of features and functionality."""
        features, _ = self.ndaversis._analyze_codebase()
        
        total_functions = len(features["functions"])
        total_classes = len(features["classes"])
        total_files = len([f for f in features["files"] if f.endswith('.py')])
        
        # Score based on total functionality
        total_items = total_functions + total_classes
        
        if total_items < 10:
            score = 30
        elif total_items < 30:
            score = 50
        elif total_items < 100:
            score = 75
        else:
            score = 95
        
        details = {
            "total_functions": total_functions,
            "total_classes": total_classes,
            "total_files": total_files,
            "total_items": total_items
        }
        
        summary = self._get_ai_summary("Quantity", {"score": score, **details})
        return {"score": score, "summary": summary, "details": details}
    
    def calculate_performance(self) -> dict:
        """Evaluate performance considerations."""
        features, code = self.ndaversis._analyze_codebase()
        
        score = 70  # Base score
        optimizations = []
        concerns = []
        
        # Check for performance optimizations
        if 'cache' in code.lower() or 'memoize' in code.lower():
            optimizations.append("Caching implemented")
            score += 10
        
        if 'async' in code or 'await' in code:
            optimizations.append("Async operations used")
            score += 10
        
        # Check for performance concerns
        if code.count('for ') > 50:
            concerns.append("Many loops detected")
            score -= 5
        
        if 'sleep(' in code:
            concerns.append("Blocking sleep calls found")
            score -= 10
        
        score = max(0, min(100, score))
        
        details = {
            "optimizations": optimizations if optimizations else ["No specific optimizations detected"],
            "concerns": concerns if concerns else ["No major performance concerns"]
        }
        
        summary = self._get_ai_summary("Performance", {"score": score, **details})
        return {"score": score, "summary": summary, "details": details}
    
    def calculate_usability(self) -> dict:
        """Evaluate usability and API clarity."""
        features, _ = self.ndaversis._analyze_codebase()
        
        # Check for README
        has_readme = any('readme' in f.lower() for f in features["files"])
        
        # Check for examples
        has_examples = any('example' in f.lower() for f in features["files"])
        
        # Check for documentation
        doc_score = self.calculate_code_quality()["score"]
        
        score = 0
        if has_readme:
            score += 40
        if has_examples:
            score += 20
        score += int(doc_score * 0.4)
        
        details = {
            "has_readme": has_readme,
            "has_examples": has_examples,
            "documentation_score": f"{doc_score}%"
        }
        
        summary = self._get_ai_summary("Usability", {"score": score, **details})
        return {"score": score, "summary": summary, "details": details}
    
    def calculate_reliability(self) -> dict:
        """Evaluate reliability through error handling and tests."""
        features, code = self.ndaversis._analyze_codebase()
        
        score = 50  # Base score
        
        # Check for tests
        has_tests = any('test' in f.lower() for f in features["files"])
        if has_tests:
            score += 30
        
        # Check for error handling
        try_count = code.count('try:')
        except_count = code.count('except')
        
        if try_count > 0 and except_count > 0:
            score += 20
        
        # Check for logging
        if 'logging' in features["imports"] or 'logger' in code.lower():
            score += 10
        
        score = min(100, score)
        
        details = {
            "has_tests": has_tests,
            "error_handling": f"{try_count} try blocks",
            "has_logging": 'logging' in features["imports"]
        }
        
        summary = self._get_ai_summary("Reliability", {"score": score, **details})
        return {"score": score, "summary": summary, "details": details}
    
    def calculate_innovation(self) -> dict:
        """Evaluate innovation and modern practices."""
        features, code = self.ndaversis._analyze_codebase()
        
        score = 50  # Base score
        innovations = []
        
        # Check for modern Python features
        if 'typing' in features["imports"] or 'Type' in code:
            innovations.append("Type hints used")
            score += 15
        
        if 'dataclass' in code or '@dataclass' in code:
            innovations.append("Dataclasses used")
            score += 10
        
        if 'async' in code or 'await' in code:
            innovations.append("Async/await patterns")
            score += 10
        
        if 'pathlib' in features["imports"]:
            innovations.append("Modern path handling")
            score += 5
        
        # Check for AI/ML
        if any(lib in features["imports"] for lib in ['tensorflow', 'torch', 'sklearn', 'transformers']):
            innovations.append("AI/ML integration")
            score += 15
        
        score = min(100, score)
        
        details = {
            "innovations": innovations if innovations else ["Standard implementation"],
            "modern_features": len(innovations)
        }
        
        summary = self._get_ai_summary("Innovation", {"score": score, **details})
        return {"score": score, "summary": summary, "details": details}
    
    def calculate_simplicity(self) -> dict:
        """Evaluate code simplicity and clarity."""
        features, code = self.ndaversis._analyze_codebase()
        metrics = features["metrics"]
        
        # Calculate average function length
        total_code = metrics["code_lines"]
        total_functions = len(features["functions"]) + sum(len(c["methods"]) for c in features["classes"].values())
        
        avg_function_length = total_code / max(total_functions, 1)
        
        # Score based on simplicity metrics
        if avg_function_length < 10:
            score = 95
        elif avg_function_length < 20:
            score = 85
        elif avg_function_length < 50:
            score = 70
        else:
            score = 50
        
        # Adjust for nesting complexity (rough estimate)
        nesting_level = code.count('    ') / max(metrics["code_lines"], 1)
        if nesting_level > 3:
            score -= 15
        
        score = max(0, score)
        
        details = {
            "avg_function_length": f"{avg_function_length:.1f} lines",
            "total_functions": total_functions,
            "estimated_complexity": "Low" if score > 75 else "Medium" if score > 50 else "High"
        }
        
        summary = self._get_ai_summary("Simplicity", {"score": score, **details})
        return {"score": score, "summary": summary, "details": details}
    
    def calculate_aesthetics(self) -> dict:
        """Evaluate code aesthetics and style."""
        features, code = self.ndaversis._analyze_codebase()
        
        score = 70  # Base score
        style_points = []
        
        # Check for consistent naming
        if all(name.islower() or '_' in name for name in features["functions"].keys()):
            style_points.append("Consistent function naming")
            score += 10
        
        # Check for PEP 8 compliance indicators
        if metrics := features["metrics"]:
            if metrics["tabs"] == 0:  # Spaces over tabs
                style_points.append("Uses spaces (PEP 8)")
                score += 10
        
        # Check for docstrings
        if any(f.get("docstring") for f in features["functions"].values()):
            style_points.append("Functions documented")
            score += 10
        
        score = min(100, score)
        
        details = {
            "style_points": style_points if style_points else ["Basic style compliance"],
            "uses_tabs": features["metrics"]["tabs"] > 0
        }
        
        summary = self._get_ai_summary("Aesthetics", {"score": score, **details})
        return {"score": score, "summary": summary, "details": details}
    
    def calculate_duration(self) -> dict:
        """Evaluate long-term maintainability."""
        features, code = self.ndaversis._analyze_codebase()
        
        score = 70  # Base score
        factors = []
        
        # Check for version control
        if os.path.exists('.git'):
            factors.append("Version control in use")
            score += 10
        
        # Check for dependencies management
        if os.path.exists('ndaversis_requirements.txt') or os.path.exists('pyproject.toml'):
            factors.append("Dependencies managed")
            score += 10
        
        # Check for TODO/FIXME
        todo_count = code.count('TODO') + code.count('FIXME')
        if todo_count > 10:
            factors.append(f"{todo_count} TODOs found")
            score -= 10
        
        # Check for tests
        if any('test' in f.lower() for f in features["files"]):
            factors.append("Test suite exists")
            score += 10
        
        score = max(0, min(100, score))
        
        details = {
            "maintainability_factors": factors,
            "todo_count": todo_count
        }
        
        summary = self._get_ai_summary("Duration/Maintainability", {"score": score, **details})
        return {"score": score, "summary": summary, "details": details}
    
    def calculate_accuracy(self) -> dict:
        """Evaluate code correctness and testing."""
        features, code = self.ndaversis._analyze_codebase()
        
        score = 60  # Base score
        
        # Check for tests
        test_files = [f for f in features["files"] if 'test' in f.lower()]
        if test_files:
            score += 25
        
        # Check for type hints (helps with correctness)
        if 'typing' in features["imports"]:
            score += 15
        
        # Check for assertions
        if 'assert' in code:
            score += 10
        
        score = min(100, score)
        
        details = {
            "test_files": len(test_files),
            "has_type_hints": 'typing' in features["imports"],
            "has_assertions": 'assert' in code
        }
        
        summary = self._get_ai_summary("Accuracy", {"score": score, **details})
        return {"score": score, "summary": summary, "details": details}
    
    def calculate_completeness(self) -> dict:
        """Evaluate feature completeness."""
        features, code = self.ndaversis._analyze_codebase()
        
        score = 70  # Base score
        completeness_factors = []
        
        # Check for README
        if any('readme' in f.lower() for f in features["files"]):
            completeness_factors.append("README present")
            score += 10
        
        # Check for LICENSE
        if any('license' in f.lower() for f in features["files"]):
            completeness_factors.append("LICENSE present")
            score += 5
        
        # Check for setup/installation files
        if any(f in features["files"] for f in ['setup.py', 'pyproject.toml', 'ndaversis_requirements.txt']):
            completeness_factors.append("Installation files present")
            score += 10
        
        # Check for TODOs (incompleteness indicator)
        todo_count = code.count('TODO') + code.count('FIXME') + code.count('XXX')
        if todo_count > 0:
            completeness_factors.append(f"{todo_count} TODOs remaining")
            score -= min(20, todo_count * 2)
        
        score = max(0, min(100, score))
        
        details = {
            "completeness_factors": completeness_factors,
            "todo_count": todo_count
        }
        
        summary = self._get_ai_summary("Completeness", {"score": score, **details})
        return {"score": score, "summary": summary, "details": details}
    
    def get_all_metrics(self) -> dict:
        """Calculate all metrics and return comprehensive report."""
        import time
        
        # Check cache
        if self.metrics_cache and self.cache_timestamp:
            if time.time() - self.cache_timestamp < self.cache_ttl:
                print("Using cached metrics...")
                return self.metrics_cache
        
        print("Calculating repository metrics...")
        
        metrics = {
            "code_quality": self.calculate_code_quality(),
            "code_size": self.calculate_code_size(),
            "security": self.calculate_security(),
            "applicability": self.calculate_applicability(),
            "platform_compatibility": self.calculate_platform_compatibility(),
            "quantity": self.calculate_quantity(),
            "performance": self.calculate_performance(),
            "usability": self.calculate_usability(),
            "reliability": self.calculate_reliability(),
            "innovation": self.calculate_innovation(),
            "simplicity": self.calculate_simplicity(),
            "aesthetics": self.calculate_aesthetics(),
            "duration": self.calculate_duration(),
            "accuracy": self.calculate_accuracy(),
            "completeness": self.calculate_completeness(),
        }
        
        # Calculate overall score
        total_score = sum(m["score"] for m in metrics.values())
        avg_score = total_score / len(metrics)
        
        result = {
            "overall_score": int(avg_score),
            "metrics": metrics,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Update cache
        self.metrics_cache = result
        self.cache_timestamp = time.time()
        
        return result


# --- Main Application Class ---
class Ndaversis:
    """
    The main class for the Ndaversis application.

    This class encapsulates the core functionality of the application, including
    version management, codebase analysis, README generation, and AI service
    integration.

    Attributes:
        version (Version): The current version of the project.
        ai_config (dict): The AI provider configuration.
        previous_code_state (dict): The code state from the last run.
        ai_service (Optional[AIService]): The AI service instance.
    """

    def __init__(self) -> None:
        """
        Initializes the Ndaversis application.

        This method sets up the initial state by loading the version,
        AI configuration, and the previous code state, and then initializes
        the AI service.
        """
        self.version: Version = self.get_version()
        self.ai_config: dict = self.load_ai_config()
        self.previous_code_state: dict = self.load_previous_code_state()
        self.ai_service: Optional[AIService] = self.get_ai_service()
        self.metrics: RepositoryMetrics = RepositoryMetrics(self)

    def is_ndaversis_repo(self):
        """
        Detect if running in the ndaversis repository itself.
        
        Returns:
            bool: True if in ndaversis repo, False if in user's repo
        """
        # Count non-ndaversis files to determine context
        user_files = []
        for root, dirs, files in os.walk('.'):
            if '.git' in root or '__pycache__' in root or 'tests_ndaversis' in root:
                continue
            for file in files:
                # Skip ndaversis-specific files
                if (not file.startswith('ndaversis') and 
                    not file.startswith('LICENSE') and 
                    file not in ['.gitignore', 'config.json', '.DS_Store']):
                    user_files.append(file)
        
        # If we have few non-ndaversis files, we're in ndaversis repo
        # Threshold: less than 3 non-ndaversis files means it's the ndaversis repo
        return len(user_files) < 3

    def get_version(self) -> Version:
        """
        Get the current version from the `__version__` variable.

        This method reads the `__version__` string, parses it, and returns a
        `Version` object.

        Returns:
            Version: A `Version` object representing the current version.
        """
        major, minor, patch = map(int, __version__.split("."))
        return Version(major, minor, patch)

    def save_version(self, version_str: str, filepath: Optional[str] = None) -> None:
        """
        Save the version back to the ndaversis.py file.

        This method updates the `__version__` string in the specified file
        (or the current file by default) with the new version.

        Args:
            version_str (str): The new version string to save.
            filepath (Optional[str]): The path to the file to update.
                                     Defaults to the current file.
        """
        if filepath is None:
            filepath = __file__
        with open(filepath, "r+", encoding="utf-8") as f:
            content = f.read()
            new_content = re.sub(
                r'__version__ = "\d+\.\d+\.\d+"',
                f'__version__ = "{version_str}"',
                content,
            )
            f.seek(0)
            f.write(new_content)
            f.truncate()

    def load_ai_config(self) -> dict:
        """
        Load AI configuration from config.json.

        This method reads the `config.json` file and returns the configuration
        as a dictionary. It handles potential errors like the file not being
        found or being invalid JSON.

        Returns:
            dict: The AI configuration, or an empty dictionary if
                            an error occurs.
        """
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Configuration file '{CONFIG_FILE}' not found. AI service disabled.")
            return {}
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading AI configuration from {CONFIG_FILE}: {e}")
            return {}

    def get_ai_service(self):
        """Factory function to get an AI service manager instance with fallback support."""
        if not self.ai_config:
            return None

        # Check if using new multi-provider config
        if "ai_providers" in self.ai_config:
            try:
                return AIServiceManager(self.ai_config)
            except Exception as e:
                print(f"Failed to initialize AI Service Manager: {e}")
                return None
        
        # Fallback to legacy single-provider config
        provider = self.ai_config.get("ai_provider")
        if not provider:
            print("No AI provider specified in the config. AI service disabled.")
            return None

        api_key_env_var = f"{provider.upper()}_API_KEY"
        api_key = os.getenv(api_key_env_var)

        service_map = {
            "gemini": GeminiService,
            "chatgpt": ChatGPTService,
            "claude": ClaudeService,
            "deepseek": DeepSeekService,
            "groq": GroqService,
            "openrouter": OpenRouterService,
            "mistral": MistralService,
            "qwen": QwenService,
            "llama": LlamaService,
            "openai_compatible": OpenAICompatibleService,
        }

        service_class = service_map.get(provider)

        if service_class:
            if provider == "openai_compatible":
                base_url = self.ai_config.get("api_base") or os.getenv("AI_API_BASE")
                model = self.ai_config.get("model") or os.getenv("AI_MODEL") or "gpt-3.5-turbo"
                if not base_url:
                    print("api_base not specified for openai_compatible provider. AI service disabled.")
                    return None
                return service_class(api_key or "no-key", base_url, model)
            
            if api_key:
                return service_class(api_key)
            else:
                print(f"{api_key_env_var} environment variable not found. AI service disabled.")
        else:
            print(f"Unknown AI provider: {provider}. AI service disabled.")

        return None

    def load_previous_code_state(self) -> dict:
        """Load the previous code state from the state file."""
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, IOError, json.JSONDecodeError):
            return {}

    def _process_python_file(self, filepath, features, method_names):
        """Process a single Python file to extract features and metrics."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()
                code = "".join(lines)
            
            # Basic metrics
            features["metrics"]["total_lines"] += len(lines)
            features["metrics"]["tabs"] += code.count('\t')
            # Count string literals using a simple regex for the analysis summary
            features["metrics"]["strings"] += len(re.findall(r'(\".*?\"|\'.*?\')', code))
            
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    features["metrics"]["blank_lines"] += 1
                elif stripped.startswith("#"):
                    features["metrics"]["comment_lines"] += 1
                else:
                    features["metrics"]["code_lines"] += 1

            tree = ast.parse(code)
            module_docstring = ast.get_docstring(tree) or ""
            features["files"][filepath] = {"docstring": module_docstring}
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = {}
                    for item in node.body:
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            methods[item.name] = {
                                "args": [arg.arg for arg in item.args.args if arg.arg != "self"],
                                "docstring": ast.get_docstring(item) or "",
                            }
                    method_names.update(methods.keys())
                    features["classes"][node.name] = {
                        "docstring": ast.get_docstring(node) or "",
                        "methods": methods
                    }
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        features["imports"].add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom) and node.module:
                    features["imports"].add(node.module.split('.')[0])
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name not in method_names:
                    # Only add if it's a top-level function (direct child of Module)
                    if any(module_item == node for module_item in tree.body):
                        docstring = ast.get_docstring(node)
                        features["functions"][node.name] = {
                            "args": [arg.arg for arg in node.args.args],
                            "docstring": docstring if docstring else "",
                        }
        except (SyntaxError, IOError, UnicodeDecodeError):
            pass
        return code

    def _analyze_codebase(self):
        """Analyze the codebase to identify key features and metrics."""
        features = {
            "imports": set(),
            "classes": {},
            "functions": {},
            "files": {},
            "metrics": {
                "total_lines": 0,
                "code_lines": 0,
                "comment_lines": 0,
                "blank_lines": 0,
                "tabs": 0,
                "strings": 0,
            },
            "languages": {},
            "requirements": set(),
        }

        # Load requirements from file if it exists
        if os.path.exists("ndaversis_requirements.txt"):
            try:
                with open("ndaversis_requirements.txt", "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            features["requirements"].add(line.split("==")[0].split(">=")[0].strip())
            except IOError:
                pass
        method_names = set()
        last_code = ""
        for root, _, files in os.walk("."):
            if any(exclude in root for exclude in [".git", "__pycache__", "tests_ndaversis"]):
                continue
            for file in files:
                filepath = os.path.join(root, file)
                ext = os.path.splitext(file)[1].lower() or "no extension"
                features["languages"][ext] = features["languages"].get(ext, 0) + 1
                
                if file.endswith(".py"):
                    last_code = self._process_python_file(filepath, features, method_names)
                else:
                    # Collect basic line metrics and file info for non-python files
                    features["files"][filepath] = {"docstring": ""}
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            lines = f.readlines()
                            features["metrics"]["total_lines"] += len(lines)
                            for line in lines:
                                if not line.strip():
                                    features["metrics"]["blank_lines"] += 1
                                # Simple comment detection for common languages
                                elif line.strip().startswith(("#", "//", "/*", "'''", '"""')):
                                    features["metrics"]["comment_lines"] += 1
                                else:
                                    features["metrics"]["code_lines"] += 1
                    except (IOError, UnicodeDecodeError):
                        pass

        features["imports"] = sorted(list(features["imports"]))
        return features, last_code

    def _capture_repo_state(self, path="."):
        """Capture the state of all files in the repository."""
        state = {}
        for root, dirs, files in os.walk(path):
            # Exclude specified directories
            if '.git' in dirs:
                dirs.remove('.git')
            if 'tests_ndaversis' in dirs:
                dirs.remove('tests_ndaversis')
            if '__pycache__' in dirs:
                dirs.remove('__pycache__')

            for file in files:
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        state[filepath] = f.read()
                except (IOError, UnicodeDecodeError):
                    pass
        return state

    def _generate_diff(self, old_state: dict, new_state: dict) -> dict:
        """
        Generate a detailed diff between two repository states.
        Returns a dictionary mapping file paths to their change metrics.
        """
        diff_data = {}
        all_files = set(old_state.keys()) | set(new_state.keys())
        for file in sorted(all_files):
            old_c = old_state.get(file, "")
            new_c = new_state.get(file, "")
            if old_c == new_c:
                continue

            metrics = {
                "status": "modified",
                "lines_added": 0, "lines_removed": 0,
                "chars_added": 0, "chars_removed": 0,
                "tabs_added": 0, "tabs_removed": 0,
                "spaces_added": 0, "spaces_removed": 0
            }
            if file not in old_state:
                metrics["status"] = "added"
            elif file not in new_state:
                metrics["status"] = "removed"

            old_lines = old_c.splitlines()
            new_lines = new_c.splitlines()
            
            diff = list(difflib.ndiff(old_lines, new_lines))
            for line in diff:
                if line.startswith("+ "):
                    metrics["lines_added"] += 1
                    content = line[2:]
                    metrics["chars_added"] += len(content)
                    metrics["tabs_added"] += content.count("\t")
                    metrics["spaces_added"] += content.count(" ")
                elif line.startswith("- "):
                    metrics["lines_removed"] += 1
                    content = line[2:]
                    metrics["chars_removed"] += len(content)
                    metrics["tabs_removed"] += content.count("\t")
                    metrics["spaces_removed"] += content.count(" ")
                elif line.startswith("? "):
                    # ndiff highlights within-line changes with ? lines
                    pass

            diff_data[file] = metrics
        return diff_data

    def generate_change_summary(self, old_state: dict, new_state: dict, diff_data: Optional[dict] = None) -> str:
        """Compare two code states and generate a detailed summary of changes."""
        if diff_data is None:
            diff_data = self._generate_diff(old_state, new_state)
        
        if not diff_data:
            return "No significant changes detected."

        summary = "| File | Status | Lines + | Lines - | Chars + | Chars - | Tabs | Spaces |\n"
        summary += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
        for file, metrics in diff_data.items():
            summary += (f"| {file} | {metrics['status']} | {metrics['lines_added']} | "
                        f"{metrics['lines_removed']} | {metrics['chars_added']} | "
                        f"{metrics['chars_removed']} | {metrics['tabs_added']} | "
                        f"{metrics['spaces_added']} |\n")
        summary += "\n"

        # Generate practical impact labels via AI or fallback
        practical_labels = {}
        if self.ai_service:
            prompt = (
                "For each file change listed below, provide a short (max 10 words) human-readable explanation of the practical value or impact of that change. "
                "Focus on what it means for the user or the project (e.g., 'Improves chart readability' or 'Fixes a bug in version tracking'). "
                "Format as a JSON object: {\"filename\": \"description\"}\n\n"
                f"Changes:\n{diff_data}\n"
            )
            try:
                ai_output = self.ai_service.generate_content(prompt, {"diff_data": diff_data})
                # Clean markdown if AI returns it
                ai_output = re.sub(r"```json\s*|\s*```", "", ai_output).strip()
                practical_labels = json.loads(ai_output)
            except:
                practical_labels = {}

        # Universal horizontal diagram for insights with full metrics and dark mode styling
        summary += "\n#### Impact Map\n\n"
        summary += "```mermaid\ngraph LR\n"
        if diff_data:
            summary += "    Root[\"Latest Changes\"] --> " + " & ".join([file.replace(".", "_").replace("/", "_").replace("-", "_").replace(" ", "_").strip("_") for file in diff_data.keys()]) + "\n"
        for file, metrics in diff_data.items():
            # Clean name for Mermaid ID
            clean_id = file.replace(".", "_").replace("/", "_").replace("-", "_").replace(" ", "_").strip("_")
            
            # Label with practical value if available, else metrics
            label = f"{file}: {metrics['status']} ({metrics.get('lines_added', 0)} + / {metrics.get('lines_removed', 0)} -)"
            summary += f"    {clean_id}[\"{label}\"]\n"
        
        # Add dark mode styling for impact map
        summary += "\n%% Dark mode styling\n"
        summary += "classDef rootNode fill:#e74c3c,stroke:#c0392b,stroke-width:3px,color:#fff\n"
        summary += "classDef modifiedNode fill:#3498db,stroke:#2980b9,stroke-width:2px,color:#fff\n"
        summary += "classDef addedNode fill:#2ecc71,stroke:#27ae60,stroke-width:2px,color:#fff\n"
        summary += "classDef deletedNode fill:#95a5a6,stroke:#7f8c8d,stroke-width:2px,color:#fff\n"
        
        summary += "\nclass Root rootNode\n"
        for file, metrics in diff_data.items():
            clean_id = file.replace(".", "_").replace("/", "_").replace("-", "_").replace(" ", "_").strip("_")
            if metrics['status'] == 'modified':
                summary += f"class {clean_id} modifiedNode\n"
            elif metrics['status'] == 'added':
                summary += f"class {clean_id} addedNode\n"
            elif metrics['status'] == 'deleted':
                summary += f"class {clean_id} deletedNode\n"
        
        summary += "```\n"

        # Generate practical impact labels via AI or fallback
        practical_labels = {}
        if self.ai_service:
            prompt = (
                "For each file change listed below, provide a short (max 10 words) human-readable explanation of the practical value or impact of that change. "
                "Focus on what it means for the user or the project (e.g., 'Improves chart readability' or 'Fixes a bug in version tracking'). "
                "Format as a JSON object: {\"filename\": \"description\"}\n\n"
                f"Changes:\n{diff_data}\n"
            )
            try:
                ai_output = self.ai_service.generate_content(prompt, {"diff_data": diff_data})
                # Clean markdown if AI returns it
                ai_output = re.sub(r"```json\s*|\s*```", "", ai_output).strip()
                practical_labels = json.loads(ai_output)
            except:
                practical_labels = {}

        return summary

    def _generate_use_cases_prompt(self) -> str:
        """
        Generates a prompt for creating comprehensive Use Cases.

        Returns:
            str: The prompt for the AI service.
        """
        return (
            "As a Senior Business Analyst, create a set of comprehensive Use Cases "
            "based on the provided codebase analysis. For each Use Case, "
            "provide a clear title, a detailed description of the user's goal, "
            "the primary actor, and the sequence of events. Ensure the Use Cases "
            "cover all key functionalities of the application."
        )

    def _generate_user_stories_prompt(self) -> str:
        """
        Generates a prompt for creating comprehensive User Stories.

        Returns:
            str: The prompt for the AI service.
        """
        return (
            "As a Senior Product Manager, create a set of comprehensive User Stories "
            "based on the provided codebase analysis. Each User Story should "
            "follow the format: 'As a [user type], I want [an action] so that "
            "[a benefit].' Ensure the User Stories are detailed, actionable, and "
            "cover all key user interactions with the application."
        )

    def _generate_repo_synthesis_prompt(self) -> str:
        """
        Generates a prompt for synthesizing the repository's main goal and tasks.

        Returns:
            str: The prompt for the AI service.
        """
        return (
            "Based on the provided codebase analysis, synthesize the following:\n"
            "1. Main Goal: A one-sentence description of the primary purpose of this repository.\n"
            "2. Core Tasks: A list of the main technical tasks or functions this repository performs.\n"
            "Return the result in a clear, concise format."
        )

    def _generate_version_bump_prompt(self, change_summary: str) -> str:
        """
        Generates a prompt for suggesting a version bump based on changes.

        Args:
            change_summary (str): A summary of the changes made.

        Returns:
            str: The prompt for the AI service.
        """
        return (
            f"Based on the following change summary, suggest the most appropriate "
            f"semantic version bump (major, minor, or patch):\n\n"
            f"{change_summary}\n\n"
            f"Reply with ONLY the word 'major', 'minor', or 'patch'."
        )

    def generate_use_case_diagram(self, analysis_data: dict) -> str:
        """
        Generates a UML Use Case diagram in Mermaid syntax.

        Args:
            analysis_data (dict): The code analysis data.

        Returns:
            str: The Mermaid syntax for the Use Case diagram.
        """
        if self.ai_service:
            prompt = (
                "Generate a UML Use Case diagram in Mermaid syntax based on the "
                "provided codebase analysis. The diagram should include actors "
                "and use cases that represent the key functionalities of the "
                "application."
            )
            return self.ai_service.generate_content(prompt, analysis_data)
        return ""

    def generate_bpmn_diagram(self, analysis_data: dict) -> str:
        """
        Generates a BPMN diagram in Mermaid syntax.

        Args:
            analysis_data (dict): The code analysis data.

        Returns:
            str: The Mermaid syntax for the BPMN diagram.
        """
        if self.ai_service:
            prompt = (
                "Generate a BPMN diagram in Mermaid syntax based on the "
                "provided codebase analysis. The diagram should illustrate the "
                "key business processes and workflows of the application."
            )
            return self.ai_service.generate_content(prompt, analysis_data)
        return ""

    def _generate_section(self, title, analysis_data, prefix, format_str):
        """Helper function to generate a section of the README."""
        content = f"## {title}\n\n"
        items = []
        for func_name, func_data in analysis_data["functions"].items():
            if func_data.get("docstring") and prefix in func_data["docstring"]:
                items.append(
                    format_str.format(
                        name=func_name.replace("_", " ").title(),
                        doc=func_data["docstring"].split(prefix)[1].strip(),
                    )
                )
        content += "".join(items)
        return content

    def generate_dynamic_sections(self, analysis_data):
        """Generate the dynamic sections of the README file."""
        # --- Use Cases ---
        use_cases = "## 3. Use Cases\n\n"
        if self.ai_service:
            content = self.ai_service.generate_content(self._generate_use_cases_prompt(), analysis_data)
            use_cases += re.sub(r"^#+ (3\.)? ?Use Cases\n*", "", content, flags=re.MULTILINE).strip()
            use_cases += "\n\n### Use Case Diagram\n\n"
            use_cases += f"```mermaid\n{self.generate_use_case_diagram(analysis_data)}\n```\n"
        else:
            items = self._generate_section("3. Use Cases", analysis_data, "Use Case:", "*   **{name}**: {doc}\n")
            content_items = items.replace("## 3. Use Cases\n\n", "").strip()
            if not content_items:
                # Professional developer-centric use cases
                use_cases += (
                    "*   **Automated Release Cycles**: Integrate version bumping into CI/CD pipelines for touchless releases.\n"
                    "*   **Dynamic Documentation Sync**: Ensure the repository's 'front window' (README) always matches the latest architectural changes.\n"
                    "*   **Offline Repository Health**: Audit codebase metrics and structure without needing external tool connectivity.\n"
                    "*   **Standardized Semantic Versioning**: Enforce consistent versioning across monolithic or microservice projects automatically.\n"
                )
            else:
                use_cases += content_items + "\n"

        # --- User Stories ---
        user_stories = "## 4. User Stories\n\n"
        if self.ai_service:
            content = self.ai_service.generate_content(self._generate_user_stories_prompt(), analysis_data)
            user_stories += re.sub(r"^#+ (4\.)? ?User Stories\n*", "", content, flags=re.MULTILINE).strip()
            user_stories += "\n\n### BPMN Diagram\n\n"
            user_stories += f"```mermaid\n{self.generate_bpmn_diagram(analysis_data)}\n```\n"
        else:
            items = self._generate_section("4. User Stories", analysis_data, "User Story:", "*   **As a {role},** I want to {action}, so that {benefit}.\n")
            content_items = items.replace("## 4. User Stories\n\n", "").strip()
            if not content_items:
                # Expert-level technical user stories
                user_stories += (
                    "*   **DevOps Engineer**: As a DevOps engineer, I want documentation to refresh on every commit, so that the team always sees the current state without manual edits.\n"
                    "*   **Open Source Maintainer**: As a maintainer, I want semantic versioning to be calculated from code changes, so that I can avoid human error during release tags.\n"
                    "*   **Full-Stack Developer**: As a developer, I want a visual map of my project structure, so that I can quickly onboard new contributors or navigate complex repos.\n"
                    "*   **Project Lead**: As a lead, I want to track code metrics like comments vs code ratios, so that I can maintain high quality and documentation standards.\n"
                )
            else:
                user_stories += content_items + "\n"

        # --- FAQ ---
        faq = "## 5. FAQ\n\n"
        faq_items = self._generate_section("5. FAQ", analysis_data, "FAQ:", "**Q: {name}?**\n**A:** {doc}\n\n").replace("## 5. FAQ\n\n", "").strip()
        if not faq_items:
            faq += (
                "*   **Q: Will this work without an internet connection?**\n"
                "    **A:** Yes, the core analysis and documentation logic works entirely offline.\n"
                "*   **Q: Does it actually update my code's version?**\n"
                "    **A:** Absolutely. It scans and updates your version strings automatically based on your changes.\n"
                "*   **Q: Is it really 'set and forget'?**\n"
                "    **A:** That's the goal. Integrate it once (e.g., via pre-commit hook), and let it handle the rest.\n"
            )
        else:
            faq += faq_items + "\n"
            
        # --- How To ---
        how_to = self._generate_section("6. How To", analysis_data, "How To:", "### {name}\n\n{doc}\n\n")
        if how_to.strip() == "## 6. How To":
            how_to += (
                "### 🚀 Quick Patch Update\n"
                "To quickly update your project's version and README after a minor change:\n"
                "```bash\npython ndaversis.py cli --patch\n```\n\n"
                "### 🎨 Using the Graphical Interface\n"
                "If you prefer a visual tool, simply run the script without arguments:\n"
                "```bash\npython ndaversis.py\n```\n\n"
                "### 🔗 Git Pre-Commit Integration\n"
                "For a true 'set and forget' experience, integrate it into your Git workflow. "
                "This ensures the README and version are updated every time you commit:\n"
                "```bash\npython ndaversis.py install-hook\n```\n\n"
                "### 🔍 Detailed Repository Audit\n"
                "To see a full analysis of your code metrics and project structure without updating anything:\n"
                "```bash\npython ndaversis.py audit\n```\n\n"
                "### 📦 Install\n"
                "#### 1. Clone and Prepare Environment\n"
                "```bash\ngit clone https://github.com/lystwork/ndaversis.git\ncd ndaversis\ncp .env.example .env   # see below for what to fill\n```\n\n"
                "#### 2. Configure Variables\n"
                "Substitute your own API key (at least one required). Example:\n"
                "```json\n{\n  \"GEMINI_API_KEY\": \"your-key-here\",\n  \"OPENAI_API_KEY\": \"your-key-here\"\n}\n```\n\n"
                "#### 3. Launch Entire Infrastructure\n"
                "```bash\npython ndaversis.py\n```\n\n"
                "The ndaversis starts polling and is ready with any free port.\n"
                "Web available at http://localhost:8080\n\n"
                "### ✅ How to Verify\n"
                "After installation, verify everything is working:\n"
                "```bash\n# Check health and configuration\npython ndaversis.py health\n\n# Run a full audit to test analysis\npython ndaversis.py audit\n\n# Test GUI functionality\npython ndaversis.py\n```\n\n"
                "### 🧪 How to Test\n"
                "Run the test suite to verify functionality:\n"
                "```bash\n# Run all tests\npython -m pytest tests_ndaversis/ -v\n\n# Run specific test file\npython -m pytest tests_ndaversis/test_ndaversis.py -v\n\n# Run with coverage\npython -m pytest tests_ndaversis/ --cov=. --cov-report=html\n```\n"
            )

        # --- Features ---
        features_str = "## 7. Features\n\n"
        # Prepend the main value proposition
        features_str += "*   **Set-and-Forget Automation**: Automatically keeps your project documentation and versioning in sync with your code, saving you manual effort on every update.\n"
        
        # Mapping technical specific functions to human-friendly descriptions
        human_features_map = {
            "generate_content": "AI-Powered Documentation: Automatically drafts FAQs, User Stories, and Use Cases by analyzing your code structure with AI, ensuring your README is professional even if you haven't written a word.",
            "increment_patch": "Intelligent Version Management: Handles semantic versioning (Major.Minor.Patch) automatically, calculating the right bump based on your actual code changes.",
            "analyze_repository": "Comprehensive Project Analysis: Gains a birds-eye view of your codebase with automatic calculation of line counts, language distribution, and complexity metrics.",
            "install_pre_commit_hook": "Set-and-Forget Workflow: One-time integration into your Git workflow that triggers documentation and version updates automatically before every commit.",
            "main_gui": "User-Friendly Interface: Provides a sleek graphical window for managing your project updates, making it accessible even for those who avoid the terminal.",
            "generate_readme_content": "Instant README Refresh: Keeps your entire project front-page up-to-date with structural maps, dependency graphs, and latest feature lists in one click.",
            "generate_bpmn_diagram": "Visual Logic Maps: Automatically generates process diagrams (BPMN) in Mermaid syntax to show how your code's logic flows visually.",
            "generate_use_case_diagram": "Automatic Architecture Charts: Creates UML Use Case diagrams to visually communicate project goals and user interactions to stakeholders.",
            "health_check": "Project Integrity Check: Automatically verifies your environment and configuration to ensure everything is set up for flawless automation.",
        }

        # Features to EXCLUDE from the main human-readable list (too technical or redundant)
        technical_blacklist = [
            "increment_major", "increment_minor", "get_version", "save_version", 
            "load_ai_config", "get_ai_service", "load_previous_code_state", 
            "generate_change_summary", "generate_dynamic_sections", 
            "generate_project_description", "generate_project_map",
            "update_changelog", "generate_user_benefit_analysis",
            "infer_goals_from_summary", "suggest_next_steps", "update_readme",
            "main_cli", "_process_python_file", "_analyze_codebase"
        ]

        features_items = []
        
        # Collect from top-level functions
        for func_name, func_data in analysis_data["functions"].items():
            if func_name.startswith("_") or func_name in technical_blacklist:
                continue
            
            # Use human mapping if available
            if func_name in human_features_map:
                features_items.append(f"*   **{human_features_map[func_name].split(': ')[0].strip()}**: {human_features_map[func_name].split(': ')[1].strip()}\n")
                continue

            docstring = func_data.get("docstring", "")
            if docstring:
                first_line = docstring.splitlines()[0].strip()
                desc = first_line.split(": ", 1)[1] if ": " in first_line else first_line
                if desc:
                    features_items.append(f"*   **{func_name.replace('_', ' ').title()}**: {desc}\n")

        # Collect from class methods
        for class_name, class_data in analysis_data.get("classes", {}).items():
            if class_name.startswith("_"):
                continue
            for method_name, method_data in class_data.get("methods", {}).items():
                if method_name.startswith("_") or method_name in ["__init__", "__str__"] or method_name in technical_blacklist:
                    continue
                
                # Use human mapping if available
                if method_name in human_features_map:
                    # Avoid duplicates if multiple classes share common method names (unlikely to be a problem here)
                    feat_text = f"*   **{human_features_map[method_name].split(': ')[0].strip()}**: {human_features_map[method_name].split(': ')[1].strip()}\n"
                    if feat_text not in features_items:
                        features_items.append(feat_text)
                    continue

                docstring = method_data.get("docstring", "")
                if docstring:
                    first_line = docstring.splitlines()[0].strip()
                    desc = first_line.split(": ", 1)[1] if ": " in first_line else first_line
                    if desc:
                        features_items.append(f"*   **{method_name.replace('_', ' ').title()}**: {desc}\n")
        
        if not features_items:
            # Fallback if no docstrings found
            items_to_use = list(analysis_data.get("functions", {}).keys()) + [m for c in analysis_data.get("classes", {}).values() for m in c.get("methods", {}).keys()]
            if items_to_use:
                features_items = [f"*   **{item.replace('_', ' ').title()}**: Specialized functional component that contributes to the project's automation goals.\n" for item in items_to_use if not item.startswith("_")][:10]
            else:
                features_items = ["*   **Automated Analysis**: Scans and parses the codebase for insights.\n", "*   **Dynamic Documentation**: Generates README content based on project state.\n"]
        
        # Ensure we don't overwhelm with too many features, pick the best ones
        features_str += "".join(features_items[:15])

        # --- Requirements ---
        requirements = "## 8. Requirements\n\n"
        stdlib_modules = set(sys.stdlib_module_names) | {"typing", "pkg_resources", "argparse", "datetime", "json", "os", "re", "sys", "ast", "getpass", "difflib", "time"}
        
        detected_imports = set(analysis_data.get("imports", []))
        external_deps = (analysis_data.get("requirements", set()) | {d for d in detected_imports if d not in stdlib_modules})
        stdlib_deps = {d for d in detected_imports if d in stdlib_modules}
        
        # Languages used
        languages = analysis_data.get("languages", {})
        if languages:
            requirements += "### Languages & Environments\n\n"
            
            # Show Python version requirement prominently if Python files detected
            if ".py" in languages:
                requirements += "**Python Version**: 3.8 or higher required\n\n"
            
            # Mermaid pie chart for language distribution with dark mode styling
            requirements += "```mermaid\npie title Language Distribution\n"
            for ext, count in sorted(languages.items(), key=lambda x: x[1], reverse=True):
                requirements += f"    \"{ext}\" : {count}\n"
            requirements += "```\n\n"

        if stdlib_deps:
            requirements += "### Built-in Standard Library (Included with Python)\n"
            requirements += "```mermaid\ngraph LR\n"
            requirements += "    Python --> " + " & ".join([d for d in sorted(stdlib_deps)]) + "\n"
            requirements += "\n%% Dark mode styling\n"
            requirements += "classDef pythonNode fill:#3776ab,stroke:#4b8bbe,stroke-width:2px,color:#fff\n"
            requirements += "class Python pythonNode\n"
            for d in sorted(stdlib_deps):
                requirements += f"class {d.replace('-', '_').replace('.', '_')} pythonNode\n"
            requirements += "```\n\n"
            requirements += "The following modules are part of Python's standard library and **do not** require external installation:\n\n"
            requirements += ", ".join([f"`{d}`" for d in sorted(stdlib_deps)]) + "\n\n"

        if external_deps:
            requirements += "### External Libraries\n\n"
            
            mandatory = ["flet"]
            ai_providers = ["openai", "google-genai", "anthropic", "deepseek"]
            optional_deps = [d for d in external_deps if d.lower() not in mandatory and d.lower() not in ai_providers]
            
            # Mandatory dependencies
            mandatory_found = [d for d in external_deps if d.lower() in mandatory]
            if mandatory_found:
                requirements += "#### Mandatory (Required for correct work)\n"
                for dep in sorted(mandatory_found):
                    requirements += f"*   `{dep}` - Required for GUI functionality\n"
                requirements += "\n"
            
            # Optional AI dependencies
            ai_found = [d for d in external_deps if d.lower() in ai_providers]
            if ai_found:
                requirements += "#### Optional - AI Providers (Could be used without)\n"
                requirements += "> [!NOTE]\n"
                requirements += "> The system works in **local on-prem mode** without any AI dependencies. "
                requirements += "AI providers enhance documentation with intelligent summaries but are not required for core functionality.\n\n"
                for dep in sorted(ai_found):
                    requirements += f"*   `{dep}` - For AI-powered documentation insights\n"
                requirements += "\n"
            
            # Other technical dependencies
            if optional_deps:
                requirements += "#### Other Dependencies\n"
                for dep in sorted(optional_deps):
                    requirements += f"*   `{dep}` - Technical dependency\n"
                requirements += "\n"
        
        requirements += "### Services & APIs (Optional)\n"
        requirements += "*   **Vertex AI / Google Gemini**: For AI-powered documentation (Recommended).\n"
        requirements += "*   **OpenAI / Anthropic / DeepSeek**: Supported providers for advanced synthesis.\n"
        requirements += "*   **Local/On-Prem**: Works entirely offline for core analysis and versioning.\n\n"

        # --- Install ---
        install = "## 9. Install\n\n"
        install += "Setting up **NDAVERSIS** is straightforward. You can use it in a fresh environment or join it with an existing project.\n\n"
        
        install += "### Step 1: Install Python\n"
        install += "Ensure you have Python 3.8 or newer. Download it from [python.org](https://www.python.org/downloads/).\n\n"
        
        install += "### Step 2: Clone & Setup\n"
        install += "Clone this repository and install the framework dependencies:\n"
        install += "```bash\npip install -r ndaversis_requirements.txt\n```\n\n"
        
        install += "### Step 3: Join with Your Project 🚀\n"
        install += "To use Ndaversis with your own code, follow these steps:\n"
        install += "1.  **Copy**: Copy `ndaversis.py` and `ndaversis_requirements.txt` into your project's root folder.\n"
        install += "2.  **Initialize**: Run `python ndaversis.py` once to create the initial state.\n"
        install += "3.  **Integrate**: (Optional) Run `python ndaversis.py install-hook` to automate everything via Git.\n\n"
        
        install += "### Step 4: (Optional) Set up AI API Keys 🔑\n"
        install += "To unlock automated summaries and stories, you can add API keys to `config.json`. Here is how:\n\n"
        install += "*   **Google Gemini (Recommended)**: Go to [Google AI Studio](https://aistudio.google.com/), click 'Get API Key'. It usually has a generous FREE tier for individual developers.\n"
        install += "*   **OpenAI (ChatGPT)**: Go to the [OpenAI Platform](https://platform.openai.com/api-keys) to create a key. This is a paid service (pay-as-you-go).\n"
        install += "*   **Anthropic (Claude)**: Visit the [Anthropic Console](https://console.anthropic.com/) to get your key.\n\n"
        install += "**How to use them**: Open `config.json` in this folder and paste your keys like this:\n"
        install += "```json\n{\n  \"GEMINI_API_KEY\": \"your-key-here\",\n  \"OPENAI_API_KEY\": \"your-key-here\"\n}\n```\n"
        install += "If you leave them blank, the tool will still work perfectly using its built-in 'smart' logic!\n\n"
        
        install += "### Step 5: Run\n"
        install += "Start the GUI or CLI to maintain your project:\n"
        install += "```bash\npython ndaversis.py\n```\n"

        # --- Modules Map ---
        modules_map = "## 11. Modules Map\n\n"
        
        # Enhanced descriptions for all modules
        for filepath, data in sorted(analysis_data.get("files", {}).items()):
            basename = os.path.basename(filepath)
            doc = data.get("docstring", "").split("\n")[0].strip()
            
            if not doc:
                # Provide specific descriptions based on file type and name
                if basename.endswith(".py"):
                    # Check if file contains classes or functions
                    file_classes = [c for c, c_data in analysis_data.get("classes", {}).items()]
                    file_functions = list(analysis_data.get("functions", {}).keys())
                    
                    if file_classes:
                        doc = f"Python module implementing {', '.join(file_classes[:3])} {'and more' if len(file_classes) > 3 else ''}"
                    elif file_functions:
                        doc = f"Python module with {len(file_functions)} function(s) for core logic"
                    else:
                        doc = "Python module containing core system logic and definitions"
                elif basename.endswith(".json"):
                    doc = f"Configuration file: {basename}"
                elif basename.endswith(".md"):
                    doc = f"Documentation file: {basename}"
                elif basename.endswith(".txt"):
                    doc = f"Text resource file: {basename}"
                elif basename == ".gitignore":
                    doc = "Git ignore rules for version control"
                elif basename == "LICENSE":
                    doc = "Project license and terms"
                else:
                    doc = f"Project resource file: {basename}"
            
            modules_map += f"*   **{basename}**: {doc}\n"
        modules_map += "\n\n### Module Structure Diagram\n\n```mermaid\nclassDiagram\n"
        if not analysis_data.get("classes"):
            modules_map += "    class MainModule {\n        +main()\n    }\n"
        else:
            for class_name, class_data in analysis_data.get("classes", {}).items():
                modules_map += f"    class {class_name} {{\n"
                for method in class_data.get("methods", {}).keys():
                    modules_map += f"        +{method}()\n"
                modules_map += "    }\n"
        modules_map += "```\n"

        # --- Dependencies Map ---
        dependencies_map = "## 12. Dependencies Map\n\n"
        
        # Re-calc lists for descriptions
        all_external = (analysis_data.get("requirements", set()) | {d for d in detected_imports if d not in stdlib_modules})
        all_built_in = {d for d in detected_imports if d in stdlib_modules}
        all_deps = all_external | all_built_in

        if not all_external and not all_built_in:
            dependencies_map += "*   No external or built-in dependencies detected.\n"
        else:
            if all_external:
                dependencies_map += "### Custom/External Frameworks\n\n"
                dep_descriptions = {
                    "flet": "Modern framework for building beautiful and fast interactive user interfaces.",
                    "google-genai": "Google's official library for accessing high-performance Gemini AI models.",
                    "openai": "Standard interface for integrating ChatGPT and other OpenAI language models.",
                    "anthropic": "Client for Claude, a highly reliable and safe institutional-grade AI.",
                    "deepseek": "Advanced AI provider known for efficient and accurate content generation.",
                    "requests": "Simplifies sending HTTP requests to interact with external APIs.",
                    "pytest": "Industry-standard testing framework for ensuring codebase reliability.",
                }
                for dep in sorted(all_external):
                    desc = dep_descriptions.get(dep.lower(), "Specialized library that supports the system's core automation logic.")
                    dependencies_map += f"*   **{dep}** (pip): {desc}\n"
                dependencies_map += "\n"

            if all_built_in:
                dependencies_map += "### Python Standard Library (Built-in)\n\n"
                dependencies_map += "These modules are built into Python (no installation required):\n\n"
                dependencies_map += ", ".join([f"`{d}`" for d in sorted(all_built_in)]) + "\n"
        
        dependencies_map += "\n\n### Library Dependency Diagram\n\n```mermaid\ngraph TD\n"
        project_node = "Project"
        if not all_deps:
            dependencies_map += f"    {project_node} --> StdLib[Standard Library]\n"
        else:
            # Group by language if multiple languages exist
            languages = analysis_data.get("languages", {})
            if len(languages) > 1:
                for lang_ext, count in languages.items():
                    lang_name = lang_ext.replace(".", "").upper() or "OTHER"
                    # Sanitize language ID for Mermaid
                    lang_id = f"lang_{lang_name.replace(' ', '_').replace('-', '_')}"
                    dependencies_map += f"    {project_node} --> {lang_id}[\"{lang_name} Overview ({count} files)\"]\n"
                    
                    # For Python projects, link all detected libraries to the Python node
                    if lang_ext == ".py":
                        for dep in sorted(all_deps):
                            # Sanitize library ID for Mermaid
                            node_id = f"dep_{dep.replace('-', '_').replace('.', '_')}"
                            dependencies_map += f"    {lang_id} --> {node_id}[\"{dep}\"]\n"
            else:
                for dep in sorted(all_deps):
                    node_id = f"dep_{dep.replace('-', '_').replace('.', '_')}"
                    dependencies_map += f"    {project_node} --> {node_id}[\"{dep}\"]\n"
        
        # Add dark mode styling for dependency diagram
        dependencies_map += "\n%% Dark mode styling\n"
        dependencies_map += "classDef projectNode fill:#1a1a2e,stroke:#eee,stroke-width:3px,color:#fff\n"
        dependencies_map += "classDef langNode fill:#0f3460,stroke:#4fbdba,stroke-width:2px,color:#fff\n"
        dependencies_map += "classDef depNode fill:#16213e,stroke:#e0913f,stroke-width:2px,color:#fff\n"
        dependencies_map += "classDef stdLibNode fill:#2d033b,stroke:#4caf50,stroke-width:2px,color:#fff\n"
        
        dependencies_map += f"\nclass {project_node.replace('-', '_')} projectNode\n"
        
        if not all_deps:
            dependencies_map += "class StdLib stdLibNode\n"
        else:
            if len(languages) > 1:
                for lang_ext, count in languages.items():
                    lang_name = lang_ext.replace(".", "").upper() or "OTHER"
                    lang_id = f"lang_{lang_name.replace(' ', '_').replace('-', '_')}"
                    dependencies_map += f"class {lang_id} langNode\n"
                    
                    if lang_ext == ".py":
                        for dep in sorted(all_deps):
                            node_id = f"dep_{dep.replace('-', '_').replace('.', '_')}"
                            dependencies_map += f"class {node_id} depNode\n"
            else:
                for dep in sorted(all_deps):
                    node_id = f"dep_{dep.replace('-', '_').replace('.', '_')}"
                    dependencies_map += f"class {node_id} depNode\n"
        
        dependencies_map += "```"

        return "\n".join(filter(None, [use_cases, user_stories, faq, how_to, features_str, requirements, install, modules_map, dependencies_map]))

    def generate_project_description(self):
        """Analyze the repository to generate a project description."""
        features, code = self._analyze_codebase()
        if self.ai_service:
            prompt = (
                "Generate a human-readable project description for a README.md file. "
                "Emphasize the 'set-and-forget' paradigm: automatically creating an "
                "actual README with semantic versioning inside the code project so "
                "the user never has to change it manually when the project changes. "
                "The description should be useful for a human developer, not just a technical summary."
            )
            return self.ai_service.generate_content(prompt, (features, code))
        
        try:
            with open(README_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                match = re.search(r"# 1\. ([^:\n]+)", content)
                if match:
                    project_name = match.group(1).strip()
                else:
                    project_name = "NDAVERSIS"
        except (IOError, IndexError, FileNotFoundError):
            project_name = "NDAVERSIS"
            
        total_methods = sum(len(c.get("methods", {})) for c in features["classes"].values())
        total_funcs = len(features["functions"])
        total_components = total_methods + total_funcs
        
        return (
            f"**{project_name}** is designed with a simple goal: to let you **'set and forget'** "
            f"your documentation and versioning. It automatically generates and maintains an "
            f"accurate README.md and manages semantic versioning directly within your code, "
            f"ensuring your project info is always up-to-date even as you change the code. "
            f"Whether you have an internet connection or not, it works locally to keep your "
            f"repository professional and informative with zero manual effort."
        )

    def generate_project_map(self):
        """Generate a markdown tree of the project structure with a Mermaid diagram."""
        project_map = "```\n"
        files_list = []
        for root, dirs, files in os.walk("."):
            if ".git" in root or "__pycache__" in root or "tests_ndaversis" in root:
                continue
            for file in sorted(files):
                filepath = os.path.join(root, file)
                display_path = filepath if filepath.startswith("./") else f"./{filepath.lstrip('./')}"
                project_map += f"{display_path}\n"
                files_list.append(display_path)
        project_map += "```\n\n### Project Structure Diagram\n\n"
        
        # Add Mermaid Project Diagram with dark-mode-friendly styling
        project_map += "```mermaid\ngraph TD\n"
        project_map += "    Root[./]\n"
        for f in files_list:
            if "/" in f.lstrip("./"):
                parts = f.lstrip("./").split("/")
                current = "Root"
                for i, part in enumerate(parts):
                    node_id = f"node_{'_'.join(parts[:i+1]).replace('.', '_')}"
                    project_map += f"    {current} --> {node_id}[\"{part}\"]\n"
                    current = node_id
            else:
                node_id = f"node_{f.lstrip('./').replace('.', '_')}"
                project_map += f"    Root --> {node_id}[\"{f.lstrip('./')}\"]\n"
        
        # Add dark-mode-friendly styling
        project_map += "\n%% Dark mode styling\n"
        project_map += "classDef rootNode fill:#1a1a2e,stroke:#eee,stroke-width:2px,color:#fff\n"
        project_map += "classDef fileNode fill:#16213e,stroke:#ddd,stroke-width:1px,color:#fff\n"
        project_map += "classDef pythonFile fill:#0f3460,stroke:#4fbdba,stroke-width:2px,color:#fff\n"
        project_map += "classDef configFile fill:#2d033b,stroke:#e0913f,stroke-width:2px,color:#fff\n"
        project_map += "classDef docFile fill:#1e5128,stroke:#4caf50,stroke-width:2px,color:#fff\n"
        
        project_map += "\n%% Apply styles\n"
        project_map += "class Root rootNode\n"
        
        for f in files_list:
            node_id = f"node_{f.lstrip('./').replace('.', '_').replace('/', '_')}"
            ext = f.split('.')[-1] if '.' in f else 'no_ext'
            if ext == 'py':
                project_map += f"class {node_id} pythonFile\n"
            elif ext in ['json', 'yml', 'yaml', 'toml', 'ini']:
                project_map += f"class {node_id} configFile\n"
            elif ext in ['md', 'txt', 'rst']:
                project_map += f"class {node_id} docFile\n"
            else:
                project_map += f"class {node_id} fileNode\n"
        
        project_map += "```"
        return project_map

    def analyze_repository(self):
        """Analyze the repository to generate a summary."""
        features, code = self._analyze_codebase()
        metrics = features["metrics"]
        
        # Language breakdown table
        lang_table = "| Extension | Count |\n| :--- | :--- |\n"
        for ext, count in sorted(features["languages"].items(), key=lambda x: x[1], reverse=True):
            lang_table += f"| {ext} | {count} |\n"
            
        # Metrics table
        metrics_table = (
            "| Metric | Value |\n"
            "| :--- | :--- |\n"
            f"| Total Lines | {metrics['total_lines']} |\n"
            f"| Code Lines | {metrics['code_lines']} |\n"
            f"| Comment Lines | {metrics['comment_lines']} |\n"
            f"| Blank Lines | {metrics['blank_lines']} |\n"
            f"| Tabs | {metrics['tabs']} |\n"
            f"| Strings | {metrics['strings']} |\n"
        )

        synthesis = ""
        if self.ai_service:
            synthesis = self.ai_service.generate_content(
                self._generate_repo_synthesis_prompt(), (features, code)
            )

        # Calculate repository size
        total_size = 0
        for root, dirs, files in os.walk("."):
            if ".git" in root or "__pycache__" in root or "tests_ndaversis" in root:
                continue
            for f in files:
                fp = os.path.join(root, f)
                if os.path.isfile(fp):
                    total_size += os.path.getsize(fp)
        
        size_str = f"{total_size / 1024:.2f} KB"
        if total_size > 1024 * 1024:
            size_str = f"{total_size / (1024 * 1024):.2f} MB"
        if total_size > 1024 * 1024 * 1024:
            size_str = f"{total_size / (1024 * 1024 * 1024):.2f} GB"

        summary = (
            f"\n\n"
            f"----- \n"
            f"*This summary is auto-generated and reflects the state of the repository at "
            f"the time of the last version update.*\n\n"
            f"### Repository Metrics\n\n{metrics_table}\n\n"
            f"### Language Breakdown\n\n{lang_table}\n\n"
            f"### File Statistics\n"
            f"- **Total Files:** {sum(features['languages'].values())}\n"
            f"- **Python Files:** {features['languages'].get('.py', 0)}\n"
            f"- **Repository Size:** {size_str}\n"
        )
        if synthesis:
            summary += f"\n**Goal & Tasks synthesis:**\n{synthesis}\n"
        summary += f"----- \n"
        return summary

    def suggest_version_bump(self, change_summary):
        """Suggest a version bump based on the change summary."""
        if not self.ai_service or not change_summary:
            return "patch"
        suggestion = self.ai_service.generate_content(
            self._generate_version_bump_prompt(change_summary), {}
        ).strip().lower()
        if suggestion in ["major", "minor", "patch"]:
            return suggestion
        return "patch"

    def update_changelog(self, version, change_summary):
        """Update the ndaversis_logs.py file with the new entry."""
        author = getpass.getuser()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        new_entry = {
            "version": str(version),
            "timestamp": timestamp,
            "author": author,
            "summary": change_summary
        }
        
        logs = []
        if os.path.exists(LOGS_FILE):
            try:
                with open(LOGS_FILE, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Basic extraction of the LOGS list
                    match = re.search(r"LOGS = (\[.*\])", content, re.DOTALL)
                    if match:
                        logs = eval(match.group(1))
            except Exception as e:
                print(f"Error reading logs: {e}")
        
        logs.insert(0, new_entry)
        
        with open(LOGS_FILE, "w", encoding="utf-8") as f:
            f.write(f'# Ndaversis Change Logs\n\nLOGS = [\n')
            for entry in logs:
                f.write(f'    {json.dumps(entry, ensure_ascii=False)},\n')
            f.write(f']\n')

    def _create_description_summary(self):
        """Creates the description summary section of the README."""
        project_name = "NDAVERSIS: Agentic Semantic Version Info System"
        content = f"# 1. {project_name}\n\n"
        content += f"**Current Version:** `{self.version}`\n\n"
        content += "## 2. Description Summary\n\n"
        content += "<!-- AUTO-DESCRIPTION-START -->\n"
        content += f"{self.generate_project_description()}\n"
        content += "<!-- AUTO-DESCRIPTION-END -->\n\n"
        return content

    def generate_user_benefit_analysis(self, analysis_data, change_summary=""):
        """Generate the 7-step analysis for the 'What's Good for the User' section."""
        if self.ai_service:
            prompt = (
                "Identify the specific technical changes in the provided metrics and explain their value to a user. "
                "Avoid generic descriptions like 'Improved stability' or 'Refined documentation'. "
                "Instead, be context-aware and mention what actually changed (e.g., 'Enhanced visual representation in diagrams' or 'Streamlined version tracking logic').\n\n"
                "CRITICAL: \n"
                "1. Each description MUST be unique and specifically tailored to the added/modified files.\n"
                "2. Keep 'What's New' and 'Why Upgrade' distinct.\n"
                "3. Focus on the tangible impact of these specific modifications.\n"
                "4. Avoid generic templates.\n"
                "5. Merge the evaluative 'Assessment' directly into 'Why Upgrade'.\n\n"
                "Format the output as follows:\n\n"
                "### 💎 What's New?\n"
                "[Specific, unique description of the new features or technical fixes]\n\n"
                "### 🚀 Why Upgrade?\n"
                "[Persuasive, context-aware explanation of the benefits of this specific version]\n"
            )
            return self.ai_service.generate_content(prompt, analysis_data)
        
        # Fallback logic with more dynamic descriptions based on change summary
        added_files = [f for f, m in analysis_data.get("diff_data", {}).items() if m['status'] == 'added']
        modified_files = [f for f, m in analysis_data.get("diff_data", {}).items() if m['status'] == 'modified']
        
        if added_files:
            new_feat = f"Expanded project scope by adding {len(added_files)} new files, including {os.path.basename(added_files[0])}."
            upgrade_v = f"This update introduces significant new components that improve the overall feature set of the repository."
        elif modified_files:
            new_feat = f"Refined the core logic in {os.path.basename(modified_files[0])} to improve performance and reliability."
            upgrade_v = f"Stay current with the latest optimizations and bug fixes in the core automation engine."
        else:
            new_feat = "General system maintenance and repository metadata updates."
            upgrade_v = "Ensures your repository documentation remains in sync with the latest minor adjustments."

        return (
            f"### 💎 What's New?\n{new_feat}\n\n"
            f"### 🚀 Why Upgrade?\n{upgrade_v}\n"
        )

    def infer_goals_from_summary(self, change_summary, analysis_data=None):
        """Infer the goals of the changes from the change summary using AI if available."""
        if self.ai_service and analysis_data:
            prompt = (
                "Based on the following change metrics and summary, generate a concise, unique one-sentence description of the primary goal for this version. "
                "Avoid repeating generic goals. Focus on the actual intent of these specific changes.\n\n"
                f"Changes:\n{change_summary}\n"
            )
            return self.ai_service.generate_content(prompt, analysis_data).strip()

        goals = []
        if "added" in change_summary.lower() or "Added file" in change_summary or "New feature" in change_summary:
            goals.append("expand the project's capabilities with new components")
        if "modified" in change_summary.lower() or "Modified file" in change_summary or "Improved logic" in change_summary:
            goals.append("refine existing features for better performance and reliability")
        if "removed" in change_summary.lower() or "Removed file" in change_summary or "Cleanup" in change_summary:
            goals.append("clean up the codebase and remove obsolete parts")
        if not goals:
            return "Address minor updates and keep the repository information current."
        return f"The main goals were to {', '.join(goals)}."

    def suggest_next_steps(self, analysis_data, previous_history=""):
        """Suggest next steps for the project, ensuring they are unique and fresh."""
        if self.ai_service:
            prompt = (
                "Based on the current state of the codebase, suggest 3 unique, actionable, and non-repeating "
                "next steps for the project. Be creative and focus on long-term value, maintainability, or "
                "user experience enhancements.\n\n"
                "CRITICAL: Avoid repeating any of the following previous suggestions:\n"
                f"{previous_history}\n\n"
                "Ensure the new suggestions are fresh and context-aware."
            )
            return self.ai_service.generate_content(prompt, analysis_data)

        # Fallback logic with a pool of suggestions to rotate
        suggestion_pool = [
            "improve robustness by adding a dedicated test suite",
            "consider modularizing the code to keep it maintainable as it grows",
            "add comprehensive error handling and logging",
            "implement a plugin system for extended functionality",
            "enhance the user interface for better accessibility",
            "optimize performance for large-scale repositories",
            "add support for more configuration formats (YAML, TOML)",
            "integrate with more AI providers for diversity",
            "create detailed API documentation for other developers",
            "implement automated benchmarking for core logic"
        ]
        
        # Filter out suggestions already in history
        available = [s for s in suggestion_pool if s.lower() not in previous_history.lower()]
        if not available:
            available = suggestion_pool # Reset if all used

        import random
        selected = random.sample(available, min(3, len(available)))
        
        return f"Moving forward, you might want to {', '.join(selected)}."

    def generate_readme_content(self, version, analysis_data, what_changed):
        """Generate the entire content of the README file."""
        content = self._create_description_summary()
        content += "<!-- AUTO-SUMMARY-START -->\n"
        content += f"{self.analyze_repository()}\n"
        content += "<!-- AUTO-SUMMARY-END -->\n\n"
        content += f"{self.generate_dynamic_sections(analysis_data)}\n"
        content += "## 10. Project Map\n\n"
        content += f"{self.generate_project_map()}\n\n"
        content += "## 13. Last Version Summary\n\n"
        content += f"The last version is `{version}`. Detailed change log and metrics:\n"
        content += f"{what_changed}\n"
        
        # Ensure analysis_data has diff_data for benefit analysis
        if "diff_data" not in analysis_data:
            analysis_data["diff_data"] = self._generate_diff(self.previous_code_state, self._capture_repo_state())

        benefit_text = self.generate_user_benefit_analysis(analysis_data, what_changed)
        
        practical_impact = "Significant improvement to project maintainability and documentation sync."
        if "### 7. Practical Impact" in benefit_text:
            try:
                impact_lines = [line.strip() for line in benefit_text.split("### 7. Practical Impact")[1].strip().split("\n") if line.strip()]
                if len(impact_lines) >= 1:
                    practical_impact = impact_lines[0]
                    if len(impact_lines) >= 2:
                        practical_impact += f" {impact_lines[1]}"
            except (IndexError, AttributeError):
                pass
        content += f"\n**Practical Impact**: {practical_impact}\n\n"
        
        history_start_marker, history_end_marker = "## 14. Version History", "## 15. Contacts"
        try:
            with open(README_FILE, "r", encoding="utf-8") as f:
                existing_content = f.read()
                start, end = existing_content.find(history_start_marker), existing_content.find(history_end_marker)
                existing_history = existing_content[start + len(history_start_marker):end].strip() if start != -1 and end != -1 else ""
        except FileNotFoundError:
            existing_history = ""
        
        # Extract previous "What's Possibly Next" for uniqueness
        previous_suggestions = ""
        if existing_history:
            prev_next = re.findall(r"### What's Possibly Next\n(.*?)(?=\n## Version|\n## 15\. Contacts|$)", existing_history, re.DOTALL)
            previous_suggestions = "\n".join(prev_next).strip()

        # Strip legacy sections and limit history to top 3
        if existing_history:
            # Remove "Change Visualization" sections
            existing_history = re.sub(r"### 📊 Change Visualization\n\n```mermaid.*?```\n+", "", existing_history, flags=re.DOTALL)
            # Remove standalone "File-level Insights" text sections (if they exist without diagrams)
            existing_history = re.sub(r"### 🔍 File-level Insights\n\n(- .*?\n)+", "", existing_history)
            
            # Limit to most recent 2 existing versions (to make room for the 1 new one)
            history_versions = re.split(r"(?=## Version \d+\.\d+\.\d+)", existing_history)
            # Filter out empty strings from split
            history_versions = [v.strip() for v in history_versions if v.strip()]
            if len(history_versions) > 2:
                existing_history = "\n\n".join(history_versions[:2])
            else:
                existing_history = "\n\n".join(history_versions)

        new_entry = (
            f"## Version {version}\n"
            f"### Goals\n{self.infer_goals_from_summary(what_changed, analysis_data)}\n\n"
            f"### What Changed\n{what_changed}\n\n"
            f"### What's Good for the User\n{benefit_text}\n\n"
            f"### What's Possibly Next\n{self.suggest_next_steps(analysis_data, previous_suggestions)}\n"
        )
        content += f"{history_start_marker}\n{new_entry}\n\n{existing_history}\n"
        content += "## 15. Contacts\n\n"
        content += f"*   **Email:** {CONTACT_EMAIL}\n*   **Repository:** {REPOSITORY_ADDRESS}\n\n"
        content += "## 16. Privacy & Terms\n\n"
        content += f"*   **Privacy Policy:** [{PRIVACY_POLICY_FILE}]({PRIVACY_POLICY_FILE})\n\n"
        content += "## 17. Investor Relations\n\n"
        content += f"> [!IMPORTANT]\n"
        content += f"> **If you want to be my investor in my new AI-based project - link to [ndaotec.com](http://ndaotec.com)**\n\n"
        content += "## 18. Copyright\n\n"
        content += f"{COPYRIGHT_TEXT}\n"
        return content

    def update_readme(self, content):
        """Update the appropriate README file based on repository context."""
        # Determine which README to update based on context
        if self.is_ndaversis_repo():
            # In ndaversis repo: update both files
            # User README for this instance
            with open(USER_README_FILE, "w", encoding="utf-8") as f:
                f.write(content)
            # Ndaversis-specific README
            with open(NDAVERSIS_README_FILE, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"README files updated: {USER_README_FILE}, {NDAVERSIS_README_FILE}")
        else:
            # In user's repo: update only user README
            with open(USER_README_FILE, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"README updated: {USER_README_FILE}")

    def main_cli(self, cli_args):
        """Run the command-line interface."""
        # Use the already loaded previous state
        old_state = self.previous_code_state

        # Capture the new state and generate a diff
        new_state = self._capture_repo_state()
        diff_data = self._generate_diff(old_state, new_state)
        change_summary = self.generate_change_summary(old_state, new_state, diff_data=diff_data)

        # Update version
        if cli_args.major:
            self.version.increment_major()
        elif cli_args.minor:
            self.version.increment_minor()
        elif cli_args.patch:
            self.version.increment_patch()
        else:
            suggestion = self.suggest_version_bump(change_summary)
            print(f"No version flag provided. AI suggested bump: {suggestion}")
            if suggestion == "major":
                self.version.increment_major()
            elif suggestion == "minor":
                self.version.increment_minor()
            else:
                self.version.increment_patch()

        # Generate and update the README
        analysis_data, _ = self._analyze_codebase()
        analysis_data["diff_data"] = diff_data
        readme_content = self.generate_readme_content(
            str(self.version), analysis_data, change_summary
        )
        self.update_readme(readme_content)

        # Save the new state and version
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(new_state, f, indent=2)
        self.save_version(str(self.version))
        self.update_changelog(self.version, change_summary)

        print(f"Version updated to {self.version}")

    def main_gui(self, test_mode=False):
        """Run the Flet GUI with futuristic Neumorphism/Brutalism design."""
        if not ft:
            print("Flet not installed. Please run 'pip install flet' to use the GUI.")
            return

        def main(page: ft.Page):
            page.title = "NDAVERSIS - Agentic Version System"
            page.theme_mode = ft.ThemeMode.DARK
            page.bgcolor = "#0a0e27"  # Deep space blue
            page.padding = 0
            page.window_width = 700
            page.window_height = 850
            page.scroll = ft.ScrollMode.ADAPTIVE
            
            # Neumorphic card container
            def create_neomorphic_card(content, padding=30):
                return ft.Container(
                    content=content,
                    padding=padding,
                    margin=20,
                    border_radius=20,
                    bgcolor="#151b35",
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=20,
                        color="#00000040",
                        offset=ft.Offset(0, 10)
                    ),
                    border=ft.border.all(1, "#1f2847")
                )
            
            # Brutalist header with geometric design
            header = ft.Container(
                content=ft.Column([
                    ft.Text(
                        "NDAVERSIS",
                        size=48,
                        weight=ft.FontWeight.BOLD,
                        font_family="Courier New",  # Brutalist monospace
                        color="#00d9ff"  # Cyan
                    ),
                    ft.Text(
                        f"v{self.version}",
                        size=18,
                        weight=ft.FontWeight.W_300,
                        color="#6c7a9b"
                    ),
                    ft.Container(
                        width=100,
                        height=4,
                        bgcolor="#00d9ff",
                        border_radius=2,
                        margin=ft.margin.only(top=10)
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=40,
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_left,
                    end=ft.alignment.bottom_right,
                    colors=["#0a0e27", "#1a1f3a", "#0f1729"]
                )
            )
            
            # Neumorphic input field
            change_input = ft.TextField(
                label="Version Changes",
                label_style=ft.TextStyle(color="#6c7a9b", size=14),
                multiline=True,
                min_lines=4,
                max_lines=6,
                hint_text="Describe what changed in this version...",
                hint_style=ft.TextStyle(color="#3d4663"),
                border_color="#1f2847",
                focused_border_color="#00d9ff",
                bgcolor="#0d1128",
                color="#e0e6f0",
                text_size=15,
                border_radius=15,
                content_padding=20
            )
            
            # Status indicator
            status_text = ft.Text("", size=14, color="#00d9ff", text_align=ft.TextAlign.CENTER)
            pb = ft.ProgressBar(
                width=500,
                height=4,
                color="#00d9ff",
                bgcolor="#1f2847",
                visible=False,
                border_radius=2
            )
            
            def on_increment(increment_type):
                if not change_input.value.strip():
                    status_text.value = "⚠️ Please describe what changed first!"
                    status_text.color = "#ff9500"  # Orange warning
                    page.update()
                    return

                status_text.value = f"Processing {increment_type} update..."
                status_text.color = "#00d9ff"
                pb.visible = True
                page.update()

                try:
                    # Logic
                    if increment_type == "Major":
                        self.version.increment_major()
                    elif increment_type == "Minor":
                        self.version.increment_minor()
                    else:
                        self.version.increment_patch()
                    what_changed = change_input.value.strip()
                    analysis_data, _ = self._analyze_codebase()
                    readme_content = self.generate_readme_content(self.version, analysis_data, what_changed)
                    self.update_readme(readme_content)
                    self.save_version(str(self.version))
                    
                    # Save to version history if module available
                    if version_history:
                        version_data = {
                            "version": str(self.version),
                            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "author": getpass.getuser(),
                            "changes": what_changed,
                            "goals": self.infer_goals_from_summary(what_changed, analysis_data)
                        }
                        version_history.add_version(version_data)

                    status_text.value = f"✅ Success! Version updated to {self.version}"
                    status_text.color = "#00ff88"  # Bright green
                    pb.visible = False
                    change_input.value = ""
                    page.update()
                    
                    # Small delay before closing
                    import time
                    time.sleep(1.5)
                    page.window_close()
                except Exception as e:
                    status_text.value = f"❌ Error: {str(e)}"
                    status_text.color = "#ff3366"  # Bright red
                    pb.visible = False
                    page.update()
            
            # Brutalist geometric buttons with gradients
            def create_version_button(label, icon, increment_type, gradient_colors):
                return ft.Container(
                    content=ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon(icon, size=20, color="#ffffff"),
                            ft.Text(label, size=14, weight=ft.FontWeight.BOLD, color="#ffffff")
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
                        on_click=lambda _: on_increment(increment_type),
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=12),
                            padding=ft.padding.symmetric(horizontal=25, vertical=18),
                            bgcolor="#1a1f3a",
                            overlay_color="#00000020"
                        ),
                        width=180,
                        height=60
                    ),
                    gradient=ft.LinearGradient(
                        colors=gradient_colors,
                        begin=ft.alignment.top_left,
                        end=ft.alignment.bottom_right
                    ),
                    border_radius=12,
                    padding=2  # Border effect
                )
            
            buttons = ft.Column([
                create_version_button("PATCH +0.0.1", ft.icons.UPGRADE, "Patch", ["#00d9ff", "#0099cc"]),
                create_version_button("MINOR +0.1.0", ft.icons.ROCKET_LAUNCH, "Minor", ["#5e60ce", "#7b2cbf"]),
                create_version_button("MAJOR +1.0.0", ft.icons.STAR, "Major", ["#ff6b35", "#f72585"])
            ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            
            # Version Update Tab Content
            version_tab_content = create_neomorphic_card(
                ft.Column([
                    ft.Text("CHANGE LOG", size=16, weight=ft.FontWeight.BOLD, color="#6c7a9b", font_family="Courier New"),
                    ft.Container(height=10),
                    change_input,
                    ft.Container(height=25),
                    buttons,
                    ft.Container(height=20),
                    ft.Column([status_text, pb], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                ])
            )
            
            # Metrics Dashboard Tab Content
            metrics_status = ft.Text("", size=14, color="#00d9ff", text_align=ft.TextAlign.CENTER)
            metrics_container = ft.Column([], scroll=ft.ScrollMode.ADAPTIVE)
            
            def calculate_metrics_ui():
                metrics_status.value = "Calculating metrics..."
                metrics_status.color = "#00d9ff"
                page.update()
                
                try:
                    metrics_result = self.metrics.get_all_metrics()
                    
                    # Clear previous metrics
                    metrics_container.controls.clear()
                    
                    # Overall score card
                    overall_score = metrics_result['overall_score']
                    score_color = "#00ff88" if overall_score >= 80 else "#00d9ff" if overall_score >= 60 else "#ff9500"
                    
                    metrics_container.controls.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Text("OVERALL SCORE", size=14, color="#6c7a9b", weight=ft.FontWeight.BOLD),
                                ft.Text(f"{overall_score}%", size=48, color=score_color, weight=ft.FontWeight.BOLD),
                                ft.ProgressBar(value=overall_score/100, color=score_color, bgcolor="#1f2847", height=8, border_radius=4)
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            padding=20,
                            border_radius=15,
                            bgcolor="#151b35",
                            border=ft.border.all(1, "#1f2847"),
                            margin=ft.margin.only(bottom=20)
                        )
                    )
                    
                    # Individual metrics
                    for metric_name, metric_data in metrics_result['metrics'].items():
                        score = metric_data['score']
                        summary = metric_data.get('summary', 'No summary available')
                        details = metric_data.get('details', {})
                        
                        # Color based on score
                        if score >= 80:
                            color = "#00ff88"
                            status_icon = "✓"
                        elif score >= 60:
                            color = "#00d9ff"
                            status_icon = "○"
                        elif score >= 40:
                            color = "#ff9500"
                            status_icon = "△"
                        else:
                            color = "#ff3366"
                            status_icon = "✗"
                        
                        metric_title = metric_name.replace('_', ' ').title()
                        
                        # Create expandable tile
                        details_text = "\n".join([f"{k}: {v}" for k, v in details.items()])
                        
                        metric_tile = ft.ExpansionTile(
                            title=ft.Row([
                                ft.Text(status_icon, size=20, color=color),
                                ft.Text(metric_title, size=14, color="#e0e6f0", weight=ft.FontWeight.BOLD),
                                ft.Container(expand=True),
                                ft.Text(f"{score}%", size=16, color=color, weight=ft.FontWeight.BOLD)
                            ]),
                            subtitle=ft.ProgressBar(value=score/100, color=color, bgcolor="#1f2847", height=4, border_radius=2),
                            controls=[
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text("Summary:", size=12, color="#6c7a9b", weight=ft.FontWeight.BOLD),
                                        ft.Text(summary if summary else "AI summary unavailable", size=12, color="#e0e6f0"),
                                        ft.Container(height=10),
                                        ft.Text("Details:", size=12, color="#6c7a9b", weight=ft.FontWeight.BOLD),
                                        ft.Text(details_text if details_text else "No details", size=11, color="#9ca3b8")
                                    ]),
                                    padding=15,
                                    bgcolor="#0d1128",
                                    border_radius=10
                                )
                            ],
                            bgcolor="#151b35",
                            collapsed_bgcolor="#151b35",
                            text_color="#e0e6f0",
                            icon_color="#00d9ff"
                        )
                        
                        metrics_container.controls.append(
                            ft.Container(
                                content=metric_tile,
                                margin=ft.margin.only(bottom=10),
                                border_radius=10,
                                border=ft.border.all(1, "#1f2847")
                            )
                        )
                    
                    metrics_status.value = f"✅ Metrics calculated! Overall: {overall_score}%"
                    metrics_status.color = "#00ff88"
                    page.update()
                    
                except Exception as e:
                    metrics_status.value = f"❌ Error: {str(e)}"
                    metrics_status.color = "#ff3366"
                    page.update()
            
            def export_metrics():
                try:
                    import json
                    metrics_result = self.metrics.get_all_metrics()
                    with open("ndaversis_metrics.json", "w") as f:
                        json.dump(metrics_result, f, indent=2)
                    metrics_status.value = "✅ Exported to ndaversis_metrics.json"
                    metrics_status.color = "#00ff88"
                    page.update()
                except Exception as e:
                    metrics_status.value = f"❌ Export failed: {str(e)}"
                    metrics_status.color = "#ff3366"
                    page.update()
            
            metrics_tab_content = ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.ElevatedButton(
                            "Calculate Metrics",
                            icon=ft.icons.ANALYTICS,
                            on_click=lambda _: calculate_metrics_ui(),
                            style=ft.ButtonStyle(
                                bgcolor="#00d9ff",
                                color="#ffffff",
                                padding=15
                            )
                        ),
                        ft.ElevatedButton(
                            "Export JSON",
                            icon=ft.icons.DOWNLOAD,
                            on_click=lambda _: export_metrics(),
                            style=ft.ButtonStyle(
                                bgcolor="#5e60ce",
                                color="#ffffff",
                                padding=15
                            )
                        )
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=15),
                    padding=20
                ),
                metrics_status,
                ft.Container(height=10),
                metrics_container
            ], scroll=ft.ScrollMode.ADAPTIVE)
            
            # Create tabs
            tabs = ft.Tabs(
                selected_index=0,
                animation_duration=300,
                tabs=[
                    ft.Tab(
                        text="Version Update",
                        icon=ft.icons.UPGRADE,
                        content=version_tab_content
                    ),
                    ft.Tab(
                        text="Metrics Dashboard",
                        icon=ft.icons.DASHBOARD,
                        content=metrics_tab_content
                    )
                ],
                label_color="#00d9ff",
                unselected_label_color="#6c7a9b",
                indicator_color="#00d9ff"
            )
            
            # Footer with geometric accent
            footer = ft.Container(
                content=ft.Column([
                    ft.Container(height=2, bgcolor="#1f2847", width=200),
                    ft.Text(
                        "Agentic Automation • ndaotec.com",
                        size=11,
                        color="#3d4663",
                        text_align=ft.TextAlign.CENTER,
                        font_family="Courier New"
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                margin=ft.margin.only(top=20, bottom=20)
            )
            
            # Main layout with gradient background
            page.add(
                ft.Stack([
                    # Gradient background
                    ft.Container(
                        gradient=ft.LinearGradient(
                            begin=ft.alignment.top_left,
                            end=ft.alignment.bottom_right,
                            colors=["#0a0e27", "#1a1f3a", "#0f1729"]
                        ),
                        expand=True
                    ),
                    # Content
                    ft.Column([
                        header,
                        ft.Container(
                            content=tabs,
                            padding=20,
                            expand=True
                        ),
                        footer
                    ], scroll=ft.ScrollMode.ADAPTIVE, expand=True)
                ], expand=True)
            )


        ft.app(target=main, view=ft.AppView.FLET_APP)

    def health_check(self):
        """Runs a health check on the project setup."""
        print("Running health check...")
        errors = []

        if not os.path.exists(CONFIG_FILE):
            errors.append(f"Configuration file '{CONFIG_FILE}' not found.")

        if not os.path.exists(REQUIREMENTS_FILE):
            errors.append(f"{REQUIREMENTS_FILE} file not found.")

        if self.ai_config:
            provider = self.ai_config.get("ai_provider")
            if not provider:
                errors.append("No AI provider specified in config.json.")
            else:
                api_key_env = f"{provider.upper()}_API_KEY"
                if not os.getenv(api_key_env):
                    errors.append(f"Environment variable '{api_key_env}' for AI provider '{provider}' is not set.")

        if errors:
            print("Health check failed with the following errors:")
            for error in errors:
                print(f"- {error}")
        else:
            print("Health check passed. All configurations seem correct.")

    def install_pre_commit_hook(self):
        """Installs a pre-commit hook."""
        hook_script = f"#!/bin/sh\npython3 ndaversis.py cli --patch\ngit add ndaversis.py {README_FILE}\n"
        hook_path = os.path.join(".git", "hooks", "pre-commit")
        try:
            with open(hook_path, "w", encoding="utf-8") as f:
                f.write(hook_script)
            os.chmod(hook_path, 0o755)
            print("Successfully installed pre-commit hook.")
        except IOError as e:
            print(f"Error installing pre-commit hook: {e}")

# --- Entry Point ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ndaversis - Agentic Semantic Version Info System")
    subparsers = parser.add_subparsers(dest="command")

    gui_parser = subparsers.add_parser("gui", help="Run the GUI")
    gui_parser.add_argument("--test", action="store_true", help="Run in test mode")

    cli_parser = subparsers.add_parser("cli", help="Run the CLI")
    group = cli_parser.add_mutually_exclusive_group(required=False)
    group.add_argument("--major", action="store_true", help="Increment major version")
    group.add_argument("--minor", action="store_true", help="Increment minor version")
    group.add_argument("--patch", action="store_true", help="Increment patch version")

    install_parser = subparsers.add_parser("install-hook", help="Install pre-commit hook")
    health_parser = subparsers.add_parser("health", help="Run a health check")
    audit_parser = subparsers.add_parser("audit", help="Run repository audit")
    metrics_parser = subparsers.add_parser("metrics", help="Calculate repository evaluation metrics")

    app = Ndaversis()

    args = parser.parse_args()

    if args.command == "gui":
        app.main_gui(test_mode=args.test)
    elif args.command == "cli":
        app.main_cli(args)
    elif args.command == "install-hook":
        app.install_pre_commit_hook()
    elif args.command == "health":
        app.health_check()
    elif args.command == "audit":
        print("Running repository audit...")
        features, _ = app._analyze_codebase()
        print(f"\nRepository Analysis:")
        print(f"  Total Lines: {features['metrics']['total_lines']}")
        print(f"  Code Lines: {features['metrics']['code_lines']}")
        print(f"  Comment Lines: {features['metrics']['comment_lines']}")
        print(f"  Functions: {len(features['functions'])}")
        print(f"  Classes: {len(features['classes'])}")
        print(f"  Imports: {len(features['imports'])}")
    elif args.command == "metrics":
        print("Calculating repository metrics...")
        metrics_result = app.metrics.get_all_metrics()
        
        # Display results
        print(f"\n{'='*60}")
        print(f"REPOSITORY EVALUATION METRICS")
        print(f"{'='*60}")
        print(f"\nOverall Score: {metrics_result['overall_score']}%")
        print(f"Timestamp: {metrics_result['timestamp']}")
        print(f"\n{'='*60}\n")
        
        # Display each metric
        for metric_name, metric_data in metrics_result['metrics'].items():
            metric_title = metric_name.replace('_', ' ').title()
            score = metric_data['score']
            summary = metric_data['summary']
            
            # Color code based on score
            if score >= 80:
                status = "✓ EXCELLENT"
            elif score >= 60:
                status = "○ GOOD"
            elif score >= 40:
                status = "△ FAIR"
            else:
                status = "✗ NEEDS IMPROVEMENT"
            
            print(f"{metric_title}: {score}% {status}")
            print(f"  {summary}")
            print()
        
        # Save to file
        metrics_file = "ndaversis_metrics.json"
        with open(metrics_file, "w") as f:
            json.dump(metrics_result, f, indent=2)
        print(f"\nDetailed metrics saved to: {metrics_file}")
    else:
        app.main_gui()
