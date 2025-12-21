"""A module for managing semantic versioning."""
import os
import re
import tkinter as tk
from tkinter import messagebox
import argparse
import sys

__version__ = "0.0.13"

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
    # 1. What is this "Name of repository"?
    try:
        with open("readme.md", "r", encoding="utf-8") as f:
            first_line = f.readline()
            project_name = first_line.split(":")[0].replace("# 1. ", "").strip()
    except (IOError, IndexError):
        project_name = "Ndaversis"

    # 2. How it operates? 3. How its designed? 4. What its core functionality?
    with open(__file__, "r", encoding="utf-8") as f:
        code = f.read()

    core_functionality = "manage semantic versioning for software projects"
    design = "monolithic, self-contained Python wrapper"
    operation = "operates independently of any version control system like Git"

    if "import tkinter" in code and "import argparse" in code:
        operation += ", and offers both a GUI and a CLI for user interaction"

    if "f.write(new_content)" in code and "__version__" in code:
        operation += ". The core functionality is encapsulated within a single script, which programmatically modifies itself to update the project's version"

    return (
        f"{project_name} is a {design} designed to {core_functionality}. "
        f"It {operation}. This tool is designed to be used by autonomous agents, "
        f"providing a simple and robust interface for version management."
    )

def analyze_repository():
    """Analyze the repository to generate a summary."""
    total_files = 0
    py_files = 0
    py_lines = 0
    for root, dirs, files in os.walk("."):
        # Exclude the .git directory
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
                    # Ignore files that can't be read
                    pass

    return (
        f'\n\n'
        f'---\n'
        f'*This summary is auto-generated and reflects the state of the repository at the time of the last version update.*\n\n'
        f'**Repository Analysis:**\n'
        f'- **Total Files:** {total_files}\n'
        f'- **Python Files:** {py_files}\n'
        f'- **Total Python Lines:** {py_lines}\n'
        f'---\n'
    )


def update_readme(version, summary):
    """Update the readme.md file with the new version and summary."""
    with open("readme.md", "r", encoding="utf-8") as f:
        content = f.read()

    version_str = str(version)
    version_line = f"## Version {version_str}"

    # Check for duplicates first
    if version_line in content:
        print(f"Version {version_str} already exists in readme.md. Skipping.")
        return

    # Update "Description Summary" with auto-generated analysis
    description = generate_project_description()
    analysis_summary = analyze_repository()

    # Define the markers for the auto-generated blocks
    desc_start_marker = "<!-- AUTO-DESCRIPTION-START -->"
    desc_end_marker = "<!-- AUTO-DESCRIPTION-END -->"
    summary_start_marker = "<!-- AUTO-SUMMARY-START -->"
    summary_end_marker = "<!-- AUTO-SUMMARY-END -->"

    # Replace the content between the markers
    content = re.sub(
        f"({desc_start_marker})(.*?)({desc_end_marker})",
        f"\\1\n{description}\n\\3",
        content,
        flags=re.DOTALL
    )
    content = re.sub(
        f"({summary_start_marker})(.*?)({summary_end_marker})",
        f"\\1{analysis_summary}\\3",
        content,
        flags=re.DOTALL
    )

    # Update "Last Version Summary"
    new_summary_text = f"\nThe last version is `{version_str}`. Summary: {summary}\n"
    content = re.sub(
        r"(?<=## 13\. Last Version Summary\n).*?(?=## 14\. Version History)",
        new_summary_text,
        content,
        flags=re.DOTALL
    )

    # Update "Version History"
    version_history_heading = "## 14. Version History"
    new_version_entry = f"## Version {version_str}\n{summary}"
    content = content.replace(
        version_history_heading,
        f"{version_history_heading}\n\n{new_version_entry}"
    )

    with open("readme.md", "w", encoding="utf-8") as f:
        f.write(content)


def main_gui():
    """Run the tkinter GUI."""
    version = get_version()

    def update_and_close(increment_func):
        increment_func()
        summary = summary_entry.get("1.0", tk.END).strip()
        save_version(version)
        update_readme(version, summary)
        messagebox.showinfo("Success", f"Version updated to {version}")
        root.destroy()

    root = tk.Tk()
    root.title(f"Version Manager - Current Version: {version}")

    tk.Label(root, text="Summary of changes:").pack()
    summary_entry = tk.Text(root, height=5, width=50)
    summary_entry.pack()

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

def main_cli(args):
    """Run the command-line interface."""
    version = get_version()

    if args.major:
        version.increment_major()
    elif args.minor:
        version.increment_minor()
    elif args.patch:
        version.increment_patch()

    summary = args.summary if args.summary else "No summary provided."
    save_version(version)
    update_readme(version, summary)
    print(f"Version updated to {version}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Version Manager")
    subparsers = parser.add_subparsers(dest="command")

    # GUI subparser
    gui_parser = subparsers.add_parser("gui", help="Run the GUI")

    # CLI subparser
    cli_parser = subparsers.add_parser("cli", help="Run the command-line interface")
    group = cli_parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--major", action="store_true", help="Increment major version")
    group.add_argument("--minor", action="store_true", help="Increment minor version")
    group.add_argument("--patch", action="store_true", help="Increment patch version")
    cli_parser.add_argument("--summary", type=str, help="Summary of changes")

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
