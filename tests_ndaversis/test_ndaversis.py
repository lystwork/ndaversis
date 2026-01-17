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
        self.test_readme_path = "test_readme.md"
        self.test_ndaversis_path = "test_ndaversis.py"
        self.test_config_path = "test_config.json"
        self.state_file_path = "ndaversis_state.json"
        self.test_logs_path = "test_ndaversis_logs.py"

        with open(self.test_readme_path, "w", encoding="utf-8") as f:
            f.write("# 1. Test Readme\n\n## 14. Version History\n\n## 15. Contacts\n")
        with open(self.test_ndaversis_path, "w", encoding="utf-8") as f:
            f.write('__version__ = "0.1.0"')
        with open(self.test_config_path, "w", encoding="utf-8") as f:
            json.dump({"ai_provider": "gemini"}, f)

        self.readme_patch = patch('ndaversis.README_FILE', self.test_readme_path)
        self.config_patch = patch('ndaversis.CONFIG_FILE', self.test_config_path)
        self.state_file_patch = patch('ndaversis.STATE_FILE', self.state_file_path)
        self.logs_file_patch = patch('ndaversis.LOGS_FILE', self.test_logs_path)
        self.readme_patch.start()
        self.config_patch.start()
        self.state_file_patch.start()
        self.logs_file_patch.start()

        self.app = Ndaversis()

    def tearDown(self):
        """Tear down the test environment."""
        self.readme_patch.stop()
        self.config_patch.stop()
        self.state_file_patch.stop()
        self.logs_file_patch.stop()

        for path in [self.test_readme_path, self.test_ndaversis_path, self.test_config_path, self.state_file_path, self.test_logs_path, "dummy_module.py"]:
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

        features = {"imports": set(), "classes": {}, "functions": {}, "files": {}}
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
        """Integration test for the README update process."""
        self.app.version = self.app.get_version()
        with open(self.state_file_path, "w", encoding="utf-8") as f:
            json.dump({'./test.txt': 'line1\n'}, f)

        with open("./test.txt", "w", encoding="utf-8") as f:
            f.write("line1\nline2\n")

        with patch('ndaversis.__file__', self.test_ndaversis_path):
            self.app.main_cli(Namespace(major=False, minor=False, patch=True))

        with open(self.test_readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("## Version 0.1.1", content)
        self.assertIn("Modified file: ./test.txt", content)

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
        with patch('os.path.exists', return_value=True), patch('os.getenv', return_value="fake_key"):
            self.app.health_check()
            mock_print.assert_any_call("Health check passed. All configurations seem correct.")

        with patch('os.path.exists', side_effect=[False, True]):
            self.app.health_check()
            mock_print.assert_any_call(f"- Configuration file '{self.test_config_path}' not found.")

    @patch('builtins.print')
    def test_load_ai_config_file_not_found(self, mock_print):
        """Test that load_ai_config handles a missing file."""
        os.remove(self.test_config_path)
        # Re-load config now that the file is removed.
        config = self.app.load_ai_config()
        self.assertEqual(config, {})
        mock_print.assert_called_with(
            f"Configuration file '{self.test_config_path}' not found. AI service disabled."
        )

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
            self.assertIn("```mermaid\nTest Use Case Diagram\n```", sections)

            self.assertIn("## 4. User Stories", sections)
            self.assertIn("Test User Stories", sections)
            self.assertIn("### BPMN Diagram", sections)
            self.assertIn("```mermaid\nTest BPMN Diagram\n```", sections)

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
        self.assertIn("Modified file: file1.txt", diff)
        self.assertIn("Added file: file3.txt", diff)
        self.assertIn("Removed file: file2.txt", diff)
        self.assertNotIn("content1_mod", diff) # Should not include content

    def test_readme_sections_and_diagrams(self):
        """Test that all required sections and Mermaid diagrams are present."""
        analysis_data = {
            "functions": {"my_func": {"docstring": "test: doc"}},
            "classes": {"MyClass": {"methods": {"my_method": {}}}},
            "imports": ["os", "sys", "requests"],
            "files": {"ndaversis.py": {"docstring": "main module"}}
        }
        what_changed = "Modified file: ndaversis.py"
        content = self.app.generate_readme_content("0.1.0", analysis_data, what_changed)
        
        # Check Sections
        for i in range(2, 15):
            self.assertIn(f"## {i}.", content)
            
        # Check Diagrams
        self.assertIn("```mermaid\ngraph TD", content) # Project Map / Dependency Graph
        self.assertIn("```mermaid\nclassDiagram", content) # Modules Map
        
        # Check Fallbacks (using no docstrings for some sections)
        analysis_empty = {"functions": {}, "classes": {}, "imports": [], "files": {}}
        content_fallback = self.app.generate_readme_content("0.1.0", analysis_empty, what_changed)
        self.assertIn("General Usage", content_fallback)
        self.assertIn("fulfill my project requirements", content_fallback)
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
        self.assertNotIn("Version Manager", content)
        self.assertNotIn("tkinter", content)
        self.assertIn("As a developer,** I want to utilize `calculate_orbit` ", content)
        self.assertIn("Q: What is the purpose of `calculate_orbit`?", content)

if __name__ == '__main__':
    unittest.main()
