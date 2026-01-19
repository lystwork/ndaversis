import unittest
import os
import sys
import json
import difflib
from argparse import Namespace
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ndaversis import Ndaversis, Version, GeminiService, ChatGPTService

class TestNdaversis(unittest.TestCase):
    """Test suite for the ndaversis script."""

    def setUp(self):
        """Set up the test environment."""
        self.test_readme_path = "test_ndaversis_readme.md"
        self.test_ndaversis_path = "test_ndaversis.py"
        self.test_logs_path = "test_ndaversis_logs.py"

        with open(self.test_readme_path, "w", encoding="utf-8") as f:
            f.write("# 1. Test Readme\n\n## 14. Version History\n\n## 15. Contacts\n")
        with open(self.test_ndaversis_path, "w", encoding="utf-8") as f:
            f.write('__version__ = "0.1.0"')

        self.readme_patch = patch('ndaversis.README_FILE', self.test_readme_path)
        self.logs_file_patch = patch('ndaversis.LOGS_FILE', self.test_logs_path)
        
        # Mock state and config modules
        self.config_mock = MagicMock()
        self.config_mock.get_all_config.return_value = {"ai_provider": "gemini"}
        self.config_mock.get_config.return_value = "gemini"
        
        self.state_mock = MagicMock()
        self.state_mock.load_state.return_value = {}

        self.modules_patch = patch.multiple('ndaversis', 
                                          ndaversis_config=self.config_mock, 
                                          ndaversis_state=self.state_mock)
        
        self.readme_patch.start()
        self.logs_file_patch.start()
        self.modules_patch.start()

        self.app = Ndaversis()

    def tearDown(self):
        """Tear down the test environment."""
        self.readme_patch.stop()
        self.logs_file_patch.stop()
        self.modules_patch.stop()

        for path in [self.test_readme_path, self.test_ndaversis_path, self.test_logs_path, "dummy_module.py", "./test.txt"]:
            if os.path.exists(path):
                os.remove(path)

    def test_version_increment(self):
        """Test the increment methods of the Version class."""
        v = Version(1, 2, 3)
        v.increment_patch()
        self.assertEqual(str(v), "1.2.4")
        v.increment_minor()
        self.assertEqual(str(v), "1.3.0")
        v.increment_major()
        self.assertEqual(str(v), "2.0.0")

    def test_save_version(self):
        """Test that the version is correctly saved to a file."""
        self.app.save_version("0.2.0", self.test_ndaversis_path)
        with open(self.test_ndaversis_path, "r", encoding="utf-8") as f:
            self.assertIn('__version__ = "0.2.0"', f.read())

    def test_analyze_codebase(self):
        """Test the codebase analysis functionality."""
        # Create a dummy file for analysis
        dummy_file = "dummy_module.py"
        with open(dummy_file, "w", encoding="utf-8") as f:
            f.write('import sys\nclass MyClass:\n    def my_method(self): pass')

        features, _ = self.app._analyze_codebase()

        self.assertIn("sys", features["imports"])
        self.assertIn("MyClass", features["classes"])
        self.assertIn("my_method", features["classes"]["MyClass"]["methods"])

        os.remove(dummy_file)

    def test_process_python_file(self):
        """Test the processing of a single Python file."""
        dummy_file_path = "dummy_module.py"
        with open(dummy_file_path, "w", encoding="utf-8") as f:
            f.write('"""Test module."""\nimport os\ndef test_func():\n    """Test function."""\n    pass')

        features = {
            "imports": set(), "classes": {}, "functions": {}, "files": {},
            "metrics": {"total_lines": 0, "code_lines": 0, "comment_lines": 0, "blank_lines": 0, "tabs": 0, "strings": 0}
        }
        method_names = set()
        self.app._process_python_file(dummy_file_path, features, method_names)

        self.assertIn("os", features["imports"])
        self.assertIn("test_func", features["functions"])
        self.assertEqual(features["functions"]["test_func"]["docstring"], "Test function.")
        self.assertEqual(features["files"][dummy_file_path]["docstring"], "Test module.")

    def test_create_description_summary(self):
        """Test the _create_description_summary method."""
        with patch.object(self.app, 'generate_project_description', return_value="Test Description"):
            summary = self.app._create_description_summary()
            self.assertIn("NDAVERSIS: Agentic Semantic Version Info System", summary)
            self.assertIn("Test Description", summary)

    @patch('ndaversis.__version__', "0.1.0")
    def test_readme_update_integration(self):
        """Integration test for the README integration process."""
        self.app.version = self.app.get_version()
        
        # Mock state load
        self.state_mock.load_state.return_value = {'./test.txt': 'line1\n'} # Mock old state
        
        with open("./test.txt", "w", encoding="utf-8") as f:
            f.write("line1\nline2\n")

        with patch('ndaversis.USER_README_FILE', self.test_readme_path), \
             patch('ndaversis.__file__', self.test_ndaversis_path), \
             patch.object(self.app, 'is_ndaversis_repo', return_value=False):
            self.app.previous_code_state = self.app.load_previous_code_state()
            self.app.main_cli(Namespace(major=False, minor=False, patch=True))

        with open(self.test_readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("## Version 0.1.1", content)
        self.assertIn("Repository Size:", content)
        self.assertIn("test_txt", content) # Mermaid node ID
        self.assertIn("./test.txt: Modified (1 + / 0 -)", content) # Full metric label

        os.remove("./test.txt")

    # @patch('os.getenv')
    # def test_get_ai_service(self, mock_getenv):
    #     """Test the AI service factory function."""
    #     mock_getenv.return_value = "fake_api_key"

    #     self.app.ai_config = {"ai_provider": "gemini"}
    #     self.assertIsInstance(self.app.get_ai_service(), GeminiService)

    #     self.app.ai_config = {"ai_provider": "chatgpt"}
    #     self.assertIsInstance(self.app.get_ai_service(), ChatGPTService)

    @patch('builtins.print')
    def test_health_check(self, mock_print):
        """Test the health check functionality."""
        # Case 1: All good
        with patch('os.path.exists', return_value=True), patch('os.getenv', return_value="fake_key"):
            self.app.health_check()
            mock_print.assert_any_call("Health check passed. All configurations seem correct.")

        # Case 2: Config module missing (simulate by setting to None)
        with patch('ndaversis.ndaversis_config', None):
             self.app.health_check()
             mock_print.assert_any_call("- ndaversis_config module could not be imported.")

    @patch('builtins.print')
    def test_load_ai_config_module_missing(self, mock_print):
        """Test that load_ai_config handles missing module."""
        with patch('ndaversis.ndaversis_config', None):
            config = self.app.load_ai_config()
            self.assertEqual(config, {})

    def test_generate_use_case_diagram(self):
        """Test the generate_use_case_diagram method."""
        with patch.object(self.app, 'ai_service') as mock_ai_service:
            mock_ai_service.generate_content.return_value = "Test Use Case Diagram"
            diagram = self.app.generate_use_case_diagram({})
            self.assertEqual(diagram, "Test Use Case Diagram")
            mock_ai_service.generate_content.assert_called_once()

    def test_generate_bpmn_diagram(self):
        """Test the generate_bpmn_diagram method."""
        with patch.object(self.app, 'ai_service') as mock_ai_service:
            mock_ai_service.generate_content.return_value = "Test BPMN Diagram"
            diagram = self.app.generate_bpmn_diagram({})
            self.assertEqual(diagram, "Test BPMN Diagram")
            mock_ai_service.generate_content.assert_called_once()

    @patch('ndaversis.Ndaversis.generate_use_case_diagram')
    @patch('ndaversis.Ndaversis.generate_bpmn_diagram')
    def test_generate_dynamic_sections_with_ai(
        self, mock_generate_bpmn_diagram, mock_generate_use_case_diagram
    ):
        """Test the generate_dynamic_sections method with AI service."""
        with patch.object(self.app, 'ai_service') as mock_ai_service:
            mock_ai_service.generate_content.side_effect = [
                "Test Use Cases",
                "Test User Stories",
            ]
            mock_generate_use_case_diagram.return_value = "Test Use Case Diagram"
            mock_generate_bpmn_diagram.return_value = "Test BPMN Diagram"

            analysis_data = {"functions": {}, "classes": {}, "imports": []}
            sections = self.app.generate_dynamic_sections(analysis_data)

            self.assertIn("## 3. Use Cases", sections)
            self.assertIn("Test Use Cases", sections)
            self.assertIn("### Use Case Diagram", sections)
            self.assertIn("Test Use Case Diagram", sections)
            self.assertIn("themeVariables", sections) # Check for theme presence

            self.assertIn("## 4. User Stories", sections)
            self.assertIn("Test User Stories", sections)
            self.assertIn("### BPMN Diagram", sections)
            self.assertIn("Test BPMN Diagram", sections)

    def test_suggest_version_bump(self):
        """Test the suggest_version_bump method."""
        with patch.object(self.app, 'ai_service') as mock_ai_service:
            mock_ai_service.generate_content.return_value = "minor"
            suggestion = self.app.suggest_version_bump("Some changes")
            self.assertEqual(suggestion, "minor")
            
            mock_ai_service.generate_content.return_value = "invalid"
            suggestion = self.app.suggest_version_bump("Some changes")
            self.assertEqual(suggestion, "patch")

    def test_update_changelog(self):
        """Test the update_changelog method."""
        self.app.update_changelog("1.0.0", "Initial release")
        self.assertTrue(os.path.exists(self.test_logs_path))
        
        with open(self.test_logs_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn('"version": "1.0.0"', content)
            self.assertIn('"summary": "Initial release"', content)
        
        # Test appending
        self.app.update_changelog("1.1.0", "New feature")
        with open(self.test_logs_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn('"version": "1.1.0"', content)
            self.assertIn('"version": "1.0.0"', content)

    @patch('ndaversis.Ndaversis.suggest_version_bump', return_value="minor")
    @patch('ndaversis.Ndaversis.update_changelog')
    @patch('ndaversis.__version__', "0.1.0")
    def test_cli_auto_versioning(self, mock_update_changelog, mock_suggest_bump):
        """Test CLI auto-versioning when no flag is provided."""
        self.app.version = self.app.get_version()
        with patch('ndaversis.__file__', self.test_ndaversis_path):
            # No major/minor/patch flags
            self.app.main_cli(Namespace(major=False, minor=False, patch=False))
            
        self.assertEqual(str(self.app.version), "0.2.0")
        mock_update_changelog.assert_called_once()

    def test_generate_project_map(self):
        """Test the generate_project_map method."""
        # Create some dummy files
        with open("dummy1.txt", "w") as f: f.write("test")
        with open("dummy2.py", "w") as f: f.write("test")
        
        project_map = self.app.generate_project_map()
        self.assertIn("./dummy1.txt", project_map)
        self.assertIn("./dummy2.py", project_map)
        
        os.remove("dummy1.txt")
        os.remove("dummy2.py")

    def test_generate_diff_concise(self):
        """Test the concise diff generation."""
        old_state = {"file1.txt": "content1", "file2.txt": "content2"}
        new_state = {"file1.txt": "content1_mod", "file3.txt": "content3"}
        diff = self.app.generate_change_summary(old_state, new_state)
        self.assertNotIn("Change Visualization", diff)
        self.assertIn("Impact Map", diff)
        self.assertIn("graph LR", diff)
        self.assertIn("Root[\"Latest Changes\"] --> file1_txt & file2_txt & file3_txt", diff)
        self.assertIn("file1.txt: Modified (1 + / 1 -)", diff)
        self.assertIn("file3.txt: Added (1 + / 0 -)", diff)
        self.assertIn("file2.txt: Removed (0 + / 1 -)", diff)
        self.assertNotIn("content1_mod", diff) # Should not include content

    def test_readme_sections_and_diagrams(self):
        """Test that all required sections and Mermaid diagrams are present."""
        analysis_data = {
            "functions": {"my_func": {"docstring": "test: doc"}},
            "classes": {"MyClass": {"methods": {"my_method": {}}}},
            "imports": ["os", "sys", "requests", "openai", "flet"],
            "files": {"ndaversis.py": {"docstring": "main module"}},
            "languages": {".py": 1, ".md": 1}
        }
        what_changed = "Modified file: ndaversis.py"
        content = self.app.generate_readme_content("0.1.0", analysis_data, what_changed)
        
        # Check Sections
        for i in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]:
            self.assertIn(f"## {i}.", content)
            
        # Check mermaid diagrams
        self.assertIn("pie title Language Distribution", content)
        self.assertIn("graph LR", content) # stdlib diagram
        self.assertIn("Python --\u003e", content)
        # Check new dependency structure
        self.assertIn("Optional - AI Providers (Could be used without)", content)
        self.assertIn("For AI-powered documentation insights", content)
        self.assertIn("Mandatory (Required for correct work)", content)
        self.assertIn("local on-prem mode", content)
        
        # Check Fallbacks (using no docstrings for some sections)
        analysis_empty = {
            "functions": {}, "classes": {}, "imports": ["os"], "files": {},
            "metrics": {"total_lines": 0, "code_lines": 0, "comment_lines": 0, "blank_lines": 0, "tabs": 0, "strings": 0},
            "languages": {}
        }
        content_fallback = self.app.generate_readme_content("0.1.0", analysis_empty, what_changed)
        self.assertIn("graph LR", content_fallback) # stdlib is still shown (empty)
        self.assertIn("## 13. Last Version Summary", content_fallback)

    def test_shadow_repo_agnostic_generation(self):
        """Verify that README sections describe the shadow repo and not Ndaversis."""
        shadow_analysis = {
            "functions": {"calculate_orbit": {"docstring": "Orbit logic."}},
            "classes": {"Planet": {"methods": {"rotate": {}}}},
            "imports": ["math", "astropy"],
            "files": {"space.py": {"docstring": "Space simulation."}}
        }
        what_changed = "New feature: planet rotation"
        content = self.app.generate_readme_content("1.0.0", shadow_analysis, what_changed)
        
        # Should mention the shadow repo items
        self.assertIn("Calculate Orbit", content)
        self.assertIn("Planet", content)
        # Should NOT mention Ndaversis-specific terms in synthesized fallbacks
        self.assertNotIn("tkinter", content)
        self.assertIn("Moving forward", content)

    def test_version_history_limiting(self):
        """Verify that only the most recent 3 versions are kept in the README."""
        # Setup existing history with 4 versions
        existing_history = (
            "## Version 1.0.0\nGoal 1\n\n"
            "## Version 0.9.0\nGoal 2\n\n"
            "## Version 0.8.0\nGoal 3\n\n"
            "## Version 0.7.0\nGoal 4\n"
        )
        
        # Mocking the existing history in the file
        with open(self.test_readme_path, "w", encoding="utf-8") as f:
            f.write(f"# 1. Test\n\n## 14. Version History\n{existing_history}\n## 15. Contacts\n")
            
        analysis_data = {
            "functions": {}, "classes": {}, "imports": [], "files": {},
            "metrics": {"total_lines": 0, "code_lines": 0, "comment_lines": 0, "blank_lines": 0, "tabs": 0, "strings": 0},
            "languages": {}, "diff_data": {}
        }
        what_changed = "Nothing much"
        
        content = self.app.generate_readme_content("1.1.0", analysis_data, what_changed)
        
        # Should contain Version 1.1.0, 1.0.0, and 0.9.0
        self.assertIn("## Version 1.1.0", content)
        self.assertIn("## Version 1.0.0", content)
        self.assertIn("## Version 0.9.0", content)
        # Should NOT contain Version 0.8.0 or 0.7.0
        self.assertNotIn("## Version 0.8.0", content)
        self.assertNotIn("## Version 0.7.0", content)

if __name__ == '__main__':
    unittest.main()
