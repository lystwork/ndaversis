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
        "files": {},
    }

    for root, _, files in os.walk("."):
        if ".git" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                with open(filepath, "r", encoding="utf-8") as f:
                    code = f.read()
                    try:
                        tree = ast.parse(code)

                        # Get module-level docstring
                        module_docstring = ast.get_docstring(tree)
                        features["files"][filepath] = {"docstring": module_docstring}

                        # Traverse the AST
                        for node in ast.walk(tree):
                            # Get imports
                            if isinstance(node, ast.Import):
                                for alias in node.names:
                                    features["imports"].add(alias.name)
                            elif isinstance(node, ast.ImportFrom):
                                if node.module:
                                    features["imports"].add(node.module)

                            # Get classes and their methods
                            elif isinstance(node, ast.ClassDef):
                                class_docstring = ast.get_docstring(node)
                                methods = {}
                                for item in node.body:
                                    if isinstance(item, ast.FunctionDef):
                                        method_docstring = ast.get_docstring(item)
                                        func_args = [arg.arg for arg in item.args.args if arg.arg != "self"]
                                        methods[item.name] = {"args": func_args, "docstring": method_docstring}
                                features["classes"][node.name] = {"docstring": class_docstring, "methods": methods}

                            # Get top-level functions
                            elif isinstance(node, ast.FunctionDef) and not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree) if hasattr(parent, 'body') and node in parent.body):
                                func_docstring = ast.get_docstring(node)
                                func_args = [arg.arg for arg in node.args.args]
                                features["functions"][node.name] = {"args": func_args, "docstring": func_docstring}

                    except SyntaxError:
                        # Ignore files with syntax errors
                        continue

    features["imports"] = sorted(list(features["imports"]))
    return features, code


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


def generate_project_map(analysis_data):
    """Generate a markdown tree of the project structure."""

    project_map = "```\n"

    for file in sorted(analysis_data["files"].keys()):
        project_map += f"{file}\n"

    project_map += "```"

    return project_map


def generate_readme_content(version, analysis_data, goals, what_changed, what_good_for_user, what_possibly_next):
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
    content += "## 14. Version History\n\n"
    content += f"## Version {version}\n"
    content += f"### Goals\n{goals}\n\n"
    content += f"### What Changed\n{what_changed}\n\n"
    content += f"### What's Good for the User\n{what_good_for_user}\n\n"
    content += f"### What's Possibly Next\n{what_possibly_next}\n\n"

    # Contacts and Copyright
    content += "## 15. Contacts\n\n"
    content += f"*   **Email:** {CONTACT_EMAIL}\n"
    content += f"*   **Repository:** {REPOSITORY_ADDRESS}\n\n"
    content += "## 16. Copyright\n\n"
    content += f"{COPYRIGHT_TEXT}\n"

    return content

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

def update_readme(content):
    """Update the readme.md file with the new content."""

    with open("readme.md", "w", encoding="utf-8") as f:
        f.write(content)

def main_gui():
    """Run the tkinter GUI."""
    version = get_version()

    root = tk.Tk()
    root.title(f"Version Manager - Current Version: {version}")

    tk.Label(root, text="Goals:").pack()
    goals_entry = tk.Text(root, height=3, width=50)
    goals_entry.pack()

    tk.Label(root, text="What changed:").pack()
    changed_entry = tk.Text(root, height=5, width=50)
    changed_entry.pack()

    tk.Label(root, text="What's good for the user:").pack()
    user_benefit_entry = tk.Text(root, height=3, width=50)
    user_benefit_entry.pack()

    tk.Label(root, text="What's possibly next:").pack()
    next_steps_entry = tk.Text(root, height=3, width=50)
    next_steps_entry.pack()

    def update_and_close(increment_func):
        increment_func()

        # Get the details from the GUI
        goals = goals_entry.get("1.0", tk.END).strip()
        what_changed = changed_entry.get("1.0", tk.END).strip()
        what_good_for_user = user_benefit_entry.get("1.0", tk.END).strip()
        what_possibly_next = next_steps_entry.get("1.0", tk.END).strip()

        # Analyze the codebase
        analysis_data, _ = _analyze_codebase()

        # Generate the new README content
        readme_content = generate_readme_content(version, analysis_data, goals, what_changed, what_good_for_user, what_possibly_next)

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

    # Set the details for the README
    goals = "Auto-generated update."
    what_good_for_user = "Automated and accurate changelog."
    what_possibly_next = "Further automation."

    # Generate the new README content
    readme_content = generate_readme_content(version, new_code_state, goals, change_summary, what_good_for_user, what_possibly_next)

    # Update the README file
    update_readme(readme_content)

    # Save the new version
    save_version(version)

    # Update the __previous_code_state__ in the versions.py file
    with open(__file__, "r+", encoding="utf-8") as f:
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
