# NDAVERSIS: agentic semantic version info system.

**Ndaversis** (**N**ikita **D**rozdov **A**gentic **Ver**sioning **S**emantic **I**nfo **S**ystem) is a monolithic, self-contained Python wrapper designed to manage semantic versioning for software projects. It operates independently of any version control system like Git, making it a flexible solution for a wide range of development workflows.

This tool is designed to be used by autonomous agents, providing a simple and robust interface for version management. The core functionality is encapsulated within a single script, `versions.py`, which programmatically modifies itself to update the project's version.

### Key Features:

*   **Git-Independent Versioning:** The project version is stored directly within the `versions.py` script, ensuring that the versioning system is entirely self-contained.
*   **Semantic Versioning 2.0.0:** Adheres to the SemVer 2.0.0 standard for MAJOR, MINOR, and PATCH increments.
*   **Automatic Changelog Generation:** Automatically updates this `readme.md` file with a new version entry and a summary of changes, creating a simple and effective changelog.
*   **Dual Interface:** Provides both a command-line interface (CLI) for headless environments and automation, and a graphical user interface (GUI) for interactive use.
*   **Monolithic Design:** All core logic is contained within a single Python file, making it easy to integrate and manage.

## Version History

## Version 0.0.1

Initial version.
