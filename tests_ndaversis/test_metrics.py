import unittest
import os
import sys
import json
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ndaversis import Ndaversis, RepositoryMetrics


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
