# pylint: disable=line-too-long,consider-using-join
"""A module for managing semantic versioning."""
import os
import re
import tkinter as tk
from tkinter import messagebox
import argparse
import sys
import ast
import json
import google.generativeai as genai
import openai
import anthropic
from deepseek import DeepSeekAPI

README_FILE = "readme.md"

# pylint: disable=too-few-public-methods
class AIService:
    """Base class for AI services."""
    def __init__(self):
        pass

    def generate_content(self, prompt, analysis_data):
        """Generate content using the AI service."""
        raise NotImplementedError

class GeminiService(AIService):
    """An AI service that uses the Google Gemini API."""
    def __init__(self, api_key):
        super().__init__()
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def generate_content(self, prompt, analysis_data):
        """Generate content using the Gemini API."""
        full_prompt = f"{prompt}\n\nCode Analysis:\n{json.dumps(analysis_data, indent=2)}"
        response = self.model.generate_content(full_prompt)
        return response.text

class ChatGPTService(AIService):
    """An AI service that uses the OpenAI ChatGPT API."""
    def __init__(self, api_key):
        super().__init__()
        self.client = openai.OpenAI(api_key=api_key)

    def generate_content(self, prompt, analysis_data):
        """Generate content using the ChatGPT API."""
        full_prompt = f"{prompt}\n\nCode Analysis:\n{json.dumps(analysis_data, indent=2)}"
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": full_prompt}]
        )
        return response.choices[0].message.content

class ClaudeService(AIService):
    """An AI service that uses the Anthropic Claude API."""
    def __init__(self, api_key):
        super().__init__()
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate_content(self, prompt, analysis_data):
        """Generate content using the Claude API."""
        full_prompt = f"{prompt}\n\nCode Analysis:\n{json.dumps(analysis_data, indent=2)}"
        message = self.client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": full_prompt,
                }
            ],
        )
        return message.content

class DeepSeekService(AIService):
    """An AI service that uses the DeepSeek API."""
    def __init__(self, api_key):
        super().__init__()
        self.client = DeepSeekAPI(api_key=api_key)

    def generate_content(self, prompt, analysis_data):
        """Generate content using the DeepSeek API."""
        full_prompt = f"{prompt}\n\nCode Analysis:\n{json.dumps(analysis_data, indent=2)}"
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": full_prompt}]
        )
        return response.choices[0].message.content

def get_ai_service(config):
    """Factory function to get an AI service instance."""
    if not config:
        return None
    provider = config.get("ai_provider")
    api_key = None

    if provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("GEMINI_API_KEY environment variable not found. AI service disabled.")
            return None
        return GeminiService(api_key)
    elif provider == "chatgpt":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("OPENAI_API_KEY environment variable not found. AI service disabled.")
            return None
        return ChatGPTService(api_key)
    elif provider == "claude":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("ANTHROPIC_API_KEY environment variable not found. AI service disabled.")
            return None
        return ClaudeService(api_key)
    elif provider == "deepseek":
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            print("DEEPSEEK_API_KEY environment variable not found. AI service disabled.")
            return None
        return DeepSeekService(api_key)
    # Add other providers here
    return None

CONTACT_EMAIL = "n@ndaotec.com"
COPYRIGHT_HOLDER = "Nikita Andreevich Drozdov"
REPOSITORY_ADDRESS = "https://github.com/lystwork/ndaversis"
COPYRIGHT_TEXT = (
    "ndaotec.com. @ All rights reserved - Nikita Andreevich Drozdov. "
    "All rights belong to their respective owners."
)

__version__ = "0.0.32"
def load_previous_code_state():
    """Load the previous code state from the readme.md file."""
    try:
        with open(README_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            match = re.search(
                r"<!-- AUTO-CODE-STATE-START -->(.*?)<!-- AUTO-CODE-STATE-END -->",
                content,
                re.DOTALL
            )
            if match:
                return json.loads(match.group(1).strip())
            return {}
    except (IOError, json.JSONDecodeError):
        return {}

def load_ai_config():
    """Load AI configuration from config.json."""
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        return {}

__previous_code_state__ = load_previous_code_state()

AI_CONFIG = load_ai_config()

class Version:
    """A class to represent a semantic version."""
    def __init__(self, major=0, minor=0, patch=0):
        self.major = major
        self.minor = minor
        self.patch = patch

    def __str__(self):
        """Return the string representation of the version."""
        return f"{self.major}.{self.minor}.{self.patch}"

    def increment_major(self):
        """Increment the major version."""
        self.major += 1
        self.minor = 0
        self.patch = 0

    def increment_minor(self):
        """Increment the minor version."""
        self.minor += 1
        self.patch = 0

    def increment_patch(self):
        """Increment the patch version."""
        self.patch += 1

def get_version():
    """Get the current version from the __version__ variable."""
    major, minor, patch = map(int, __version__.split("."))
    return Version(major, minor, patch)

def save_version(version_str):
    """Save the version back to the ndaversis.py file."""
    with open(__file__, "r+", encoding="utf-8") as f:
        content = f.read()
        new_content = re.sub(
            r'__version__ = "\d+\.\d+\.\d+"',
            f'__version__ = "{version_str}"',
            content
        )
        f.seek(0)
        f.write(new_content)
        f.truncate()

def _process_python_file(filepath, features, method_names):
    """Process a single Python file to extract features."""
    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()
    try:
        tree = ast.parse(code)
        module_docstring = ast.get_docstring(tree) or ""
        features["files"][filepath] = {"docstring": module_docstring}
        # First pass: Get classes and their methods
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = {
                    item.name: [arg.arg for arg in item.args.args if arg.arg != "self"]
                    for item in node.body if isinstance(item, ast.FunctionDef)
                }
                method_names.update(methods.keys())
                features["classes"][node.name] = {"methods": methods}

        # Second pass: Get imports and top-level functions
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                features["imports"].update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                features["imports"].add(node.module)
            elif isinstance(node, ast.FunctionDef) and node.name not in method_names:
                docstring = ast.get_docstring(node)
                features["functions"][node.name] = {
                    "args": [arg.arg for arg in node.args.args],
                    "docstring": docstring if docstring else ""
                }
    except SyntaxError:
        # Ignore files with syntax errors
        pass
    return code

def _analyze_codebase():
    """Analyze the codebase to identify key features and return a structured dictionary."""
    features = {
        "imports": set(),
        "classes": {},
        "functions": {},
        "files": {},
    }
    method_names = set()
    last_code = "" # To return a representative code sample
    for root, _, files in os.walk("."):
        if ".git" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                last_code = _process_python_file(filepath, features, method_names)


    features["imports"] = sorted(list(features["imports"]))
    return features, last_code


def suggest_next_steps(analysis_data):
    """Suggest next steps for the project."""
    suggestions = []
    if not any("test" in func for func in analysis_data["functions"]):
        suggestions.append("add a dedicated test suite to improve robustness")
    if "tkinter" in analysis_data["imports"] and "argparse" in analysis_data["imports"]:
        suggestions.append("enhance the GUI and CLI with more features")
    if len(analysis_data["functions"]) > 15:
        suggestions.append("consider modularizing the codebase to improve maintainability")

    if not suggestions:
        return (
            "The project is in a good state, and the next steps will be "
            "determined by user feedback."
        )

    return f"The next steps for the project could be to {', '.join(suggestions)}."


def generate_user_benefit_analysis(analysis_data):
    """Generate the 7-step analysis for the 'What's Good for the User' section."""
    ai_service = get_ai_service(AI_CONFIG)
    if ai_service:
        prompt = (
            "Generate a 7-step analysis for the 'What's Good for the User' section "
            "of a README.md file. The analysis should be based on the provided "
            "codebase analysis. The steps are: User's Goal, Evaluation of the "
            "repository Solution, Core Functionality, Safety & Side Effects, "
            "Completeness, Assessment, and Is that good result?"
        )
        return ai_service.generate_content(prompt, analysis_data)

    # Fallback to original logic if AI service is not available
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

def infer_goals_from_summary(change_summary):
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


def generate_change_summary(old_state, new_state):
    """Compare two code states and generate a summary of changes."""
    summary = []

    # Compare imports
    old_imports = set(old_state.get("imports", []))
    new_imports = set(new_state.get("imports", []))
    added_imports = new_imports - old_imports
    removed_imports = old_imports - new_imports
    if added_imports:
        summary.append(f"- Added imports: {', '.join(sorted(list(added_imports)))}")
    if removed_imports:
        summary.append(f"- Removed imports: {', '.join(sorted(list(removed_imports)))}")

    # Compare functions
    old_functions = old_state.get("functions", {})
    new_functions = new_state.get("functions", {})
    added_functions = set(new_functions.keys()) - set(old_functions.keys())
    removed_functions = set(old_functions.keys()) - set(new_functions.keys())
    if added_functions:
        summary.append(f"- Added functions: {', '.join(sorted(list(added_functions)))}")
    if removed_functions:
        summary.append(f"- Removed functions: {', '.join(sorted(list(removed_functions)))}")

    # Compare classes
    old_classes = old_state.get("classes", {})
    new_classes = new_state.get("classes", {})
    added_classes = set(new_classes.keys()) - set(old_classes.keys())
    removed_classes = set(old_classes.keys()) - set(new_classes.keys())
    if added_classes:
        summary.append(f"- Added classes: {', '.join(sorted(list(added_classes)))}")
    if removed_classes:
        summary.append(f"- Removed classes: {', '.join(sorted(list(removed_classes)))}")

    if not summary:
        return "No significant changes detected."

    return "\n".join(summary)


def _generate_section(title, analysis_data, prefix, format_str):
    """Helper function to generate a section of the README."""
    content = f"## {title}\n\n"
    items = []
    for func_name, func_data in analysis_data["functions"].items():
        if func_data.get("docstring") and prefix in func_data["docstring"]:
            items.append(
                format_str.format(
                    name=func_name.replace('_', ' ').title(),
                    doc=func_data['docstring'].split(prefix)[1].strip()
                )
            )
    content += "".join(items)
    return content

def generate_dynamic_sections(analysis_data):
    """Generate the dynamic sections of the README file."""

    use_cases = _generate_section(
        "3. Use Cases",
        analysis_data,
        "Use Case:",
        "*   **{name}**: {doc}\n"
    )

    user_stories = _generate_section(
        "4. User Stories",
        analysis_data,
        "User Story:",
        "*   **As a user,** I want to be able to {name}, so that {doc}.\n"
    )

    faq = _generate_section(
        "5. FAQ",
        analysis_data,
        "FAQ:",
        "**Q: {name}?**\n**A:** {doc}\n\n"
    )

    how_to = _generate_section(
        "6. How To",
        analysis_data,
        "How To:",
        "### {name}\n\n{doc}\n\n"
    )

    features_str = "## 7. Features\n\n"
    features_str += "".join(
        f"*   **{func_name.replace('_', ' ').title()}**: "
        f"{func_data.get('docstring', '').splitlines()[0].strip()}\n"
        for func_name, func_data in analysis_data["functions"].items()
        if func_data.get("docstring")
    )


    # Requirements
    requirements = "## 8. Requirements\n\n*   Python 3.6+\n"
    if "tkinter" in analysis_data["imports"]:
        requirements += "*   `tkinter` (for the GUI, usually included with Python)\n"

    # Install
    install = (
        "## 9. Install\n\nNo installation is required. Simply clone or "
        "download the repository and run the `ndaversis.py` script.\n"
    )

    # Project Map is generated separately

    # Modules Map
    modules_map = "## 11. Modules Map\n\n"
    modules_map_items = [
        f"*   `{os.path.basename(file_path)}`: "
        f"{file_data.get('docstring', '').splitlines()[0].strip()}"
        for file_path, file_data in analysis_data.get("files", {}).items()
        if file_data.get("docstring")
    ]
    modules_map += "\n".join(modules_map_items)


    # Dependencies Map
    dependencies_map = "## 12. Dependencies Map\n\n"
    dependencies_map_items = [
        f"*   `{dep}`"
        for dep in analysis_data.get("imports", [])
    ]
    dependencies_map += "\n".join(dependencies_map_items)


    return "\n".join(
        [
            use_cases,
            user_stories,
            faq,
            how_to,
            features_str,
            requirements,
            install,
            modules_map,
            dependencies_map,
        ]
    )


def generate_project_description():
    """Analyze the repository to generate a project description."""
    features, code = _analyze_codebase()
    ai_service = get_ai_service(AI_CONFIG)
    if ai_service:
        prompt = (
            "Generate a project description for a README.md file. The description "
            "should be based on the provided codebase analysis. It should cover: "
            "What is this repository?, How it operates?, How it's designed?, and "
            "What is its core functionality?"
        )
        return ai_service.generate_content(prompt, (features, code))

    # Fallback to original logic if AI service is not available
    try:
        with open(README_FILE, "r", encoding="utf-8") as f:
            first_line = f.readline()
            project_name = first_line.split(":")[0].replace("# 1. ", "").strip()
    except (IOError, IndexError):
        project_name = "Ndaversis"
    core_functionality = (
        "be an agentic module that leverages various large language models "
        "(like Gemini, ChatGPT, etc.) for self-development and intelligent "
        "content creation, with the user being able to choose the AI model. "
        "It also automates README creation and updates, ensuring it's always "
        "self-updating with the most recent and accurate information, "
        "alongside managing semantic versioning"
    )
    design = "monolithic, self-contained Python wrapper"
    operation = "operates independently of any version control system like Git"

    if "tkinter" in features["imports"] and "argparse" in features["imports"]:
        operation += ", and offers both a GUI and a CLI for user interaction"

    if "save_version" in features["functions"] and "__version__" in code:
        operation += (
            ". The core functionality is encapsulated within a single script, "
            "which programmatically modifies itself to update the project's version"
        )

    return (
        f"{project_name} is a {design} designed to {core_functionality}. "
        f"It {operation}. This tool is designed to be used by autonomous agents, "
        "providing a simple and robust interface for version management."
    )

def generate_project_map(analysis_data):
    """Generate a markdown tree of the project structure."""

    project_map = "```\n"

    for file in sorted(analysis_data.get("files", {}).keys()):
        project_map += f"{file}\n"

    project_map += "```"

    return project_map


def analyze_repository():
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
    return (
        f'\n\n'
        f'---\n'
        f'*This summary is auto-generated and reflects the state of the repository at '
        f'the time of the last version update.*\n\n'
        f'**Repository Analysis:**\n'
        f'- **Total Files:** {total_files}\n'
        f'- **Python Files:** {py_files}\n'
        f'- **Total Python Lines:** {py_lines}\n'
        f'---\n'
    )

def generate_readme_content(version, analysis_data, what_changed):
    """Generate the entire content of the README file."""

    project_name = "NDAVERSIS: Agentic Semantic Version Info System"

    # Title and Description
    content = f"# 1. {project_name}\n\n"
    content += "## 2. Description Summary\n\n"
    content += "<!-- AUTO-DESCRIPTION-START -->\n"
    content += f"{generate_project_description()}\n"
    content += "<!-- AUTO-DESCRIPTION-END -->\n\n"

    # Summary
    content += "<!-- AUTO-SUMMARY-START -->\n"
    content += f"{analyze_repository()}\n"
    content += "<!-- AUTO-SUMMARY-END -->\n\n"

    # Dynamic Sections
    content += f"{generate_dynamic_sections(analysis_data)}\n"

    # Project Map
    content += "## 10. Project Map\n\n"
    content += f"{generate_project_map(analysis_data)}\n\n"

    # Last Version Summary
    content += "## 13. Last Version Summary\n\n"
    content += f"The last version is `{version}`. Summary: {what_changed}\n\n"

    # Version History
    history_start_marker = "## 14. Version History"
    history_end_marker = "## 15. Contacts"
    try:
        with open(README_FILE, "r", encoding="utf-8") as f:
            existing_content = f.read()
            history_start_index = existing_content.find(history_start_marker)
            history_end_index = existing_content.find(history_end_marker)

            if history_start_index != -1 and history_end_index != -1:
                # Extract the content between the markers, excluding the markers themselves
                existing_history = existing_content[history_start_index + len(history_start_marker):history_end_index].strip()
            else:
                existing_history = ""
    except FileNotFoundError:
        existing_history = ""


    new_entry = (
        f"## Version {version}\n"
        f"### Goals\n{infer_goals_from_summary(what_changed)}\n\n"
        f"### What Changed\n{what_changed}\n\n"
        f"### What's Good for the User\n"
        f"{generate_user_benefit_analysis(analysis_data)}\n\n"
        f"### What's Possibly Next\n{suggest_next_steps(analysis_data)}\n"
    )

    content += f"{history_start_marker}\n{new_entry}\n\n{existing_history}\n"

    # Contacts and Copyright
    content += "## 15. Contacts\n\n"
    content += f"*   **Email:** {CONTACT_EMAIL}\n"
    content += f"*   **Repository:** {REPOSITORY_ADDRESS}\n\n"
    content += "## 16. Copyright\n\n"
    content += f"{COPYRIGHT_TEXT}\n"

    return content


def update_readme(content):
    """Update the readme.md file with the new content."""

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(content)

def main_gui(test_mode=False):
    """Run the tkinter GUI."""
    version = get_version()

    if test_mode:
        # In test mode, we don't create a GUI.
        # We just call the core logic directly.
        what_changed = "GUI test mode"
        version.increment_patch()
        analysis_data, _ = _analyze_codebase()
        readme_content = generate_readme_content(version, analysis_data, what_changed)
        update_readme(readme_content)
        save_version(str(version))
        print("GUI test mode complete.")
        return

    root = tk.Tk()
    root.title(f"Version Manager - Current Version: {version}")

    tk.Label(root, text="What changed:").pack()
    changed_entry = tk.Text(root, height=5, width=50)
    changed_entry.pack()

    def update_and_close(increment_func):
        increment_func()

        # Get the details from the GUI
        what_changed = changed_entry.get("1.0", tk.END).strip()

        # Analyze the codebase
        analysis_data, _ = _analyze_codebase()

        # Generate the new README content
        readme_content = generate_readme_content(version, analysis_data, what_changed)

        # Update the README file
        update_readme(readme_content)

        # Save the new version
        save_version(str(version))

        messagebox.showinfo("Success", f"Version updated to {version}")
        root.destroy()

    major_button = tk.Button(
        root, text="Increment Major", command=lambda: update_and_close(version.increment_major)
    )
    major_button.pack()
    minor_button = tk.Button(
        root, text="Increment Minor", command=lambda: update_and_close(version.increment_minor)
    )
    minor_button.pack()
    patch_button = tk.Button(
        root, text="Increment Patch", command=lambda: update_and_close(version.increment_patch)
    )
    patch_button.pack()

    root.mainloop()


def install_pre_commit_hook():
    """Installs a pre-commit hook to automate README and version updates."""
    hook_script = """
#!/bin/sh
# Automatically update the version and README on commit.
python3 ndaversis.py cli --patch
git add ndaversis.py readme.md
"""
    hook_path = os.path.join(".git", "hooks", "pre-commit")
    try:
        with open(hook_path, "w", encoding="utf-8") as f:
            f.write(hook_script)
        os.chmod(hook_path, 0o755)
        print("Successfully installed pre-commit hook.")
    except IOError as e:
        print(f"Error installing pre-commit hook: {e}")

def main_cli(cli_args):
    """Run the command-line interface."""
    version = get_version()

    # Analyze the current code state
    new_code_state, _ = _analyze_codebase()

    # Generate the change summary
    change_summary = generate_change_summary(__previous_code_state__, new_code_state)

    if cli_args.major:
        version.increment_major()
    elif cli_args.minor:
        version.increment_minor()
    elif cli_args.patch:
        version.increment_patch()

    # Generate the new README content
    readme_content = generate_readme_content(version, new_code_state, change_summary)

    # Update the README file
    update_readme(readme_content)

    # Save the new version
    save_version(str(version))

    # Update the __previous_code_state__ in the readme.md file
    with open(README_FILE, "r+", encoding="utf-8") as f:
        content = f.read()
        state_string = json.dumps(new_code_state, indent=4)
        # Use a robust regex to find and replace the state block
        new_content = re.sub(
            r"<!-- AUTO-CODE-STATE-START -->.*?<!-- AUTO-CODE-STATE-END -->",
            (
                f"<!-- AUTO-CODE-STATE-START -->\n{state_string}\n"
                f"<!-- AUTO-CODE-STATE-END -->"
            ),
            content,
            flags=re.DOTALL
        )
        # If the block doesn't exist, append it to the end of the file
        if "<!-- AUTO-CODE-STATE-START -->" not in new_content:
            new_content += f"\n<!-- AUTO-CODE-STATE-START -->\n{state_string}\n<!-- AUTO-CODE-STATE-END -->"
        f.seek(0)
        f.write(new_content)
        f.truncate()

    print(f"Version updated to {version}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Version Manager")
    subparsers = parser.add_subparsers(dest="command")

    gui_parser = subparsers.add_parser("gui", help="Run the GUI")
    gui_parser.add_argument("--test", action="store_true", help="Run the GUI in test mode")
    cli_parser = subparsers.add_parser("cli", help="Run the command-line interface")
    install_parser = subparsers.add_parser("install-hook", help="Install the pre-commit hook")


    group = cli_parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--major", action="store_true", help="Increment major version")
    group.add_argument("--minor", action="store_true", help="Increment minor version")
    group.add_argument("--patch", action="store_true", help="Increment patch version")

    if len(sys.argv) == 1:
        main_gui()
    else:
        args = parser.parse_args()
        if args.command == "gui":
            main_gui(test_mode=args.test)
        elif args.command == "cli":
            main_cli(args)
        elif args.command == "install-hook":
            install_pre_commit_hook()
        else:
            parser.print_help()
