import unittest
import os
import sys
import json
import ast

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
)

class TestNdaversis(unittest.TestCase):
    """Test suite for the ndaversis script."""

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
        # Create a separate file for the save_version function to modify
        test_file_path = "test_version_file.py"
        with open(test_file_path, "w", encoding="utf-8") as f:
            f.write('__version__ = "0.1.0"')

        # Overwrite the `__file__` attribute in the `ndaversis` module
        import ndaversis
        ndaversis.__file__ = test_file_path

        # Call the function to save the new version
        save_version("0.2.0")

        # Read the file and check if the version was updated
        with open(test_file_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn('__version__ = "0.2.0"', content)

        # Clean up the dummy file
        os.remove(test_file_path)

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

    def test_readme_content_generator(self):
        """Test the generation of README content."""
        # Get the current version
        version = get_version()

        # Define a minimal analysis data structure
        analysis_data = {
            "imports": ["os", "sys"],
            "functions": {
                "test_func": {
                    "docstring": "Use Case: A test function for the README.",
                    "args": [],
                }
            },
            "classes": {},
            "files": {"ndaversis.py": {"docstring": "A test file."}},
        }

        # Generate the README content
        readme_content = generate_readme_content(version, analysis_data, "Initial version.")

        # Check for key sections in the generated content
        self.assertIn("# 1. NDAVERSIS: Agentic Semantic Version Info System", readme_content)
        self.assertIn("## 2. Description Summary", readme_content)
        self.assertIn("## 3. Use Cases", readme_content)
        self.assertIn("## 13. Last Version Summary", readme_content)
        self.assertIn("## 14. Version History", readme_content)
        self.assertIn(f"The last version is `{version}`.", readme_content)

if __name__ == '__main__':
    unittest.main()
