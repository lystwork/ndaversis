"""A module for managing semantic versioning."""
import os
import re
import tkinter as tk
from tkinter import messagebox
import argparse
import sys

__version__ = "0.0.14"

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

def generate_project_description():
    """Analyze the repository to generate a project description."""
    try:
        with open("readme.md", "r", encoding="utf-8") as f:
            first_line = f.readline()
            project_name = first_line.split(":")[0].replace("# 1. ", "").strip()
    except (IOError, IndexError):
        project_name = "Ndaversis"

    with open(__file__, "r", encoding="utf-8") as f:
        code = f.read()

    core_functionality = "manage semantic versioning for software projects"
    design = "monolithic, self-contained Python wrapper"
    operation = "operates independently of any version control system like Git"

    if "import tkinter" in code and "import argparse" in code:
        operation += ", and offers both a GUI and a CLI for user interaction"

    if "f.write(new_content)" in code and "__version__" in code:
        operation += (
            ". The core functionality is encapsulated within a single script, "
            "which programmatically modifies itself to update the project's version"
        )

    return (
        f"{project_name} is a {design} designed to {core_functionality}. "
        f"It {operation}. This tool is designed to be used by autonomous agents, "
        f"providing a simple and robust interface for version management."
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
        f'\n\n---\n'
        f'*This summary is auto-generated and reflects the state of the repository '
        f'at the time of the last version update.*\n\n'
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
        r"(?<=## 13\. Last Version Summary\n).*?(?=## 14\. Version History)",
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

    if cli_args.major:
        version.increment_major()
    elif cli_args.minor:
        version.increment_minor()
    elif cli_args.patch:
        version.increment_patch()

    details = {
        "goals": cli_args.goals or "No goals provided.",
        "what_changed": cli_args.changed or "No changes specified.",
        "what_good_for_user": cli_args.user_benefit or "No user benefits specified.",
        "what_possibly_next": cli_args.next_steps or "No next steps specified."
    }
    save_version(version)
    update_readme(version, **details)
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

    cli_parser.add_argument("--goals", type=str, help="Goals for this version.")
    cli_parser.add_argument("--changed", type=str, help="What changed in this version.")
    cli_parser.add_argument("--user-benefit", type=str, help="What is good for the user.")
    cli_parser.add_argument("--next-steps", type=str, help="What are the next steps.")

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
