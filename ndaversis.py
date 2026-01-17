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
import tkinter as tk
from tkinter import messagebox
import argparse
import sys
import ast
import json
import datetime
import getpass
from typing import Optional
# import google.generativeai as genai
# import openai
# import anthropic
# from deepseek import DeepSeekAPI

import difflib

# --- Constants ---
README_FILE = "readme.md"
CONFIG_FILE = "config.json"
STATE_FILE = "ndaversis_state.json"
LOGS_FILE = "ndaversis_logs.py"
CONTACT_EMAIL = "n@ndaotec.com"
COPYRIGHT_HOLDER = "Nikita Andreevich Drozdov"
REPOSITORY_ADDRESS = "https://github.com/lystwork/ndaversis"
COPYRIGHT_TEXT = (
    "ndaotec.com. @ All rights reserved - Nikita Andreevich Drozdov. "
    "All rights belong to their respective owners."
)
__version__ = "0.0.34"

# --- AI Service Classes ---
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
        """Factory function to get an AI service instance."""
        if not self.ai_config:
            return None

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
        }

        service_class = service_map.get(provider)

        if service_class:
            if api_key:
                return service_class(api_key)
            else:
                print(f"{api_key_env_var} environment variable not found. AI service disabled.")
        else:
            print(f"Unknown AI provider: {provider}. AI service disabled.")

        return None

    def load_previous_code_state(self) -> dict:
        """
        This method is deprecated and now returns an empty dictionary.
        The functionality to track code state in the README has been removed.
        """
        return {}

    def _process_python_file(self, filepath, features, method_names):
        """Process a single Python file to extract features."""
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()
        try:
            tree = ast.parse(code)
            module_docstring = ast.get_docstring(tree) or ""
            features["files"][filepath] = {"docstring": module_docstring}
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = {
                        item.name: [arg.arg for arg in item.args.args if arg.arg != "self"]
                        for item in node.body
                        if isinstance(item, ast.FunctionDef)
                    }
                    method_names.update(methods.keys())
                    features["classes"][node.name] = {"methods": methods}
                elif isinstance(node, ast.Import):
                    features["imports"].update(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    features["imports"].add(node.module)
                elif isinstance(node, ast.FunctionDef) and node.name not in method_names:
                    docstring = ast.get_docstring(node)
                    features["functions"][node.name] = {
                        "args": [arg.arg for arg in node.args.args],
                        "docstring": docstring if docstring else "",
                    }
        except SyntaxError:
            pass
        return code

    def _analyze_codebase(self):
        """Analyze the codebase to identify key features."""
        features = {"imports": set(), "classes": {}, "functions": {}, "files": {}}
        method_names = set()
        last_code = ""
        for root, _, files in os.walk("."):
            if ".git" in root:
                continue
            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    last_code = self._process_python_file(filepath, features, method_names)
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

    def _generate_diff(self, old_state, new_state):
        """Generate a concise diff between two repository states."""
        diff = []
        all_files = set(old_state.keys()) | set(new_state.keys())
        for file in sorted(all_files):
            if file not in old_state:
                diff.append(f"Added file: {file}")
            elif file not in new_state:
                diff.append(f"Removed file: {file}")
            elif old_state[file] != new_state[file]:
                diff.append(f"Modified file: {file}")
        return "\n".join(diff) if diff else "No significant changes detected."

    def generate_change_summary(self, old_state, new_state):
        """Compare two code states and generate a summary of changes."""
        return self._generate_diff(old_state, new_state)

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
        use_cases = "## 3. Use Cases\n\n"
        if self.ai_service:
            # Use AI to generate content and remove potential redundant headers
            content = self.ai_service.generate_content(
                self._generate_use_cases_prompt(), analysis_data
            )
            use_cases += re.sub(r"^#+ (3\.)? ?Use Cases\n*", "", content, flags=re.MULTILINE).strip()
            use_cases += "\n\n### Use Case Diagram\n\n"
            use_cases += f"```mermaid\n{self.generate_use_case_diagram(analysis_data)}\n```\n"
        else:
            items = self._generate_section(
                "3. Use Cases", analysis_data, "Use Case:", "*   **{name}**: {doc}\n"
            )
            content_items = items.replace("## 3. Use Cases\n\n", "").strip()
            if not content_items:
                # Universal fallback based on detected functions
                funcs = list(analysis_data.get("functions", {}).keys())
                classes = list(analysis_data.get("classes", {}).keys())
                if funcs or classes:
                    for item in (funcs + classes)[:5]:
                        display_name = item.replace('_', ' ').title()
                        use_cases += f"*   **{display_name}**: Typical use case for leveraging the `{item}` component within the system.\n"
                else:
                    use_cases += "*   **General Usage**: Typical use case involving the core functionality of the repository.\n"
            else:
                use_cases += content_items + "\n"

        user_stories = "## 4. User Stories\n\n"
        if self.ai_service:
            content = self.ai_service.generate_content(
                self._generate_user_stories_prompt(), analysis_data
            )
            user_stories += re.sub(r"^#+ (4\.)? ?User Stories\n*", "", content, flags=re.MULTILINE).strip()
            user_stories += "\n\n### BPMN Diagram\n\n"
            user_stories += f"```mermaid\n{self.generate_bpmn_diagram(analysis_data)}\n```\n"
        else:
            items = self._generate_section(
                "4. User Stories",
                analysis_data,
                "User Story:",
                "*   **As a user,** I want to be able to {name}, so that {doc}.\n",
            )
            content_items = items.replace("## 4. User Stories\n\n", "").strip()
            if not content_items:
                items_to_use = list(analysis_data.get("functions", {}).keys()) + list(analysis_data.get("classes", {}).keys())
                if items_to_use:
                    for item in items_to_use[:5]:
                        user_stories += f"*   **As a developer,** I want to utilize `{item}` so that I can achieve robust integration and functionality.\n"
                else:
                    user_stories += "*   **As a user,** I want to interact with the repository effectively so that I can fulfill my project requirements.\n"
            else:
                user_stories += content_items + "\n"
        faq = self._generate_section(
            "5. FAQ", analysis_data, "FAQ:", "**Q: {name}?**\n**A:** {doc}\n\n"
        )
        if faq.strip() == "## 5. FAQ":
            items_to_use = list(analysis_data.get("functions", {}).keys()) + list(analysis_data.get("classes", {}).keys())
            if items_to_use:
                for item in items_to_use[:3]:
                    display_name = item.replace('_', ' ').title()
                    faq += f"*   **Q: What is the purpose of `{item}`?**\n    **A:** It is a core component used to handle `{display_name}` related operations within the project.\n"
            else:
                faq += "*   **Q: How do I get started?**\n    **A:** Refer to the Installation and How To sections for initial setup and usage instructions.\n"
            
        how_to = self._generate_section(
            "6. How To", analysis_data, "How To:", "### {name}\n\n{doc}\n\n"
        )
        if how_to.strip() == "## 6. How To":
            items_to_use = list(analysis_data.get("functions", {}).keys())
            if items_to_use:
                main_func = "main" if "main" in items_to_use else items_to_use[0]
                how_to += f"### Basic Usage Guide\n\nTo use this project, you can invoke the primary functions. For example:\n```python\n# Basic invocation of {main_func}\n{main_func}()\n```\n\n"
            else:
                how_to += "### Usage Instructions\n\nFollow the installation steps and then run the primary entry point script of the repository.\n"
        features_str = "## 7. Features\n\n"
        features_items = [
            f"*   **{func_name.replace('_', ' ').title()}**: {func_data.get('docstring', '').splitlines()[0].strip().split(': ')[1]}\n"
            for func_name, func_data in analysis_data["functions"].items()
            if func_data.get("docstring")
            and ": " in func_data.get("docstring", "").splitlines()[0]
        ]
        if not features_items:
            items_to_use = list(analysis_data.get("functions", {}).keys())
            if items_to_use:
                features_items = [
                    f"*   **{item.replace('_', ' ').title()}**: Provides specialized functionality for `{item}` within the codebase.\n"
                    for item in items_to_use[:5]
                ]
            else:
                features_items = [
                    "*   **Codebase Analysis**: Automated parsing and mapping of repository structure.\n",
                    "*   **Documentation Automation**: Dynamic README generation tailored to the project content.\n"
                ]
        features_str += "".join(features_items)
        requirements = "## 8. Requirements\n\n*   Python 3.6+\n"
        if "tkinter" in analysis_data["imports"]:
            requirements += "*   `tkinter` (for the GUI, usually included with Python)\n"
        install = (
            "## 9. Install\n\nTo install the required dependencies, run the following command:\n\n"
            "```\npip install -r requirements.txt\n```\n"
        )
        modules_map = "## 11. Modules Map\n\n"
        modules_map_items = [
            f"*   `{os.path.basename(file_path)}`: "
            f"{file_data.get('docstring', '').splitlines()[0].strip()}"
            for file_path, file_data in analysis_data.get("files", {}).items()
            if file_data.get("docstring")
        ]
        if not modules_map_items:
            modules_map_items = [f"*   `{os.path.basename(fp)}`: Python module." for fp in analysis_data.get("files", {}).keys()]
        modules_map += "\n".join(modules_map_items)
        
        # Add Mermaid Module Diagram
        modules_map += "\n\n### Module Structure Diagram\n\n"
        modules_map += "```mermaid\nclassDiagram\n"
        if not analysis_data.get("classes"):
            modules_map += "    class MainModule {\n        +main()\n    }\n"
        else:
            for class_name, class_data in analysis_data.get("classes", {}).items():
                modules_map += f"    class {class_name} {{\n"
                for method in class_data.get("methods", {}).keys():
                    modules_map += f"        +{method}()\n"
                modules_map += "    }\n"
        modules_map += "```\n"

        dependencies_map = "## 12. Dependencies Map\n\n"
        stdlib_modules = set(sys.stdlib_module_names)
        deps = [
            dep
            for dep in analysis_data.get("imports", [])
            if dep not in stdlib_modules
        ]
        if not deps:
            deps = ["No external dependencies."]
        dependencies_map += "\n".join([f"*   `{dep}`" for dep in deps])
        
        # Add Mermaid Dependency Diagram
        dependencies_map += "\n\n### Dependency Graph\n\n"
        dependencies_map += "```mermaid\ngraph TD\n"
        project_name = "Project"
        external_deps = [d for d in deps if d != "No external dependencies."]
        if not external_deps:
            dependencies_map += f"    {project_name} --> StdLib[Standard Library]\n"
        else:
            for dep in external_deps:
                dependencies_map += f"    {project_name} --> {dep}\n"
        dependencies_map += "```\n"

        return "\n".join(
            filter(None, [
                use_cases,
                user_stories,
                faq,
                how_to,
                features_str,
                requirements,
                install,
                modules_map,
                dependencies_map,
            ])
        )

    def generate_project_description(self):
        """Analyze the repository to generate a project description."""
        features, code = self._analyze_codebase()
        if self.ai_service:
            prompt = (
                "Generate a project description for a README.md file. The description "
                "should be based on the provided codebase analysis. It should cover: "
                "What is this repository?, How it operates?, How it's designed?, and "
                "What is its core functionality?"
            )
            return self.ai_service.generate_content(prompt, (features, code))
        try:
            with open(README_FILE, "r", encoding="utf-8") as f:
                first_line = f.readline()
                project_name = first_line.split(":")[0].replace("# 1. ", "").strip()
        except (IOError, IndexError, FileNotFoundError):
            project_name = "This Repository"
            
        core_functionality = "provide a robust set of features"
        if features["functions"]:
            core_functionality = f"implement {len(features['functions'])} functions for various system tasks"
            
        design = "modularly designed" if features["classes"] else "script-based"
        operation = "features a comprehensive codebase analysis and documentation system"
        
        if "tkinter" in features["imports"]:
            operation += ", including a graphical user interface"
        if "argparse" in features["imports"]:
            operation += " and a command-line interface"
            
        return (
            f"{project_name} is a {design} solution designed to {core_functionality}. "
            f"It {operation}. This tool is built to be easily integrated and self-updating, "
            "providing a streamlined experience for project management and development."
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
        
        # Add Mermaid Project Diagram
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
        project_map += "```"
        return project_map

    def analyze_repository(self):
        """Analyze the repository to generate a summary."""
        total_files, py_files, py_lines = 0, 0, 0
        for root, dirs, files in os.walk("."):
            if ".git" in dirs:
                dirs.remove(".git")
            for file in files:
                total_files += 1
                if file.endswith(".py"):
                    py_files += 1
                    try:
                        with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                            py_lines += len(f.readlines())
                    except (IOError, UnicodeDecodeError):
                        pass

        synthesis = ""
        if self.ai_service:
            features, code = self._analyze_codebase()
            synthesis = self.ai_service.generate_content(
                self._generate_repo_synthesis_prompt(), (features, code)
            )

        summary = (
            f"\n\n"
            f"---\n"
            f"*This summary is auto-generated and reflects the state of the repository at "
            f"the time of the last version update.*\n\n"
            f"**Repository Analysis:**\n"
            f"- **Total Files:** {total_files}\n"
            f"- **Python Files:** {py_files}\n"
            f"- **Total Python Lines:** {py_lines}\n"
        )
        if synthesis:
            summary += f"\n**Goal & Tasks synthesis:**\n{synthesis}\n"
        summary += f"---\n"
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

    def generate_user_benefit_analysis(self, analysis_data):
        """Generate the 7-step analysis for the 'What's Good for the User' section."""
        if self.ai_service:
            prompt = (
                "Generate a 7-step analysis for the 'What's Good for the User' section "
                "of a README.md file. The analysis should be based on the provided "
                "codebase analysis. The steps are: User's Goal, Evaluation of the "
                "repository Solution, Core Functionality, Safety & Side Effects, "
                "Completeness, Assessment, and Is that good result?"
            )
            return self.ai_service.generate_content(prompt, analysis_data)
        user_goal = (
            "The user wants a fully automated and dynamically updated README.md "
            "that accurately reflects the state of the repository."
        )
        evaluation = (
            "The solution successfully meets the user's goal by implementing a robust "
            "system for auto-generating the README.md from the codebase."
        )
        core_functionality = (
            f"The core functionality is the dynamic generation of the README.md, "
            f"which now includes {len(analysis_data['functions'])} functions and "
            f"{len(analysis_data['classes'])} classes."
        )
        safety = (
            "The solution is safe and has no unintended side effects. The primary "
            "side effect is that the README.md is now entirely managed by the "
            "script, which is the intended outcome."
        )
        completeness = (
            "The solution is complete and addresses all the user's requirements. "
            "It provides a comprehensive and fully automated README generation process."
        )
        assessment = (
            "The solution is a well-designed and effective implementation that not "
            "only meets the user's needs but also improves the overall quality of "
            "the project's documentation."
        )
        is_good_result = (
            "Yes, this is an excellent result that provides significant value to the "
            "user by automating a critical part of the development workflow."
        )
        return (
            f"### 1. User's Goal\n{user_goal}\n\n"
            f"### 2. Evaluation of the repository Solution\n{evaluation}\n\n"
            f"### 3. Core Functionality\n{core_functionality}\n\n"
            f"### 4. Safety & Side Effects\n{safety}\n\n"
            f"### 5. Completeness\n{completeness}\n\n"
            f"### 6. Assessment\n{assessment}\n\n"
            f"### 7. Is that good result?\n{is_good_result}\n"
        )

    def infer_goals_from_summary(self, change_summary):
        """Infer the goals of the changes from the change summary."""
        goals = []
        if "Added functions" in change_summary or "Added classes" in change_summary:
            goals.append("enhance functionality")
        if "Removed functions" in change_summary or "Removed classes" in change_summary:
            goals.append("refactor and simplify the codebase")
        if "Added imports" in change_summary or "Removed imports" in change_summary:
            goals.append("update dependencies and manage imports")
        if not goals:
            return "The main goal was to address minor updates and improvements."
        return f"The main goals of this update were to {', '.join(goals)}."

    def suggest_next_steps(self, analysis_data):
        """Suggest next steps for the project."""
        suggestions = []
        if not any("test" in func for func in analysis_data["functions"]):
            suggestions.append("add a dedicated test suite to improve robustness")
        if "tkinter" in analysis_data["imports"] and "argparse" in analysis_data["imports"]:
            suggestions.append("enhance the GUI and CLI with more features")
        if len(analysis_data["functions"]) > 15:
            suggestions.append(
                "consider modularizing the codebase to improve maintainability"
            )
        if not suggestions:
            return (
                "The project is in a good state, and the next steps will be "
                "determined by user feedback."
            )
        return f"The next steps for the project could be to {', '.join(suggestions)}."

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
        content += f"The last version is `{version}`. Summary of major changes:\n"
        # Make the summary a bit more descriptive if it's just a list of files
        descriptive_summary = what_changed.replace("Added file:", "New feature added:").replace("Modified file:", "Improved logic in:").replace("Removed file:", "Cleanup in:")
        content += f"{descriptive_summary}\n\n"
        history_start_marker, history_end_marker = "## 14. Version History", "## 15. Contacts"
        try:
            with open(README_FILE, "r", encoding="utf-8") as f:
                existing_content = f.read()
                start, end = existing_content.find(history_start_marker), existing_content.find(history_end_marker)
                existing_history = existing_content[start + len(history_start_marker):end].strip() if start != -1 and end != -1 else ""
        except FileNotFoundError:
            existing_history = ""
        new_entry = (
            f"## Version {version}\n"
            f"### Goals\n{self.infer_goals_from_summary(what_changed)}\n\n"
            f"### What Changed\n{what_changed}\n\n"
            f"### What's Good for the User\n{self.generate_user_benefit_analysis(analysis_data)}\n\n"
            f"### What's Possibly Next\n{self.suggest_next_steps(analysis_data)}\n"
        )
        content += f"{history_start_marker}\n{new_entry}\n\n{existing_history}\n"
        content += "## 15. Contacts\n\n"
        content += f"*   **Email:** {CONTACT_EMAIL}\n*   **Repository:** {REPOSITORY_ADDRESS}\n\n"
        content += "## 16. Copyright\n\n"
        content += f"{COPYRIGHT_TEXT}\n"
        return content

    def update_readme(self, content):
        """Update the readme.md file with the new content."""
        with open(README_FILE, "w", encoding="utf-8") as f:
            f.write(content)

    def main_cli(self, cli_args):
        """Run the command-line interface."""
        # Load the previous state
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                old_state = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            old_state = {}

        # Capture the new state and generate a diff
        new_state = self._capture_repo_state()
        change_summary = self.generate_change_summary(old_state, new_state)

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
        readme_content = self.generate_readme_content(
            str(self.version), self._analyze_codebase()[0], change_summary
        )
        self.update_readme(readme_content)

        # Save the new state and version
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(new_state, f, indent=2)
        self.save_version(str(self.version))
        self.update_changelog(self.version, change_summary)

        print(f"Version updated to {self.version}")

    def main_gui(self, test_mode=False):
        """Run the tkinter GUI."""
        if test_mode:
            self.version.increment_patch()
            self.save_version(str(self.version))
            print("GUI test mode complete.")
            return

        root = tk.Tk()
        root.title(f"Version Manager - Current Version: {self.version}")
        tk.Label(root, text="What changed:").pack()
        changed_entry = tk.Text(root, height=5, width=50)
        changed_entry.pack()

        def update_and_close(increment_func):
            increment_func()
            what_changed = changed_entry.get("1.0", tk.END).strip()
            analysis_data, _ = self._analyze_codebase()
            readme_content = self.generate_readme_content(self.version, analysis_data, what_changed)
            self.update_readme(readme_content)
            self.save_version(str(self.version))
            messagebox.showinfo("Success", f"Version updated to {self.version}")
            root.destroy()

        major_button = tk.Button(
            root, text="Increment Major", command=lambda: update_and_close(self.version.increment_major)
        )
        major_button.pack()
        minor_button = tk.Button(
            root, text="Increment Minor", command=lambda: update_and_close(self.version.increment_minor)
        )
        minor_button.pack()
        patch_button = tk.Button(
            root, text="Increment Patch", command=lambda: update_and_close(self.version.increment_patch)
        )
        patch_button.pack()
        root.mainloop()

    def health_check(self):
        """Runs a health check on the project setup."""
        print("Running health check...")
        errors = []

        if not os.path.exists(CONFIG_FILE):
            errors.append(f"Configuration file '{CONFIG_FILE}' not found.")

        if not os.path.exists("requirements.txt"):
            errors.append("requirements.txt file not found.")

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
        hook_script = "#!/bin/sh\npython3 ndaversis.py cli --patch\ngit add ndaversis.py readme.md\n"
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
    parser = argparse.ArgumentParser(description="Version Manager")
    subparsers = parser.add_subparsers(dest="command")

    gui_parser = subparsers.add_parser("gui", help="Run the GUI")
    gui_parser.add_argument("--test", action="store_true", help="Run in test mode")

    cli_parser = subparsers.add_parser("cli", help="Run the CLI")
    group = cli_parser.add_mutually_exclusive_group(required=False)
    group.add_argument("--major", action="store_true", help="Increment major version")
    group.add_argument("--minor", action="store_true", help="Increment minor version")
    group.add_argument("--patch", action="store_true", help="Increment patch version")

    install_parser = subparsers.add_parser("install-hook", help="Install pre-commit hook")
    health_check_parser = subparsers.add_parser("health-check", help="Run a health check")

    app = Ndaversis()

    args = parser.parse_args()

    if args.command == "gui":
        app.main_gui(test_mode=args.test)
    elif args.command == "cli":
        app.main_cli(args)
    elif args.command == "install-hook":
        app.install_pre_commit_hook()
    elif args.command == "health-check":
        app.health_check()
    else:
        app.main_gui()
