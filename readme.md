# 1. NDAVERSIS: Agentic Semantic Version Info System

## 2. Description Summary
"Ndaversis is a monolithic, self-contained Python wrapper designed to manage semantic versioning for software projects. It operates independently of any version control system like Git, making it a flexible solution for a wide range of development workflows.
This tool is designed to be used by autonomous agents, providing a simple and robust interface for version management. The core functionality is encapsulated within a single script, versions.py, which programmatically modifies itself to update the project's version."

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

The last version is `0.0.4`. Summary: Testing robust regex
## 14. Version History

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
