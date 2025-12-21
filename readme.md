# 1. NDAVERSIS: Agentic Semantic Version Info System

## 2. Description Summary

<!-- AUTO-DESCRIPTION-START -->
NDAVERSIS is a monolithic, self-contained Python wrapper designed to manage semantic versioning for software projects. It operates independently of any version control system like Git, and offers both a GUI and a CLI for user interaction. This tool is designed to be used by autonomous agents, providing a simple and robust interface for version management.
<!-- AUTO-DESCRIPTION-END -->

---
<!-- AUTO-SUMMARY-START -->

---
*This summary is auto-generated and reflects the state of the repository at the time of the last version update.*

**Repository Analysis:**
- **Total Files:** 6
- **Python Files:** 3
- **Total Python Lines:** 417
---
<!-- AUTO-SUMMARY-END -->

## 3. Use Cases
*   **Git-Independent Projects:** Ideal for projects where versioning is needed but Git is not used, such as in certain CI/CD pipelines or for projects managed outside of traditional version control.
*   **Agent-Driven Development:** Provides a simple and reliable way for autonomous agents to manage software versions without needing to interact with a complex version control system.
*   **Simplified Changelog Management:** Automatically generates a clear and consistent changelog in the `readme.md` file, reducing the manual effort required to maintain one.

## 4. User Stories
*   **As a developer,** I want to be able to increment the version of my project with a single command, so that I can easily manage releases without needing to manually update multiple files.
*   **As an autonomous agent,** I need a simple and reliable way to update the project version, so that I can programmatically manage software releases as part of my development workflow.
*   **As a project manager,** I want a clear and up-to-date changelog, so that I can easily track the history of changes and new features in the project.

## 5. FAQ
**Q: Why is the version stored in the `versions.py` file itself?**
**A:** This is a core design feature that makes the versioning system entirely self-contained and independent of any version control system. It allows the script to manage the version without any external dependencies.

**Q: Can I use this with Git?**
**A:** Yes, you can. However, the versioning system is designed to be independent of Git. If you use it with Git, you will need to commit the changes to `versions.py` and `readme.md` after each version update.

**Q: Is it safe for the script to modify itself?**
**A:** While self-modifying code can be risky, the implementation in `versions.py` is designed to be as safe as possible. It uses a specific regular expression to target only the `__version__` variable, minimizing the risk of accidental damage.

## 6. How To
### Increment the Version
You can increment the version using the command-line interface (CLI) or the graphical user interface (GUI).

**Using the CLI:**
```bash
python3 versions.py cli --[major|minor|patch] --summary "Your summary of changes"
```
*   `--major`: Increments the MAJOR version (e.g., `1.0.0` -> `2.0.0`).
*   `--minor`: Increments the MINOR version (e.g., `1.1.0` -> `1.2.0`).
*   `--patch`: Increments the PATCH version (e.g., `1.1.1` -> `1.1.2`).

**Using the GUI:**
```bash
python3 versions.py gui
```
This will open a simple graphical interface where you can enter a summary of changes and click a button to increment the desired version.

## 7. Features
*   **Git-Independent Versioning:** The project version is stored directly within the `versions.py` script.
*   **Semantic Versioning 2.0.0:** Adheres to the SemVer 2.0.0 standard.
*   **Automatic Changelog Generation:** Automatically updates this `readme.md` file with a new version entry and a summary of changes.
*   **Dual Interface:** Provides both a CLI and a GUI.
*   **Monolithic Design:** All core logic is contained within a single Python file.

## 8. Requirements
*   Python 3.6+
*   `tkinter` (for the GUI, usually included with Python)

## 9. Install
No installation is required. Simply clone or download the repository and run the `versions.py` script.

## 10. Project Map
```
.
├── copyright.py
├── readme.md
├── versions.py
└── versions_testing
    ├── dummy_readme.md
    └── dummycode.py
```

## 11. Modules Map
*   `versions.py`: The core module, containing all the logic for version management.
*   `copyright.py`: A simple module containing copyright and contact information.

## 12. Dependencies Map
*   `os`: Used for file system operations.
*   `re`: Used for regular expressions (for self-modification).
*   `tkinter`: Used for the GUI.
*   `argparse`: Used for the CLI.

## 13. Last Version Summary

The last version is `0.0.18`. Summary: - Added imports: argparse, ast, json, os, re, sys, tkinter
- Added functions: _analyze_codebase, analyze_repository, generate_change_summary, generate_project_description, get_version, hello_world, load_previous_code_state, main_cli, main_gui, save_version, update_and_close, update_readme
- Added classes: Version
## 14. Version History

## Version 0.0.18
### Goals
Auto-generated update.

### What Changed
- Added imports: argparse, ast, json, os, re, sys, tkinter
- Added functions: _analyze_codebase, analyze_repository, generate_change_summary, generate_project_description, get_version, hello_world, load_previous_code_state, main_cli, main_gui, save_version, update_and_close, update_readme
- Added classes: Version

### What's Good for the User
Automated and accurate changelog.

### What's Possibly Next
Further automation.

## Version 0.0.17
### Goals
Auto-generated update.

### What Changed
- Added imports: json
- Added functions: generate_change_summary, load_previous_code_state, update_and_close

### What's Good for the User
Automated and accurate changelog.

### What's Possibly Next
Further automation.

## Version 0.0.16
### Goals
Auto-generated update.

### What Changed
- Added functions: generate_change_summary, update_and_close

### What's Good for the User
Automated and accurate changelog.

### What's Possibly Next
Further automation.

## Version 0.0.15
### Goals
Auto-generated update.

### What Changed
- Added imports: argparse, ast, os, re, sys, tkinter
- Added functions: _analyze_codebase, analyze_repository, generate_change_summary, generate_project_description, get_version, main_cli, main_gui, save_version, update_readme
- Added classes: Version

### What's Good for the User
Automated and accurate changelog.

### What's Possibly Next
Further automation.

## Version 0.0.14
### Goals
Test goal

### What Changed
Test change

### What's Good for the User
Test benefit

### What's Possibly Next
Test next

## Version 0.0.13
Test dynamic description

## Version 0.0.12
Test corrected file counts

## Version 0.0.11
Test marker-based insertion

## Version 0.0.10
Final test of formatting

## Version 0.0.9
Test final formatting

## Version 0.0.8
Test reordered summary

## Version 0.0.7
Test final regex

## Version 0.0.6
Test corrected formatting

## Version 0.0.5
Test auto-summary

## Version 0.0.4
Testing robust regex

## Version 0.0.3
This is a multi-line
summary to test the new regex.
It should be fully captured.

## Version 0.0.2
Updated readme generation
## Version 0.0.1
Initial version.

## 15. Contacts
*   **Email:** n@ndaotec.com
*   **Repository:** https://github.com/lystwork/ndaversis

## 16. Copyright
ndaotec.com. @ All rights reserved - Nikita Andreevich Drozdov. All rights belong to their respective owners.

<!-- AUTO-CODE-STATE-START -->
{
    "imports": [
        "argparse",
        "ast",
        "json",
        "os",
        "re",
        "sys",
        "tkinter"
    ],
    "classes": {
        "Version": {
            "methods": {
                "__init__": [
                    "major",
                    "minor",
                    "patch"
                ],
                "__str__": [],
                "increment_major": [],
                "increment_minor": [],
                "increment_patch": []
            }
        }
    },
    "functions": {
        "load_previous_code_state": [],
        "get_version": [],
        "save_version": [
            "version"
        ],
        "_analyze_codebase": [],
        "generate_change_summary": [
            "old_state",
            "new_state"
        ],
        "generate_project_description": [],
        "analyze_repository": [],
        "update_readme": [
            "version",
            "goals",
            "what_changed",
            "what_good_for_user",
            "what_possibly_next"
        ],
        "main_gui": [],
        "main_cli": [
            "cli_args"
        ],
        "update_and_close": [
            "increment_func"
        ],
        "hello_world": []
    }
}
<!-- AUTO-CODE-STATE-END -->