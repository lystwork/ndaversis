"""A module for managing semantic versioning."""
import os
import re
import tkinter as tk
from tkinter import messagebox
import argparse

__version__ = "0.0.1"

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

def update_readme(version, summary):
    """Update the readme.md file with the new version and summary."""
    with open("readme.md", "r", encoding="utf-8") as f:
        content = f.read()

    version_str = str(version)
    version_line = f"## Version {version_str}"

    if version_line in content:
        # Version already exists, so we don't do anything
        print(f"Version {version_str} already exists in readme.md. Skipping.")
        return

    # Add the new version and summary
    new_content = content + f"\n{version_line}\n\n{summary}\n"

    with open("readme.md", "w", encoding="utf-8") as f:
        f.write(new_content)


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

def main_cli():
    """Run the command-line interface."""
    parser = argparse.ArgumentParser(description="Version Manager")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--major", action="store_true", help="Increment major version")
    group.add_argument("--minor", action="store_true", help="Increment minor version")
    group.add_argument("--patch", action="store_true", help="Increment patch version")
    parser.add_argument("--summary", type=str, help="Summary of changes")
    args = parser.parse_args()

    version = get_version()

    if args.major:
        version.increment_major()
    elif args.minor:
        version.increment_minor()
    elif args.patch:
        version.increment_patch()
    else:
        print("No version increment specified. Use --major, --minor, or --patch")
        return

    summary = args.summary if args.summary else "No summary provided."
    save_version(version)
    update_readme(version, summary)
    print(f"Version updated to {version}")


if __name__ == "__main__":
    main_parser = argparse.ArgumentParser(description="Version Manager")
    main_parser.add_argument("--gui", action="store_true", help="Run the GUI")
    main_args, unknown = main_parser.parse_known_args()

    if main_args.gui:
        main_gui()
    else:
        main_cli()
