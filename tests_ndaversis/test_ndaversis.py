import unittest
import os
import sys
import json
import ast
from argparse import Namespace
from unittest.mock import patch, MagicMock

# Add the root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ndaversis import (
    Version,
    _analyze_codebase,
    generate_change_summary,
    save_version,
    _process_python_file,
    generate_readme_content,
    get_version,
    main_cli,
    get_ai_service,
    GeminiService,
    ChatGPTService,
    ClaudeService,
    DeepSeekService,
)

class TestNdaversis(unittest.TestCase):
    """Test suite for the ndaversis script."""

    def setUp(self):
        """Set up the test environment."""
        self.test_readme_path = "test_readme.md"
        self.test_ndaversis_path = "test_ndaversis.py"
        # Create a dummy readme file
        with open(self.test_readme_path, "w", encoding="utf-8") as f:
            f.write("# 1. Test Readme\n\n## 14. Version History\n\n## 15. Contacts\n")
        # Create a dummy ndaversis file
        with open(self.test_ndaversis_path, "w", encoding="utf-8") as f:
            f.write('__version__ = "0.1.0"')

    def tearDown(self):
        """Tear down the test environment."""
        if os.path.exists(self.test_readme_path):
            os.remove(self.test_readme_path)
        if os.path.exists(self.test_ndaversis_path):
            os.remove(self.test_ndaversis_path)

    def test_version_increment(self):
        """Test the increment methods of the Version class."""
        v = Version(1, 2, 3)
        self.assertEqual(str(v), "1.2.3")

        v.increment_patch()
        self.assertEqual(str(v), "1.2.4")

        v.increment_minor()
        self.assertEqual(str(v), "1.3.0")

        v.increment_major()
        self.assertEqual(str(v), "2.0.0")

    def test_save_version(self):
        """Test that the version is correctly saved to a file."""
        save_version("0.2.0", self.test_ndaversis_path)
        with open(self.test_ndaversis_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn('__version__ = "0.2.0"', content)

    @patch('ndaversis.README_FILE', 'test_readme.md')
    def test_process_python_file(self):
        """Test the processing of a single Python file."""
        # Create a dummy file to be analyzed
        dummy_file_path = "dummy_module.py"
        with open(dummy_file_path, "w", encoding="utf-8") as f:
            f.write('"""This is a test module."""\n\n')
            f.write('import os\n\n')
            f.write('def test_func():\n')
            f.write('    """This is a test function."""\n')
            f.write('    pass\n')

        # Create a features dictionary to pass to the function
        features = {
            "imports": set(),
            "classes": {},
            "functions": {},
            "files": {},
        }
        method_names = set()

        # Process the dummy file
        _process_python_file(dummy_file_path, features, method_names)

        # Check that the features were correctly extracted
        self.assertIn("os", features["imports"])
        self.assertIn("test_func", features["functions"])
        self.assertEqual(
            features["functions"]["test_func"]["docstring"],
            "This is a test function.",
        )
        self.assertEqual(
            features["files"][dummy_file_path]["docstring"],
            "This is a test module.",
        )

        # Clean up the dummy file
        os.remove(dummy_file_path)

    @patch('ndaversis.README_FILE', 'test_readme.md')
    def test_analyze_codebase(self):
        """Test the codebase analysis functionality."""
        # Create a dummy file to be analyzed
        dummy_file_path = "dummy_module_for_codebase.py"
        with open(dummy_file_path, "w", encoding="utf-8") as f:
            f.write('"""This is a test module for codebase analysis."""\n\n')
            f.write('import sys\n\n')
            f.write('class MyClass:\n')
            f.write('    def my_method(self):\n')
            f.write('        pass\n')

        # Analyze the codebase
        features, _ = _analyze_codebase()

        # Check that the features were correctly extracted
        self.assertIn("sys", features["imports"])
        self.assertIn("MyClass", features["classes"])
        self.assertIn("my_method", features["classes"]["MyClass"]["methods"])

        # Clean up the dummy file
        os.remove(dummy_file_path)

    def test_change_summary_generator(self):
        """Test the generation of the change summary."""
        old_state = {
            "imports": ["os"],
            "functions": {"old_func": {}},
            "classes": {"OldClass": {}},
        }
        new_state = {
            "imports": ["sys"],
            "functions": {"new_func": {}},
            "classes": {"NewClass": {}},
        }

        summary = generate_change_summary(old_state, new_state)

        # Check that the summary contains the expected changes
        self.assertIn("- Added imports: sys", summary)
        self.assertIn("- Removed imports: os", summary)
        self.assertIn("- Added functions: new_func", summary)
        self.assertIn("- Removed functions: old_func", summary)
        self.assertIn("- Added classes: NewClass", summary)
        self.assertIn("- Removed classes: OldClass", summary)

    @patch('ndaversis.README_FILE', 'test_readme.md')
    @patch('ndaversis.__file__', 'test_ndaversis.py')
    def test_readme_update_integration(self):
        """Integration test for the README update process."""
        cli_args = Namespace(major=False, minor=False, patch=True)

        # The dummy file is created with 0.1.0 in setUp
        # We patch __version__ so get_version() returns the correct starting version for the test
        with patch('ndaversis.__version__', "0.1.0"):
            main_cli(cli_args)

        with open(self.test_readme_path, "r", encoding="utf-8") as f:
            readme_content = f.read()
        with open(self.test_ndaversis_path, "r", encoding="utf-8") as f:
            ndaversis_content = f.read()

        self.assertIn("## Version 0.1.1", readme_content)
        self.assertIn('__version__ = "0.1.1"', ndaversis_content)
        # Check that other dynamic sections are present
        self.assertIn("## 2. Description Summary", readme_content)
        self.assertIn("## 13. Last Version Summary", readme_content)

    @patch('os.getenv')
    def test_get_ai_service(self, mock_getenv):
        """Test the AI service factory function."""
        # Test Gemini
        mock_getenv.return_value = "fake_api_key"
        config = {"ai_provider": "gemini"}
        service = get_ai_service(config)
        self.assertIsInstance(service, GeminiService)

        # Test ChatGPT
        config = {"ai_provider": "chatgpt"}
        service = get_ai_service(config)
        self.assertIsInstance(service, ChatGPTService)

        # Test Claude
        config = {"ai_provider": "claude"}
        service = get_ai_service(config)
        self.assertIsInstance(service, ClaudeService)

        # Test DeepSeek
        config = {"ai_provider": "deepseek"}
        service = get_ai_service(config)
        self.assertIsInstance(service, DeepSeekService)

        # Test unknown provider
        config = {"ai_provider": "unknown"}
        service = get_ai_service(config)
        self.assertIsNone(service)

        # Test missing API key
        mock_getenv.return_value = None
        config = {"ai_provider": "gemini"}
        service = get_ai_service(config)
        self.assertIsNone(service)

if __name__ == '__main__':
    unittest.main()
