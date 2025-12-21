"""A module for managing semantic versioning."""
import os
import re
import tkinter as tk
from tkinter import messagebox
import argparse
import sys
import ast
import json

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

def update_readme(version, goals, what_changed, what_good_for_user, what_possibly_next):
    """Update the readme.md file with the new version and details."""
    with open("readme.md", "r", encoding="utf-8") as f:
        content = f.read()

    version_str = str(version)
    if f"## Version {version_str}" in content:
        print(f"Version {version_str} already exists in readme.md. Skipping.")
        return

    description = generate_project_description()
    analysis_summary = analyze_repository()

    desc_markers = ("<!-- AUTO-DESCRIPTION-START -->", "<!-- AUTO-DESCRIPTION-END -->")
    summary_markers = ("<!-- AUTO-SUMMARY-START -->", "<!-- AUTO-SUMMARY-END -->")

    content = re.sub(
        f"({desc_markers[0]})(.*?)({desc_markers[1]})",
        f"\\1\n{description}\n\\3", content, flags=re.DOTALL
    )
    content = re.sub(
        f"({summary_markers[0]})(.*?)({summary_markers[1]})",
        f"\\1{analysis_summary}\\3", content, flags=re.DOTALL
    )

    summary_text = f"\nThe last version is `{version_str}`. Summary: {what_changed}\n"
    content = re.sub(
        r"(?<=## 13\. Last Version Summary\n)(.|\n)*?(?=## 14\. Version History)",
        summary_text, content, flags=re.DOTALL
    )

    history_heading = "## 14. Version History"
    new_entry = (
        f"## Version {version_str}\n"
        f"### Goals\n{goals}\n\n"
        f"### What Changed\n{what_changed}\n\n"
        f"### What's Good for the User\n{what_good_for_user}\n\n"
        f"### What's Possibly Next\n{what_possibly_next}"
    )
    content = content.replace(history_heading, f"{history_heading}\n\n{new_entry}")

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
        details = {
            "goals": goals_entry.get("1.0", tk.END).strip(),
            "what_changed": changed_entry.get("1.0", tk.END).strip(),
            "what_good_for_user": user_benefit_entry.get("1.0", tk.END).strip(),
            "what_possibly_next": next_steps_entry.get("1.0", tk.END).strip()
        }
        save_version(version)
        update_readme(version, **details)
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

    details = {
        "goals": "Auto-generated update.",
        "what_changed": change_summary,
        "what_good_for_user": "Automated and accurate changelog.",
        "what_possibly_next": "Further automation.",
    }

    save_version(version)
    update_readme(version, **details)

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
