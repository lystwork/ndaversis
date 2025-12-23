import unittest
import os
import sys
import json
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

        with open(self.test_readme_path, "w", encoding="utf-8") as f:
            f.write("# 1. Test Readme\n\n## 14. Version History\n\n## 15. Contacts\n")
        with open(self.test_ndaversis_path, "w", encoding="utf-8") as f:
            f.write('__version__ = "0.1.0"')
        with open(self.test_config_path, "w", encoding="utf-8") as f:
            json.dump({"ai_provider": "gemini"}, f)

        self.readme_patch = patch('ndaversis.README_FILE', self.test_readme_path)
        self.config_patch = patch('ndaversis.CONFIG_FILE', self.test_config_path)
        self.readme_patch.start()
        self.config_patch.start()

        self.app = Ndaversis()

    def tearDown(self):
        """Tear down the test environment."""
        self.readme_patch.stop()
        self.config_patch.stop()

        for path in [self.test_readme_path, self.test_ndaversis_path, self.test_config_path, "dummy_module.py"]:
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

    def test_change_summary_generator(self):
        """Test the generation of the change summary."""
        old_state = {"imports": ["os"], "functions": {"old_func": {}}}
        new_state = {"imports": ["sys"], "functions": {"new_func": {}}}
        summary = self.app.generate_change_summary(old_state, new_state)
        self.assertIn("- Added imports: sys", summary)
        self.assertIn("- Removed imports: os", summary)
        self.assertIn("- Added functions: new_func", summary)
        self.assertIn("- Removed functions: old_func", summary)

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
        cli_args = Namespace(major=False, minor=False, patch=True)

        with patch('ndaversis.__file__', self.test_ndaversis_path):
            self.app.main_cli(cli_args)

        with open(self.test_readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("## Version 0.1.1", content)
        self.assertIn("## 2. Description Summary", content)
        self.assertIn("## 13. Last Version Summary", content)

    @patch('os.getenv')
    def test_get_ai_service(self, mock_getenv):
        """Test the AI service factory function."""
        mock_getenv.return_value = "fake_api_key"

        self.app.ai_config = {"ai_provider": "gemini"}
        self.assertIsInstance(self.app.get_ai_service(), GeminiService)

        self.app.ai_config = {"ai_provider": "chatgpt"}
        self.assertIsInstance(self.app.get_ai_service(), ChatGPTService)

    @patch('builtins.print')
    def test_health_check(self, mock_print):
        """Test the health check functionality."""
        with patch('os.path.exists', return_value=True), patch('os.getenv', return_value="fake_key"):
            self.app.health_check()
            mock_print.assert_any_call("Health check passed. All configurations seem correct.")

        with patch('os.path.exists', side_effect=[False, True]):
            self.app.health_check()
            mock_print.assert_any_call(f"- Configuration file '{self.test_config_path}' not found.")

if __name__ == '__main__':
    unittest.main()
