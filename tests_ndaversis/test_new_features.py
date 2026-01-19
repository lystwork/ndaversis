import unittest
import os
import sys
import json
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ndaversis import Ndaversis, Version

class TestNdaversisNewFeatures(unittest.TestCase):
    def setUp(self):
        self.app = Ndaversis()

    def test_change_visualization_style(self):
        """Verify that Change Visualization does not use pink and is horizontal."""
        old_state = {"test.py": "print('hello')"}
        new_state = {"test.py": "print('hello world')"}
        summary = self.app.generate_change_summary(old_state, new_state)
        
        # Check horizontal orientation
        self.assertIn("graph LR", summary)
        
        # Check that Change Visualization is NOT present
        self.assertNotIn("### 📊 Change Visualization", summary)

    def test_file_level_insights_diagram(self):
        """Verify that File-level Insights contains a diagram."""
        old_state = {"test.py": "print('hello')"}
        new_state = {"test.py": "print('hello world')"}
        summary = self.app.generate_change_summary(old_state, new_state)
        
        self.assertIn("### 🔍 File-level Insights", summary)
        # Should contain an Impact Map with full path and metrics
        self.assertIn("#### Impact Map", summary)
        self.assertIn("graph LR", summary)
        self.assertIn("test.py: Modified (+1/-1)", summary)

    def test_next_steps_uniqueness_fallback(self):
        """Verify that suggest_next_steps fallback returns different suggestions."""
        analysis_data = {"functions": {}, "classes": {}, "imports": [], "files": {}}
        
        # history including one of the pool items
        history = "improve robustness by adding a dedicated test suite"
        
        suggestions = self.app.suggest_next_steps(analysis_data, history)
        
        # The suggestion should not be exactly the same as in history if it's the only one
        self.assertNotIn(history, suggestions)

    def test_readme_uniqueness_integration(self):
        """Integration test for history extraction and uniqueness."""
        # Create a mock readme with version history
        readme_path = "test_readme_uniqueness.md"
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write("""# 1. Test
## 14. Version History
## Version 1.0.0
### What's Possibly Next
improve robustness by adding a dedicated test suite

## 15. Contacts
""")
        
        import ndaversis
        original_readme = ndaversis.README_FILE
        ndaversis.README_FILE = readme_path
        
        try:
            analysis_data = {
                "functions": {}, "classes": {}, "imports": [], "files": {},
                "metrics": {"total_lines": 0, "code_lines": 0, "comment_lines": 0, "blank_lines": 0, "tabs": 0, "strings": 0},
                "languages": {}
            }
            content = self.app.generate_readme_content("1.0.1", analysis_data, "Changes")
            
            # Check if history was extracted and used to make next steps unique
            self.assertIn("## Version 1.0.1", content)
            self.assertIn("## Version 1.0.0", content)
            
            # Check that the specific suggestion from 1.0.0 is NOT in 1.0.1's next steps
            v101_section = content.split("## Version 1.0.1")[1].split("## Version 1.0.0")[0]
            self.assertNotIn("improve robustness by adding a dedicated test suite", v101_section)
            
        finally:
            ndaversis.README_FILE = original_readme
            if os.path.exists(readme_path):
                os.remove(readme_path)

if __name__ == '__main__':
    unittest.main()
