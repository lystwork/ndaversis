# 1. NDAVERSIS: Agentic Semantic Version Info System

**Current Version:** `0.0.60`

## 2. Description Summary

<!-- AUTO-DESCRIPTION-START -->
**NDAVERSIS** is designed with a simple goal: to let you **'set and forget'** your documentation and versioning. It automatically generates and maintains an accurate README.md and manages semantic versioning directly within your code, ensuring your project info is always up-to-date even as you change the code. Whether you have an internet connection or not, it works locally to keep your repository professional and informative with zero manual effort.
<!-- AUTO-DESCRIPTION-END -->

<!-- AUTO-SUMMARY-START -->


----- 
*This summary is auto-generated and reflects the state of the repository at the time of the last version update.*

### Repository Metrics

| Metric | Value |
| :--- | :--- |
| Total Lines | 2282 |
| Code Lines | 1793 |
| Comment Lines | 147 |
| Blank Lines | 342 |
| Tabs | 0 |
| Strings | 1605 |


### Language Breakdown

| Extension | Count |
| :--- | :--- |
| .py | 2 |
| .md | 2 |
| .json | 2 |
| no extension | 2 |
| .txt | 2 |


### File Statistics
- **Total Files:** 10
- **Python Files:** 2
----- 

<!-- AUTO-SUMMARY-END -->

## 3. Use Cases

*   **Automated Release Cycles**: Integrate version bumping into CI/CD pipelines for touchless releases.
*   **Dynamic Documentation Sync**: Ensure the repository's 'front window' (README) always matches the latest architectural changes.
*   **Offline Repository Health**: Audit codebase metrics and structure without needing external tool connectivity.
*   **Standardized Semantic Versioning**: Enforce consistent versioning across monolithic or microservice projects automatically.

## 4. User Stories

*   **DevOps Engineer**: As a DevOps engineer, I want documentation to refresh on every commit, so that the team always sees the current state without manual edits.
*   **Open Source Maintainer**: As a maintainer, I want semantic versioning to be calculated from code changes, so that I can avoid human error during release tags.
*   **Full-Stack Developer**: As a developer, I want a visual map of my project structure, so that I can quickly onboard new contributors or navigate complex repos.
*   **Project Lead**: As a lead, I want to track code metrics like comments vs code ratios, so that I can maintain high quality and documentation standards.

## 5. FAQ

*   **Q: Will this work without an internet connection?**
    **A:** Yes, the core analysis and documentation logic works entirely offline.
*   **Q: Does it actually update my code's version?**
    **A:** Absolutely. It scans and updates your version strings automatically based on your changes.
*   **Q: Is it really 'set and forget'?**
    **A:** That's the goal. Integrate it once (e.g., via pre-commit hook), and let it handle the rest.

## 6. How To

### 🚀 Quick Patch Update
To quickly update your project's version and README after a minor change:
```bash
python ndaversis.py cli --patch
```

### 🎨 Using the Graphical Interface
If you prefer a visual tool, simply run the script without arguments:
```bash
python ndaversis.py
```

### 🔗 Git Pre-Commit Integration
For a true 'set and forget' experience, integrate it into your Git workflow. This ensures the README and version are updated every time you commit:
```bash
python ndaversis.py install-hook
```

### 🔍 Detailed Repository Audit
To see a full analysis of your code metrics and project structure without updating anything:
```bash
python ndaversis.py audit
```

## 7. Features

*   **Set-and-Forget Automation**: Automatically keeps your project documentation and versioning in sync with your code, saving you manual effort on every update.
*   **AI-Powered Documentation**: Automatically drafts FAQs, User Stories, and Use Cases by analyzing your code structure with AI, ensuring your README is professional even if you haven't written a word.
*   **Intelligent Version Management**: Handles semantic versioning (Major.Minor.Patch) automatically, calculating the right bump based on your actual code changes.
*   **Automatic Architecture Charts**: Creates UML Use Case diagrams to visually communicate project goals and user interactions to stakeholders.
*   **Visual Logic Maps**: Automatically generates process diagrams (BPMN) in Mermaid syntax to show how your code's logic flows visually.
*   **Comprehensive Project Analysis**: Gains a birds-eye view of your codebase with automatic calculation of line counts, language distribution, and complexity metrics.
*   **Suggest Version Bump**: Suggest a version bump based on the change summary.
*   **Instant README Refresh**: Keeps your entire project front-page up-to-date with structural maps, dependency graphs, and latest feature lists in one click.
*   **User-Friendly Interface**: Provides a sleek graphical window for managing your project updates, making it accessible even for those who avoid the terminal.
*   **Project Integrity Check**: Automatically verifies your environment and configuration to ensure everything is set up for flawless automation.
*   **Set-and-Forget Workflow**: One-time integration into your Git workflow that triggers documentation and version updates automatically before every commit.

## 8. Requirements

### Languages & Environments
*   **PY**: Primary development language (2 files detected). Requires Python 3.8+.*   **MD**: Primary development language (2 files detected).*   **JSON**: Primary development language (2 files detected).*   **NO EXTENSION**: Primary development language (2 files detected).*   **TXT**: Primary development language (2 files detected).### Built-in Standard Library (Included with Python)
The following modules are part of Python's standard library and **do not** require external installation:

`argparse`, `ast`, `datetime`, `difflib`, `getpass`, `json`, `os`, `random`, `re`, `sys`, `time`, `typing`

### External Libraries (Must be installed)
To run this project, ensure you have the following packages installed via `pip`:

*   `anthropic`
*   `deepseek`
*   `flet`
*   `google-genai`
*   `openai`

### Services & APIs (Optional)
*   **Vertex AI / Google Gemini**: For AI-powered content generation.
*   **OpenAI / Anthropic / DeepSeek**: Alternative AI providers supported by the system.


## 9. Install

Setting up **NDAVERSIS** is straightforward. You can use it in a fresh environment or join it with an existing project.

### Step 1: Install Python
Ensure you have Python 3.8 or newer. Download it from [python.org](https://www.python.org/downloads/).

### Step 2: Clone & Setup
Clone this repository and install the framework dependencies:
```bash
pip install -r requirements.txt
```

### Step 3: Join with Your Project 🚀
To use Ndaversis with your own code, follow these steps:
1.  **Copy**: Copy `ndaversis.py` and `requirements.txt` into your project's root folder.
2.  **Initialize**: Run `python ndaversis.py` once to create the initial state.
3.  **Integrate**: (Optional) Run `python ndaversis.py install-hook` to automate everything via Git.

### Step 4: (Optional) Set up AI API Keys 🔑
To unlock automated summaries and stories, you can add API keys to `config.json`. Here is how:

*   **Google Gemini (Recommended)**: Go to [Google AI Studio](https://aistudio.google.com/), click 'Get API Key'. It usually has a generous FREE tier for individual developers.
*   **OpenAI (ChatGPT)**: Go to the [OpenAI Platform](https://platform.openai.com/api-keys) to create a key. This is a paid service (pay-as-you-go).
*   **Anthropic (Claude)**: Visit the [Anthropic Console](https://console.anthropic.com/) to get your key.

**How to use them**: Open `config.json` in this folder and paste your keys like this:
```json
{
  "GEMINI_API_KEY": "your-key-here",
  "OPENAI_API_KEY": "your-key-here"
}
```
If you leave them blank, the tool will still work perfectly using its built-in 'smart' logic!

### Step 5: Run
Start the GUI or CLI to maintain your project:
```bash
python ndaversis.py
```

## 11. Modules Map

*   **ndaversis_logs.py**: Core logic and definitions for ndaversis_logs.py
*   **ndaversis.py**: Ndaversis: Agentic Semantic Version Information System.


### Module Structure Diagram

```mermaid
classDiagram
    class AIService {
        +__init__()
        +_create_full_prompt()
        +generate_content()
    }
    class GeminiService {
        +__init__()
        +generate_content()
    }
    class ChatGPTService {
        +__init__()
        +generate_content()
    }
    class ClaudeService {
        +__init__()
        +generate_content()
    }
    class DeepSeekService {
        +__init__()
        +generate_content()
    }
    class OpenAICompatibleService {
        +__init__()
        +generate_content()
    }
    class Version {
        +__init__()
        +__str__()
        +increment_major()
        +increment_minor()
        +increment_patch()
    }
    class Ndaversis {
        +__init__()
        +get_version()
        +save_version()
        +load_ai_config()
        +get_ai_service()
        +load_previous_code_state()
        +_process_python_file()
        +_analyze_codebase()
        +_capture_repo_state()
        +_generate_diff()
        +generate_change_summary()
        +_generate_use_cases_prompt()
        +_generate_user_stories_prompt()
        +_generate_repo_synthesis_prompt()
        +_generate_version_bump_prompt()
        +generate_use_case_diagram()
        +generate_bpmn_diagram()
        +_generate_section()
        +generate_dynamic_sections()
        +generate_project_description()
        +generate_project_map()
        +analyze_repository()
        +suggest_version_bump()
        +update_changelog()
        +_create_description_summary()
        +generate_user_benefit_analysis()
        +infer_goals_from_summary()
        +suggest_next_steps()
        +generate_readme_content()
        +update_readme()
        +main_cli()
        +main_gui()
        +health_check()
        +install_pre_commit_hook()
    }
```

## 12. Dependencies Map

### Custom/External Frameworks

*   **anthropic** (pip): Client for Claude, a highly reliable and safe institutional-grade AI.
*   **deepseek** (pip): Advanced AI provider known for efficient and accurate content generation.
*   **flet** (pip): Modern framework for building beautiful and fast interactive user interfaces.
*   **google-genai** (pip): Google's official library for accessing high-performance Gemini AI models.
*   **openai** (pip): Standard interface for integrating ChatGPT and other OpenAI language models.

### Python Standard Library (Built-in)

These modules are built into Python (no installation required):

`argparse`, `ast`, `datetime`, `difflib`, `getpass`, `json`, `os`, `random`, `re`, `sys`, `time`, `typing`


### Library Dependency Diagram

```mermaid
graph TD
    Project --> lang_PY["PY Overview (2 files)"]
    lang_PY --> dep_anthropic["anthropic"]
    lang_PY --> dep_argparse["argparse"]
    lang_PY --> dep_ast["ast"]
    lang_PY --> dep_datetime["datetime"]
    lang_PY --> dep_deepseek["deepseek"]
    lang_PY --> dep_difflib["difflib"]
    lang_PY --> dep_flet["flet"]
    lang_PY --> dep_getpass["getpass"]
    lang_PY --> dep_google_genai["google-genai"]
    lang_PY --> dep_json["json"]
    lang_PY --> dep_openai["openai"]
    lang_PY --> dep_os["os"]
    lang_PY --> dep_random["random"]
    lang_PY --> dep_re["re"]
    lang_PY --> dep_sys["sys"]
    lang_PY --> dep_time["time"]
    lang_PY --> dep_typing["typing"]
    Project --> lang_MD["MD Overview (2 files)"]
    Project --> lang_JSON["JSON Overview (2 files)"]
    Project --> lang_NO_EXTENSION["NO EXTENSION Overview (2 files)"]
    Project --> lang_TXT["TXT Overview (2 files)"]
```

## 10. Project Map

```
./.gitignore
./LICENSE
./PRIVACY_POLICY.md
./config.json
./ndaversis.py
./ndaversis_logs.py
./ndaversis_state.json
./readme.md
./requirements.txt
./test_output.txt
```

### Project Structure Diagram

```mermaid
graph TD
    Root[./]
    Root --> node_gitignore["gitignore"]
    Root --> node_LICENSE["LICENSE"]
    Root --> node_PRIVACY_POLICY_md["PRIVACY_POLICY.md"]
    Root --> node_config_json["config.json"]
    Root --> node_ndaversis_py["ndaversis.py"]
    Root --> node_ndaversis_logs_py["ndaversis_logs.py"]
    Root --> node_ndaversis_state_json["ndaversis_state.json"]
    Root --> node_readme_md["readme.md"]
    Root --> node_requirements_txt["requirements.txt"]
    Root --> node_test_output_txt["test_output.txt"]
```

## 13. Last Version Summary

The last version is `0.0.60`. Detailed change log and metrics:
| File | Status | Lines + | Lines - | Chars + | Chars - | Tabs | Spaces |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| ./ndaversis.py | modified | 18 | 16 | 901 | 727 | 0 | 215 |
| ./ndaversis_logs.py | modified | 1 | 0 | 1265 | 0 | 0 | 196 |
| ./ndaversis_state.json | modified | 4 | 4 | 756682 | 472381 | 0 | 142145 |
| ./readme.md | modified | 78 | 93 | 3222 | 4277 | 0 | 506 |


#### Impact Map

```mermaid
graph LR
    Root["Latest Changes"] --> ndaversis_py & ndaversis_logs_py & ndaversis_state_json & readme_md
    ndaversis_py["./ndaversis.py: Modified with 18 additions and 16 removals."]
    style ndaversis_py fill:#bbdefb,stroke:#333,stroke-width:2px
    ndaversis_logs_py["./ndaversis_logs.py: Modified with 1 additions and 0 removals."]
    style ndaversis_logs_py fill:#bbdefb,stroke:#333,stroke-width:2px
    ndaversis_state_json["./ndaversis_state.json: Modified with 4 additions and 4 removals."]
    style ndaversis_state_json fill:#bbdefb,stroke:#333,stroke-width:2px
    readme_md["./readme.md: Modified with 78 additions and 93 removals."]
    style readme_md fill:#bbdefb,stroke:#333,stroke-width:2px
```


**Practical Impact**: Significant improvement to project maintainability and documentation sync.

## 14. Version History
## Version 0.0.60
### Goals
The main goals were to refine existing features for better performance and reliability.

### What Changed
| File | Status | Lines + | Lines - | Chars + | Chars - | Tabs | Spaces |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| ./ndaversis.py | modified | 18 | 16 | 901 | 727 | 0 | 215 |
| ./ndaversis_logs.py | modified | 1 | 0 | 1265 | 0 | 0 | 196 |
| ./ndaversis_state.json | modified | 4 | 4 | 756682 | 472381 | 0 | 142145 |
| ./readme.md | modified | 78 | 93 | 3222 | 4277 | 0 | 506 |


#### Impact Map

```mermaid
graph LR
    Root["Latest Changes"] --> ndaversis_py & ndaversis_logs_py & ndaversis_state_json & readme_md
    ndaversis_py["./ndaversis.py: Modified with 18 additions and 16 removals."]
    style ndaversis_py fill:#bbdefb,stroke:#333,stroke-width:2px
    ndaversis_logs_py["./ndaversis_logs.py: Modified with 1 additions and 0 removals."]
    style ndaversis_logs_py fill:#bbdefb,stroke:#333,stroke-width:2px
    ndaversis_state_json["./ndaversis_state.json: Modified with 4 additions and 4 removals."]
    style ndaversis_state_json fill:#bbdefb,stroke:#333,stroke-width:2px
    readme_md["./readme.md: Modified with 78 additions and 93 removals."]
    style readme_md fill:#bbdefb,stroke:#333,stroke-width:2px
```


### What's Good for the User
### 💎 What's New?
Refined the core logic in ndaversis.py to improve performance and reliability.

### 🚀 Why Upgrade?
Stay current with the latest optimizations and bug fixes in the core automation engine.


### What's Possibly Next
Moving forward, you might want to implement a plugin system for extended functionality, add comprehensive error handling and logging, enhance the user interface for better accessibility.


## Version 0.0.59
### Goals
The main goals were to refine existing features for better performance and reliability.

### What Changed
| File | Status | Lines + | Lines - | Chars + | Chars - | Tabs | Spaces |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| ./ndaversis.py | modified | 1 | 1 | 22 | 22 | 0 | 2 |
| ./ndaversis_logs.py | modified | 1 | 0 | 1259 | 0 | 0 | 196 |
| ./ndaversis_state.json | modified | 4 | 3 | 472381 | 226333 | 0 | 94694 |
| ./readme.md | modified | 86 | 113 | 3792 | 5369 | 0 | 586 |


#### Impact Map

```mermaid
graph LR
    Root["Latest Changes"] --> ndaversis_py & ndaversis_logs_py & ndaversis_state_json & readme_md
    ndaversis_py["./ndaversis.py: Modified with 1 additions and 1 removals."]
    style ndaversis_py fill:#bbdefb,stroke:#333,stroke-width:2px
    ndaversis_logs_py["./ndaversis_logs.py: Modified with 1 additions and 0 removals."]
    style ndaversis_logs_py fill:#bbdefb,stroke:#333,stroke-width:2px
    ndaversis_state_json["./ndaversis_state.json: Modified with 4 additions and 3 removals."]
    style ndaversis_state_json fill:#bbdefb,stroke:#333,stroke-width:2px
    readme_md["./readme.md: Modified with 86 additions and 113 removals."]
    style readme_md fill:#bbdefb,stroke:#333,stroke-width:2px
```


### What's Good for the User
### 💎 What's New?
Expanded project scope by adding 10 new files, including .gitignore.

### 🚀 Why Upgrade?
This update introduces significant new components that improve the overall feature set of the repository.


### What's Possibly Next
Moving forward, you might want to integrate with more AI providers for diversity, consider modularizing the code to keep it maintainable as it grows.

## Version 0.0.58
### Goals
The main goals were to expand the project's capabilities with new components, refine existing features for better performance and reliability.

### What Changed
| File | Status | Lines + | Lines - | Chars + | Chars - | Tabs | Spaces |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| ./ndaversis.py | modified | 1 | 1 | 22 | 22 | 0 | 2 |
| ./ndaversis_logs.py | modified | 1 | 0 | 2305 | 0 | 0 | 371 |
| ./ndaversis_state.json | added | 11 | 0 | 255389 | 0 | 0 | 51233 |
| ./readme.md | modified | 110 | 905 | 5233 | 34887 | 0 | 861 |


#### Impact Map

```mermaid
graph LR
    Root["Latest Changes"] --> ndaversis_py & ndaversis_logs_py & ndaversis_state_json & readme_md
    ndaversis_py["./ndaversis.py: Modified with 1 additions and 1 removals."]
    style ndaversis_py fill:#bbdefb,stroke:#333,stroke-width:2px
    ndaversis_logs_py["./ndaversis_logs.py: Modified with 1 additions and 0 removals."]
    style ndaversis_logs_py fill:#bbdefb,stroke:#333,stroke-width:2px
    ndaversis_state_json["./ndaversis_state.json: Added with 11 additions and 0 removals."]
    style ndaversis_state_json fill:#bbdefb,stroke:#333,stroke-width:2px
    readme_md["./readme.md: Modified with 110 additions and 905 removals."]
    style readme_md fill:#bbdefb,stroke:#333,stroke-width:2px
```


### What's Good for the User
### 💎 What's New?
Expanded project scope by adding 10 new files, including .gitignore.

### 🚀 Why Upgrade?
This update introduces significant new components that improve the overall feature set of the repository.


### What's Possibly Next
Moving forward, you might want to optimize performance for large-scale repositories, create detailed API documentation for other developers.
## 15. Contacts

*   **Email:** n@ndaotec.com
*   **Repository:** https://github.com/lystwork/ndaversis

## 16. Privacy & Terms

*   **Privacy Policy:** [PRIVACY_POLICY.md](PRIVACY_POLICY.md)

## 17. Investor Relations

> [!IMPORTANT]
> **If you want to be my investor in my new AI-based project - link to [ndaotec.com](http://ndaotec.com)**

## 18. Copyright

ndaotec.com. @ All rights reserved - Nikita Andreevich Drozdov. All rights belong to their respective owners.
