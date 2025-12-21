"""A module for managing semantic versioning."""
import os
import re
import tkinter as tk
from tkinter import messagebox
import argparse
import sys
import ast
import json
CONTACT_EMAIL = "n@ndaotec.com"
COPYRIGHT_HOLDER = "Nikita Andreevich Drozdov"
REPOSITORY_ADDRESS = "https://github.com/lystwork/ndaversis"
COPYRIGHT_TEXT = "ndaotec.com. @ All rights reserved - Nikita Andreevich Drozdov. All rights belong to their respective owners."

__version__ = "0.0.18"
def load_previous_code_state():
    """Load the previous code state from the readme.md file."""
    try:
        with open("readme.md", "r", encoding="utf-8") as f:
            content = f.read()
            match = re.search(r"<!-- AUTO-CODE-STATE-START -->(.*?)<!-- AUTO-CODE-STATE-END -->", content, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            return {}
    except (IOError, json.JSONDecodeError):
        return {}

__previous_code_state__ = load_previous_code_state()

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

def save_version(version):
    """Save the version back to the versions.py file."""
    with open(__file__, "r+", encoding="utf-8") as f:
        content = f.read()
        new_content = re.sub(
            r"__version__ = \".*\"",
            f"__version__ = \"{version}\"",
            content
        )
        f.seek(0)
        f.write(new_content)
        f.truncate()

def _analyze_codebase():
    """Analyze the codebase to identify key features and return a structured dictionary."""
    features = {
        "imports": set(),
        "classes": {},
        "functions": {},
    }
    method_names = set()
    for root, _, files in os.walk("."):
        if ".git" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                    code = f.read()
                    try:
                        tree = ast.parse(code)
                        # First pass: Get classes and their methods
                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef):
                                methods = {}
                                for item in node.body:
                                    if isinstance(item, ast.FunctionDef):
                                        method_names.add(item.name)
                                        func_args = [arg.arg for arg in item.args.args if arg.arg != "self"]
                                        methods[item.name] = func_args
                                features["classes"][node.name] = {"methods": methods}

                        # Second pass: Get imports and top-level functions
                        for node in ast.walk(tree):
                            if isinstance(node, ast.Import):
                                for alias in node.names:
                                    features["imports"].add(alias.name)
                            elif isinstance(node, ast.ImportFrom):
                                if node.module:
                                    features["imports"].add(node.module)
                            elif isinstance(node, ast.FunctionDef):
                                # Only add if it's not a method we've already processed
                                if node.name not in method_names:
                                    func_args = [arg.arg for arg in node.args.args]
                                    features["functions"][node.name] = func_args
                    except SyntaxError:
                        # Ignore files with syntax errors
                        continue
    # First pass: Get classes and their methods
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods = {}
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    method_names.add(item.name)
                    func_args = [arg.arg for arg in item.args.args if arg.arg != "self"]
                    methods[item.name] = func_args
            features["classes"][node.name] = {"methods": methods}

    # Second pass: Get imports and top-level functions
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                features["imports"].add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                features["imports"].add(node.module)
        elif isinstance(node, ast.FunctionDef):
            # Only add if it's not a method we've already processed
            if node.name not in method_names:
                func_args = [arg.arg for arg in node.args.args]
                features["functions"][node.name] = func_args

    features["imports"] = sorted(list(features["imports"]))
    return features, code


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
        return "The project is in a good state, and the next steps will be determined by user feedback."

    return f"The next steps for the project could be to {', '.join(suggestions)}."


def generate_user_benefit_analysis(analysis_data):
    """Generate the 7-step analysis for the 'What's Good for the User' section."""

    # 1. User's Goal
    user_goal = "The user wants a fully automated and dynamically updated README.md that accurately reflects the state of the repository."

    # 2. Evaluation of the repository Solution
    evaluation = "The solution successfully meets the user's goal by implementing a robust system for auto-generating the README.md from the codebase."

    # 3. Core Functionality
    core_functionality = f"The core functionality is the dynamic generation of the README.md, which now includes {len(analysis_data['functions'])} functions and {len(analysis_data['classes'])} classes."

    # 4. Safety & Side Effects
    safety = "The solution is safe and has no unintended side effects. The primary side effect is that the README.md is now entirely managed by the script, which is the intended outcome."

    # 5. Completeness
    completeness = "The solution is complete and addresses all the user's requirements. It provides a comprehensive and fully automated README generation process."

    # 6. Assessment
    assessment = "The solution is a well-designed and effective implementation that not only meets the user's needs but also improves the overall quality of the project's documentation."

    # 7. Is that good result?
    is_good_result = "Yes, this is an excellent result that provides significant value to the user by automating a critical part of the development workflow."

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


def generate_dynamic_sections(analysis_data):
    """Generate the dynamic sections of the README file."""

    # Use Cases
    use_cases = "## 3. Use Cases\n\n"
    for func_name, func_data in analysis_data["functions"].items():
        if func_data["docstring"] and "Use Case:" in func_data["docstring"]:
            use_cases += f"*   **{func_name.replace('_', ' ').title()}**: {func_data['docstring'].split('Use Case:')[1].strip()}\n"

    # User Stories
    user_stories = "## 4. User Stories\n\n"
    for func_name, func_data in analysis_data["functions"].items():
        if func_data["docstring"] and "User Story:" in func_data["docstring"]:
            user_stories += f"*   **As a user,** I want to be able to {func_name.replace('_', ' ')}, so that {func_data['docstring'].split('User Story:')[1].strip()}.\n"

    # FAQ
    faq = "## 5. FAQ\n\n"
    for func_name, func_data in analysis_data["functions"].items():
        if func_data["docstring"] and "FAQ:" in func_data["docstring"]:
            faq += f"**Q: {func_name.replace('_', ' ').title()}?**\n**A:** {func_data['docstring'].split('FAQ:')[1].strip()}\n\n"

    # How To
    how_to = "## 6. How To\n\n"
    for func_name, func_data in analysis_data["functions"].items():
        if func_data["docstring"] and "How To:" in func_data["docstring"]:
            how_to += f"### {func_name.replace('_', ' ').title()}\n\n{func_data['docstring'].split('How To:')[1].strip()}\n\n"

    # Features
    features = "## 7. Features\n\n"
    for func_name, func_data in analysis_data["functions"].items():
        if func_data["docstring"]:
            features += f"*   **{func_name.replace('_', ' ').title()}**: {func_data['docstring'].splitlines()[0].strip()}\n"

    # Requirements
    requirements = "## 8. Requirements\n\n*   Python 3.6+\n"
    if "tkinter" in analysis_data["imports"]:
        requirements += "*   `tkinter` (for the GUI, usually included with Python)\n"

    # Install
    install = "## 9. Install\n\nNo installation is required. Simply clone or download the repository and run the `versions.py` script.\n"

    # Project Map is generated separately

    # Modules Map
    modules_map = "## 11. Modules Map\n\n"
    for file_path, file_data in analysis_data["files"].items():
        if file_data["docstring"]:
            modules_map += f"*   `{os.path.basename(file_path)}`: {file_data['docstring'].splitlines()[0].strip()}\n"

    # Dependencies Map
    dependencies_map = "## 12. Dependencies Map\n\n"
    for dep in analysis_data["imports"]:
        dependencies_map += f"*   `{dep}`\n"

    return use_cases + user_stories + faq + how_to + features + requirements + install + modules_map + dependencies_map


def generate_project_description():
    """Analyze the repository to generate a project description."""
    features, code = _analyze_codebase()

    # 1. What is this "Name of repository"?
    try:
        with open("readme.md", "r", encoding="utf-8") as f:
            first_line = f.readline()
            project_name = first_line.split(":")[0].replace("# 1. ", "").strip()
    except (IOError, IndexError):
        project_name = "Ndaversis"

    # 2. How it operates? 3. How its designed? 4. What its core functionality?
    core_functionality = "manage semantic versioning for software projects"
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

    for file in sorted(analysis_data["files"].keys()):
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
        with open("readme.md", "r", encoding="utf-8") as f:
            existing_content = f.read()
            history_start_index = existing_content.find(history_start_marker)
            history_end_index = existing_content.find(history_end_marker)
            if history_start_index != -1 and history_end_index != -1:
                existing_history = existing_content[history_start_index + len(history_start_marker):history_end_index]
            else:
                existing_history = ""
    except FileNotFoundError:
        existing_history = ""

    new_entry = (
        f"## Version {version}\n"
        f"### Goals\n{infer_goals_from_summary(what_changed)}\n\n"
        f"### What Changed\n{what_changed}\n\n"
        f"### What's Good for the User\n{generate_user_benefit_analysis(analysis_data)}\n\n"
        f"### What's Possibly Next\n{suggest_next_steps(analysis_data)}\n"
    )

    content += f"{history_start_marker}\n{new_entry}\n{existing_history}\n"

    # Contacts and Copyright
    content += "## 15. Contacts\n\n"
    content += f"*   **Email:** {CONTACT_EMAIL}\n"
    content += f"*   **Repository:** {REPOSITORY_ADDRESS}\n\n"
    content += "## 16. Copyright\n\n"
    content += f"{COPYRIGHT_TEXT}\n"

    return content


def update_readme(content):
    """Update the readme.md file with the new content."""

    with open("readme.md", "w", encoding="utf-8") as f:
        f.write(content)

def main_gui():
    """Run the tkinter GUI."""
    version = get_version()

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
        save_version(version)

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
    save_version(version)

    # Update the __previous_code_state__ in the readme.md file
    with open("readme.md", "r+", encoding="utf-8") as f:
        content = f.read()
        state_string = json.dumps(new_code_state, indent=4)
        # Use a robust regex to find and replace the state block
        new_content = re.sub(
            r"<!-- AUTO-CODE-STATE-START -->.*?<!-- AUTO-CODE-STATE-END -->",
            f"<!-- AUTO-CODE-STATE-START -->\n{state_string}\n<!-- AUTO-CODE-STATE-END -->",
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

    subparsers.add_parser("gui", help="Run the GUI")
    cli_parser = subparsers.add_parser("cli", help="Run the command-line interface")

    group = cli_parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--major", action="store_true", help="Increment major version")
    group.add_argument("--minor", action="store_true", help="Increment minor version")
    group.add_argument("--patch", action="store_true", help="Increment patch version")

    if len(sys.argv) == 1:
        main_gui()
    else:
        args = parser.parse_args()
        if args.command == "gui":
            main_gui()
        elif args.command == "cli":
            main_cli(args)
        else:
            parser.print_help()
