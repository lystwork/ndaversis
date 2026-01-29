import unittest
import os
import sys
import json
import difflib
from argparse import Namespace
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ndaversis import Ndaversis, RepositoryMetrics, Version, GeminiService, ChatGPTService

class TestNdaversis(unittest.TestCase):
    """Test suite for the ndaversis script."""

    def setUp(self):
        """Set up the test environment."""
        self.test_readme_path = "test_ndaversis_readme.md"
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
        self.user_readme_patch = patch('ndaversis.USER_README_FILE', self.test_readme_path)
        self.ndaversis_readme_patch = patch('ndaversis.NDAVERSIS_README_FILE', self.test_readme_path)
        self.config_patch = patch('ndaversis.CONFIG_FILE', self.test_config_path)
        self.state_file_patch = patch('ndaversis.STATE_FILE', self.state_file_path)
        self.logs_file_patch = patch('ndaversis.LOGS_FILE', self.test_logs_path)
        
        self.readme_patch.start()
        self.user_readme_patch.start()
        self.ndaversis_readme_patch.start()
        self.config_patch.start()
        self.state_file_patch.start()
        self.logs_file_patch.start()

        self.app = Ndaversis()

    def tearDown(self):
        """Tear down the test environment."""
        self.readme_patch.stop()
        self.user_readme_patch.stop()
        self.ndaversis_readme_patch.stop()
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
            self.assertIn("NDAVERSIS: Agentic AI-powered Code Analytics and Infrastructure Platform (BETA Version)", summary)
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
            self.app.previous_code_state = self.app.load_previous_code_state()
            self.app.main_cli(Namespace(major=False, minor=False, patch=True))

        with open(self.test_readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("## Version 0.1.1", content)
        self.assertIn("Repository Size:", content)
        self.assertIn("test_txt", content) # Mermaid node ID
        self.assertIn("./test.txt: modified (1 + / 0 -)", content) # Full metric label

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
        self.assertNotIn("Change Visualization", diff)
        self.assertIn("Impact Map", diff)
        self.assertIn("graph LR", diff)
        self.assertIn("Root[\"Latest Changes\"] --> file1_txt & file2_txt & file3_txt", diff)
        self.assertIn("file1.txt: modified (1 + / 1 -)", diff)
        self.assertIn("file3.txt: added (1 + / 0 -)", diff)
        self.assertIn("file2.txt: removed (0 + / 1 -)", diff)
        self.assertNotIn("content1_mod", diff) # Should not include content

    def test_readme_sections_and_diagrams(self):
        """Test that all required sections and Mermaid diagrams are present."""
        analysis_data = {
            "functions": {
                "my_func": {"docstring": "test: doc"},
                "generate_content": {"docstring": "AI logic"},
                "generate_bpmn_diagram": {},
                "generate_use_case_diagram": {},
                "health_check": {}
            },
            "classes": {
                "MyClass": {"methods": {"my_method": {}}},
                "Ndaversis": {"methods": {
                    "increment_patch": {}, 
                    "analyze_repository": {},
                    "install_pre_commit_hook": {},
                    "main_gui": {},
                    "generate_readme_content": {},
                    "is_ndaversis_repo": {},
                    "suggest_version_bump": {}
                }}
            },
            "imports": ["os", "sys", "requests", "openai", "PyQt6"],
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
        
        # Check high-quality diagram fallbacks (offline mode)
        self.assertIn("UC1(Update Version)", content)
        self.assertIn("Analyze[Analyze Codebase]", content)

        # Check new dependency structure
        self.assertIn("Optional - AI Providers (Could be used without)", content)
        self.assertIn("For AI-powered documentation insights", content)
        self.assertIn("Mandatory (Required for correct work)", content)
        self.assertIn("local on-prem mode", content)
        
        # Check high-quality Product Features
        self.assertIn("Set-and-Forget Automation", content)
        self.assertIn("AI-Powered Documentation", content)
        self.assertIn("Intelligent Version Management", content)
        self.assertIn("Visual Logic Maps", content)
        
        # Check Fallbacks (using no docstrings for some sections)
        analysis_empty = {
            "functions": {}, "classes": {}, "imports": ["os"], "files": {},
            "metrics": {"total_lines": 0, "code_lines": 0, "comment_lines": 0, "blank_lines": 0, "tabs": 0, "strings": 0},
            "languages": {}
        }
        content_fallback = self.app.generate_readme_content("0.1.0", analysis_empty, what_changed)
        self.assertIn("graph LR", content_fallback) 
        self.assertIn("## 13. Last Version Summary", content_fallback)
        # Should still have professional templates in fallback
        self.assertIn("Automated Release Cycles", content_fallback)
        self.assertIn("DevOps Engineer", content_fallback)

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


class TestRepositoryMetrics(unittest.TestCase):
    """Comprehensive test suite for the 15 repository evaluation metrics."""

    def setUp(self):
        """Set up test environment."""
        self.app = Ndaversis()
        self.metrics = self.app.metrics

    def test_metrics_initialization(self):
        """Test that RepositoryMetrics initializes correctly."""
        self.assertIsInstance(self.metrics, RepositoryMetrics)
        self.assertEqual(self.metrics.cache_ttl, 1800)
        self.assertIsNone(self.metrics.cache_timestamp)
        self.assertEqual(self.metrics.metrics_cache, {})

    def test_code_quality_metric(self):
        """Test Code Quality metric calculation."""
        result = self.metrics.calculate_code_quality()
        
        self.assertIn('score', result)
        self.assertIn('summary', result)
        self.assertIn('details', result)
        self.assertIsInstance(result['score'], int)
        self.assertGreaterEqual(result['score'], 0)
        self.assertLessEqual(result['score'], 100)
        self.assertIn('docstring_coverage', result['details'])

    def test_code_size_metric(self):
        """Test Code Size metric calculation."""
        result = self.metrics.calculate_code_size()
        
        self.assertIn('score', result)
        self.assertIn('details', result)
        self.assertIn('total_lines', result['details'])
        self.assertIn('code_lines', result['details'])
        self.assertGreater(result['details']['total_lines'], 0)

    def test_security_metric(self):
        """Test Security metric calculation."""
        result = self.metrics.calculate_security()
        
        self.assertIn('score', result)
        self.assertIn('details', result)
        self.assertIsInstance(result['score'], int)
        self.assertGreaterEqual(result['score'], 0)
        self.assertLessEqual(result['score'], 100)

    def test_applicability_metric(self):
        """Test Applicability metric calculation."""
        result = self.metrics.calculate_applicability()
        
        self.assertIn('score', result)
        self.assertIn('details', result)
        self.assertIn('public_functions', result['details'])
        self.assertIn('public_classes', result['details'])

    def test_platform_compatibility_metric(self):
        """Test Platform Compatibility metric calculation."""
        result = self.metrics.calculate_platform_compatibility()
        
        self.assertIn('score', result)
        self.assertIsInstance(result['score'], int)
        self.assertGreaterEqual(result['score'], 0)
        self.assertLessEqual(result['score'], 100)

    def test_quantity_metric(self):
        """Test Quantity metric calculation."""
        result = self.metrics.calculate_quantity()
        
        self.assertIn('score', result)
        self.assertIn('details', result)
        self.assertIn('total_functions', result['details'])
        self.assertIn('total_classes', result['details'])

    def test_performance_metric(self):
        """Test Performance metric calculation."""
        result = self.metrics.calculate_performance()
        
        self.assertIn('score', result)
        self.assertIn('details', result)
        self.assertIsInstance(result['score'], int)

    def test_usability_metric(self):
        """Test Usability metric calculation."""
        result = self.metrics.calculate_usability()
        
        self.assertIn('score', result)
        self.assertIn('details', result)
        self.assertIn('has_readme', result['details'])

    def test_reliability_metric(self):
        """Test Reliability metric calculation."""
        result = self.metrics.calculate_reliability()
        
        self.assertIn('score', result)
        self.assertIn('details', result)
        self.assertIn('error_handling', result['details'])

    def test_innovation_metric(self):
        """Test Innovation metric calculation."""
        result = self.metrics.calculate_innovation()
        
        self.assertIn('score', result)
        self.assertIn('details', result)
        self.assertIn('innovations', result['details'])

    def test_simplicity_metric(self):
        """Test Simplicity metric calculation."""
        result = self.metrics.calculate_simplicity()
        
        self.assertIn('score', result)
        self.assertIn('details', result)
        self.assertIsInstance(result['score'], int)

    def test_aesthetics_metric(self):
        """Test Aesthetics metric calculation."""
        result = self.metrics.calculate_aesthetics()
        
        self.assertIn('score', result)
        self.assertIn('details', result)
        self.assertIn('uses_tabs', result['details'])

    def test_duration_metric(self):
        """Test Duration/Maintainability metric calculation."""
        result = self.metrics.calculate_duration()
        
        self.assertIn('score', result)
        self.assertIn('details', result)
        self.assertIsInstance(result['score'], int)

    def test_accuracy_metric(self):
        """Test Accuracy metric calculation."""
        result = self.metrics.calculate_accuracy()
        
        self.assertIn('score', result)
        self.assertIn('details', result)
        self.assertIn('has_type_hints', result['details'])

    def test_completeness_metric(self):
        """Test Completeness metric calculation."""
        result = self.metrics.calculate_completeness()
        
        self.assertIn('score', result)
        self.assertIn('details', result)
        self.assertIsInstance(result['score'], int)

    def test_get_all_metrics(self):
        """Test that get_all_metrics returns all 15 metrics."""
        result = self.metrics.get_all_metrics()
        
        self.assertIn('overall_score', result)
        self.assertIn('metrics', result)
        self.assertIn('timestamp', result)
        
        # Verify all 15 metrics are present
        expected_metrics = [
            'code_quality', 'code_size', 'security', 'applicability',
            'platform_compatibility', 'quantity', 'performance', 'usability',
            'reliability', 'innovation', 'simplicity', 'aesthetics',
            'duration', 'accuracy', 'completeness'
        ]
        
        for metric in expected_metrics:
            self.assertIn(metric, result['metrics'])
            self.assertIn('score', result['metrics'][metric])
            self.assertIn('summary', result['metrics'][metric])
            self.assertIn('details', result['metrics'][metric])
        
        # Verify overall score is calculated correctly
        total_score = sum(m['score'] for m in result['metrics'].values())
        expected_overall = int(total_score / len(result['metrics']))
        self.assertEqual(result['overall_score'], expected_overall)

    def test_metrics_caching(self):
        """Test that metrics are cached properly."""
        # First call should calculate
        result1 = self.metrics.get_all_metrics()
        self.assertIsNotNone(self.metrics.cache_timestamp)
        
        # Second call should use cache
        result2 = self.metrics.get_all_metrics()
        self.assertEqual(result1, result2)
        
        # Verify cache was used (same timestamp)
        self.assertEqual(result1['timestamp'], result2['timestamp'])

    def test_ai_summary_fallback(self):
        """Test that AI summary falls back gracefully when AI is unavailable."""
        # Temporarily disable AI service
        original_ai = self.metrics.ndaversis.ai_service
        self.metrics.ndaversis.ai_service = None
        
        result = self.metrics.calculate_code_quality()
        
        # Should still have a summary (fallback message)
        self.assertIn('summary', result)
        self.assertIsInstance(result['summary'], str)
        
        # Restore AI service
        self.metrics.ndaversis.ai_service = original_ai

    def test_metrics_score_ranges(self):
        """Test that all metric scores are within valid range (0-100)."""
        result = self.metrics.get_all_metrics()
        
        for metric_name, metric_data in result['metrics'].items():
            score = metric_data['score']
            self.assertGreaterEqual(score, 0, f"{metric_name} score below 0")
            self.assertLessEqual(score, 100, f"{metric_name} score above 100")

    def test_metrics_json_export(self):
        """Test that metrics can be exported to JSON."""
        result = self.metrics.get_all_metrics()
        
        # Try to serialize to JSON
        json_str = json.dumps(result, indent=2)
        self.assertIsInstance(json_str, str)
        
        # Verify it can be deserialized
        parsed = json.loads(json_str)
        self.assertEqual(parsed['overall_score'], result['overall_score'])

    @patch('ndaversis.RepositoryMetrics._get_ai_summary')
    def test_ai_summary_generation(self, mock_ai_summary):
        """Test AI summary generation with mocked AI service."""
        mock_ai_summary.return_value = "Test AI summary"
        
        result = self.metrics.calculate_code_quality()
        
        # Verify AI summary was called
        self.assertEqual(result['summary'], "Test AI summary")

    def test_metrics_details_structure(self):
        """Test that all metrics return properly structured details."""
        result = self.metrics.get_all_metrics()
        
        for metric_name, metric_data in result['metrics'].items():
            self.assertIsInstance(metric_data['details'], dict, 
                                f"{metric_name} details is not a dict")
            self.assertGreater(len(metric_data['details']), 0,
                             f"{metric_name} details is empty")

if __name__ == '__main__':
    unittest.main()


# --- GUI Tests ---
try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    HAS_PYQT_TEST = True
except ImportError:
    HAS_PYQT_TEST = False

@unittest.skipUnless(HAS_PYQT_TEST, "PyQt6 not installed")
class TestNdaversisGUI(unittest.TestCase):
    """Test suite for the PyQt6 GUI."""
    
    @classmethod
    def setUpClass(cls):
        # Create a single QApplication instance for all tests
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        self.ndaversis_app = Ndaversis()
        # Mock important parts that GUI interacts with
        self.ndaversis_app.version = Version(1, 0, 0)
        self.ndaversis_app._analyze_codebase = MagicMock(return_value=({}, {}))
        self.ndaversis_app.generate_readme_content = MagicMock(return_value="Test Content")
        self.ndaversis_app.update_readme = MagicMock()
        self.ndaversis_app.save_version = MagicMock()
        self.ndaversis_app.infer_goals_from_summary = MagicMock(return_value="Test Goals")
        self.ndaversis_app.metrics.get_all_metrics = MagicMock(return_value={
            'overall_score': 85,
            'timestamp': '2023-01-01',
            'metrics': {'code_quality': {'score': 90, 'summary': 'Good', 'details': {}}}
        })
        
        # Import GUIApp directly from the module if possible, or access it 
        # But since it's defined inside ndaversis.py, we need to import it.
        # It was imported at the top of this file via 'from ndaversis import ...'
        from ndaversis import GUIApp
        self.window = GUIApp(self.ndaversis_app)

    def tearDown(self):
        self.window.close()
        self.window.deleteLater()

    def test_gui_initialization(self):
        """Test that the GUI initializes without error."""
        self.assertIsNotNone(self.window)
        self.assertEqual(self.window.windowTitle(), "NDAVERSIS - Agentic Version System")

    def test_tabs_existence(self):
        """Test that tabs are created."""
        self.assertEqual(self.window.tabs.count(), 2)
        self.assertEqual(self.window.tabs.tabText(0), "Version Update")
        self.assertEqual(self.window.tabs.tabText(1), "Metrics Dashboard")

    def test_version_increment_flow(self):
        """Test the version increment logic via GUI methods."""
        # Simulate typing in the change input
        self.window.change_input.setText("Test Change")
        
        # Call the increment method directly (simulating button click)
        self.window.on_increment("Patch")
        
        # Verify calls
        self.ndaversis_app._analyze_codebase.assert_called()
        self.ndaversis_app.update_readme.assert_called()
        self.ndaversis_app.save_version.assert_called()
        self.assertEqual(self.window.status_label.text(), "✅ Success! Version updated to 1.0.1")

    def test_metrics_calculation_flow(self):
        """Test the metrics calculation logic via GUI methods."""
        # Call metrics calculation
        self.window.calculate_metrics_ui()
        
        # Verify metrics were fetched
        self.ndaversis_app.metrics.get_all_metrics.assert_called()
        self.assertIn("Overall: 85%", self.window.metrics_status.text())
        
        # Verify widgets were added (Header + 1 metric)
        # Note: layout count might include spacers or other items depending on implementation
        # But should be > 0
        self.assertGreater(self.window.metrics_layout.count(), 0)
