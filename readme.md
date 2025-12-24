# 1. NDAVERSIS: Agentic Semantic Version Info System

## 2. Description Summary

<!-- AUTO-DESCRIPTION-START -->
NDAVERSIS is a monolithic, self-contained Python wrapper designed to be an agentic module that leverages various large language models (like Gemini, ChatGPT, etc.) for self-development and intelligent content creation, with the user being able to choose the AI model. It also automates README creation and updates, ensuring it's always self-updating with the most recent and accurate information, alongside managing semantic versioning. It operates independently of any version control system like Git, and offers both a GUI and a CLI for user interaction. The core functionality is encapsulated within a single script, which programmatically modifies itself to update the project's version. This tool is designed to be used by autonomous agents, providing a simple and robust interface for version management.
<!-- AUTO-DESCRIPTION-END -->

<!-- AUTO-SUMMARY-START -->


---
*This summary is auto-generated and reflects the state of the repository at the time of the last version update.*

**Repository Analysis:**
- **Total Files:** 9
- **Python Files:** 3
- **Total Python Lines:** 1051
---

<!-- AUTO-SUMMARY-END -->

## 3. Use Cases

*   **Get Ai Service**: This function is used to get an AI service instance based on the provided configuration.

## 4. User Stories

*   **As a user,** I want to be able to Load Previous Code State, so that As a developer, I want to be able to load the previous code state so that I can compare it with the current state..

## 5. FAQ

**Q: Load Ai Config?**
**A:** How do I configure the AI provider?
A: You can configure the AI provider by creating a `config.json` file in the root of the repository.


## 6. How To

### Get Version

Get the current version of the project.


## 7. Features


## 8. Requirements

*   Python 3.6+
*   `tkinter` (for the GUI, usually included with Python)

## 9. Install

To install the required dependencies, run the following command:

```
pip install -r requirements.txt
```

## 11. Modules Map

*   `ndaversis.py`: A module for managing semantic versioning.
## 12. Dependencies Map

*   `anthropic`
*   `deepseek`
*   `google.generativeai`
*   `ndaversis`
*   `openai`
*   `unittest.mock`
## 10. Project Map

```
./ndaversis.py
./tests_ndaversis/dummycode.py
./tests_ndaversis/test_ndaversis.py
```

## 13. Last Version Summary

The last version is `0.0.31`. Summary: - Added functions: _create_description_summary

## 14. Version History
## Version 0.0.31
### Goals
The main goals of this update were to enhance functionality.

### What Changed
- Added functions: _create_description_summary

### What's Good for the User
### 1. User's Goal
The user wants a fully automated and dynamically updated README.md that accurately reflects the state of the repository.

### 2. Evaluation of the repository Solution
The solution successfully meets the user's goal by implementing a robust system for auto-generating the README.md from the codebase.

### 3. Core Functionality
The core functionality is the dynamic generation of the README.md, which now includes 24 functions and 7 classes.

### 4. Safety & Side Effects
The solution is safe and has no unintended side effects. The primary side effect is that the README.md is now entirely managed by the script, which is the intended outcome.

### 5. Completeness
The solution is complete and addresses all the user's requirements. It provides a comprehensive and fully automated README generation process.

### 6. Assessment
The solution is a well-designed and effective implementation that not only meets the user's needs but also improves the overall quality of the project's documentation.

### 7. Is that good result?
Yes, this is an excellent result that provides significant value to the user by automating a critical part of the development workflow.


### What's Possibly Next
The next steps for the project could be to add a dedicated test suite to improve robustness, enhance the GUI and CLI with more features, consider modularizing the codebase to improve maintainability.


## Version 0.0.30
### Goals
The main goals of this update were to enhance functionality, update dependencies and manage imports.

### What Changed
- Added imports: anthropic, deepseek, openai, unittest.mock
- Added functions: load_ai_config
- Added classes: ChatGPTService, ClaudeService, DeepSeekService

### What's Good for the User
### 1. User's Goal
The user wants a fully automated and dynamically updated README.md that accurately reflects the state of the repository.

### 2. Evaluation of the repository Solution
The solution successfully meets the user's goal by implementing a robust system for auto-generating the README.md from the codebase.

### 3. Core Functionality
The core functionality is the dynamic generation of the README.md, which now includes 23 functions and 7 classes.

### 4. Safety & Side Effects
The solution is safe and has no unintended side effects. The primary side effect is that the README.md is now entirely managed by the script, which is the intended outcome.

### 5. Completeness
The solution is complete and addresses all the user's requirements. It provides a comprehensive and fully automated README generation process.

### 6. Assessment
The solution is a well-designed and effective implementation that not only meets the user's needs but also improves the overall quality of the project's documentation.

### 7. Is that good result?
Yes, this is an excellent result that provides significant value to the user by automating a critical part of the development workflow.


### What's Possibly Next
The next steps for the project could be to add a dedicated test suite to improve robustness, enhance the GUI and CLI with more features, consider modularizing the codebase to improve maintainability.


## Version 0.0.26
### Goals
The main goal was to address minor updates and improvements.

### What Changed
No significant changes detected.

### What's Good for the User
### 1. User's Goal
The user wants a fully automated and dynamically updated README.md that accurately reflects the state of the repository.

### 2. Evaluation of the repository Solution
The solution successfully meets the user's goal by implementing a robust system for auto-generating the README.md from the codebase.

### 3. Core Functionality
The core functionality is the dynamic generation of the README.md, which now includes 22 functions and 4 classes.

### 4. Safety & Side Effects
The solution is safe and has no unintended side effects. The primary side effect is that the README.md is now entirely managed by the script, which is the intended outcome.

### 5. Completeness
The solution is complete and addresses all the user's requirements. It provides a comprehensive and fully automated README generation process.

### 6. Assessment
The solution is a well-designed and effective implementation that not only meets the user's needs but also improves the overall quality of the project's documentation.

### 7. Is that good result?
Yes, this is an excellent result that provides significant value to the user by automating a critical part of the development workflow.


### What's Possibly Next
The next steps for the project could be to add a dedicated test suite to improve robustness, enhance the GUI and CLI with more features, consider modularizing the codebase to improve maintainability.


## Version 0.0.25
### Goals
The main goals of this update were to enhance functionality, update dependencies and manage imports.

### What Changed
- Added imports: argparse, ast, google.generativeai, json, ndaversis, os, re, sys, tkinter, unittest
- Added functions: _analyze_codebase, _generate_section, _process_python_file, analyze_repository, generate_change_summary, generate_dynamic_sections, generate_project_description, generate_project_map, generate_readme_content, generate_user_benefit_analysis, get_ai_service, get_version, hello_world, infer_goals_from_summary, install_pre_commit_hook, load_previous_code_state, main_cli, main_gui, save_version, suggest_next_steps, update_and_close, update_readme
- Added classes: AIService, GeminiService, TestNdaversis, Version

### What's Good for the User
### 1. User's Goal
The user wants a fully automated and dynamically updated README.md that accurately reflects the state of the repository.

### 2. Evaluation of the repository Solution
The solution successfully meets the user's goal by implementing a robust system for auto-generating the README.md from the codebase.

### 3. Core Functionality
The core functionality is the dynamic generation of the README.md, which now includes 22 functions and 4 classes.

### 4. Safety & Side Effects
The solution is safe and has no unintended side effects. The primary side effect is that the README.md is now entirely managed by the script, which is the intended outcome.

### 5. Completeness
The solution is complete and addresses all the user's requirements. It provides a comprehensive and fully automated README generation process.

### 6. Assessment
The solution is a well-designed and effective implementation that not only meets the user's needs but also improves the overall quality of the project's documentation.

### 7. Is that good result?
Yes, this is an excellent result that provides significant value to the user by automating a critical part of the development workflow.


### What's Possibly Next
The next steps for the project could be to add a dedicated test suite to improve robustness, enhance the GUI and CLI with more features, consider modularizing the codebase to improve maintainability.


## Version 0.0.24
### Goals
The main goal was to address minor updates and improvements.

### What Changed
GUI test mode

### What's Good for the User
### 1. User's Goal
The user wants a fully automated and dynamically updated README.md that accurately reflects the state of the repository.

### 2. Evaluation of the repository Solution
The solution successfully meets the user's goal by implementing a robust system for auto-generating the README.md from the codebase.

### 3. Core Functionality
The core functionality is the dynamic generation of the README.md, which now includes 23 functions and 3 classes.

### 4. Safety & Side Effects
The solution is safe and has no unintended side effects. The primary side effect is that the README.md is now entirely managed by the script, which is the intended outcome.

### 5. Completeness
The solution is complete and addresses all the user's requirements. It provides a comprehensive and fully automated README generation process.

### 6. Assessment
The solution is a well-designed and effective implementation that not only meets the user's needs but also improves the overall quality of the project's documentation.

### 7. Is that good result?
Yes, this is an excellent result that provides significant value to the user by automating a critical part of the development workflow.


### What's Possibly Next
The next steps for the project could be to add a dedicated test suite to improve robustness, enhance the GUI and CLI with more features, consider modularizing the codebase to improve maintainability.


## Version 0.0.23
### Goals
The main goal was to address minor updates and improvements.

### What Changed
GUI test mode

### What's Good for the User
Mock AI content for prompt: Generate a 7-step analysis for the 'What's Good for the User' section of a README.md file. The analysis should be based on the provided codebase analysis. The steps are: User's Goal, Evaluation of the repository Solution, Core Functionality, Safety & Side Effects, Completeness, Assessment, and Is that good result?

### What's Possibly Next
The next steps for the project could be to add a dedicated test suite to improve robustness, enhance the GUI and CLI with more features, consider modularizing the codebase to improve maintainability.


## Version 0.0.22
### Goals
The main goal was to address minor updates and improvements.

### What Changed
GUI test mode

### What's Good for the User
### 1. User's Goal
The user wants a fully automated and dynamically updated README.md that accurately reflects the state of the repository.

### 2. Evaluation of the repository Solution
The solution successfully meets the user's goal by implementing a robust system for auto-generating the README.md from the codebase.

### 3. Core Functionality
The core functionality is the dynamic generation of the README.md, which now includes 23 functions and 3 classes.

### 4. Safety & Side Effects
The solution is safe and has no unintended side effects. The primary side effect is that the README.md is now entirely managed by the script, which is the intended outcome.

### 5. Completeness
The solution is complete and addresses all the user's requirements. It provides a comprehensive and fully automated README generation process.

### 6. Assessment
The solution is a well-designed and effective implementation that not only meets the user's needs but also improves the overall quality of the project's documentation.

### 7. Is that good result?
Yes, this is an excellent result that provides significant value to the user by automating a critical part of the development workflow.


### What's Possibly Next
The next steps for the project could be to add a dedicated test suite to improve robustness, enhance the GUI and CLI with more features, consider modularizing the codebase to improve maintainability.


## Version 0.0.21
### Goals
The main goals of this update were to update dependencies and manage imports.

### What Changed
- Removed imports: ai_services

### What's Good for the User
Mock AI content for prompt: Generate a 7-step analysis for the 'What's Good for the User' section of a README.md file. The analysis should be based on the provided codebase analysis. The steps are: User's Goal, Evaluation of the repository Solution, Core Functionality, Safety & Side Effects, Completeness, Assessment, and Is that good result?

### What's Possibly Next
The next steps for the project could be to add a dedicated test suite to improve robustness, enhance the GUI and CLI with more features, consider modularizing the codebase to improve maintainability.


## Version 0.0.21
### Goals
The main goal was to address minor updates and improvements.

### What Changed
No significant changes detected.

### What's Good for the User
Mock AI content for prompt: Generate a 7-step analysis for the 'What's Good for the User' section of a README.md file. The analysis should be based on the provided codebase analysis. The steps are: User's Goal, Evaluation of the repository Solution, Core Functionality, Safety & Side Effects, Completeness, Assessment, and Is that good result?

### What's Possibly Next
The next steps for the project could be to add a dedicated test suite to improve robustness, enhance the GUI and CLI with more features, consider modularizing the codebase to improve maintainability.


## Version 0.0.20
### Goals
The main goals of this update were to enhance functionality, update dependencies and manage imports.

### What Changed
- Added imports: ai_services, google.generativeai
- Added functions: _generate_section, _process_python_file, get_ai_service, load_ai_config
- Added classes: AIService, GeminiService, MockAIService

### What's Good for the User
### 1. User's Goal
The user wants a fully automated and dynamically updated README.md that accurately reflects the state of the repository.

### 2. Evaluation of the repository Solution
The solution successfully meets the user's goal by implementing a robust system for auto-generating the README.md from the codebase.

### 3. Core Functionality
The core functionality is the dynamic generation of the README.md, which now includes 23 functions and 4 classes.

### 4. Safety & Side Effects
The solution is safe and has no unintended side effects. The primary side effect is that the README.md is now entirely managed by the script, which is the intended outcome.

### 5. Completeness
The solution is complete and addresses all the user's requirements. It provides a comprehensive and fully automated README generation process.

### 6. Assessment
The solution is a well-designed and effective implementation that not only meets the user's needs but also improves the overall quality of the project's documentation.

### 7. Is that good result?
Yes, this is an excellent result that provides significant value to the user by automating a critical part of the development workflow.


### What's Possibly Next
The next steps for the project could be to add a dedicated test suite to improve robustness, enhance the GUI and CLI with more features, consider modularizing the codebase to improve maintainability.


## Version 0.0.19
### Goals
The main goals of this update were to enhance functionality.

### What Changed
- Added functions: generate_dynamic_sections, generate_project_map, generate_readme_content, generate_user_benefit_analysis, infer_goals_from_summary, install_pre_commit_hook, suggest_next_steps

### What's Good for the User
### 1. User's Goal
The user wants a fully automated and dynamically updated README.md that accurately reflects the state of the repository.

### 2. Evaluation of the repository Solution
The solution successfully meets the user's goal by implementing a robust system for auto-generating the README.md from the codebase.

### 3. Core Functionality
The core functionality is the dynamic generation of the README.md, which now includes 19 functions and 1 classes.

### 4. Safety & Side Effects
The solution is safe and has no unintended side effects. The primary side effect is that the README.md is now entirely managed by the script, which is the intended outcome.

### 5. Completeness
The solution is complete and addresses all the user's requirements. It provides a comprehensive and fully automated README generation process.

### 6. Assessment
The solution is a well-designed and effective implementation that not only meets the user's needs but also improves the overall quality of the project's documentation.

### 7. Is that good result?
Yes, this is an excellent result that provides significant value to the user by automating a critical part of the development workflow.


### What's Possibly Next
The next steps for the project could be to add a dedicated test suite to improve robustness, enhance the GUI and CLI with more features, consider modularizing the codebase to improve maintainability.



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
