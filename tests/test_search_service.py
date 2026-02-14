"""
Unit tests for search_service.py

Tests BingSearchService functionality with mocked API calls.
Does not require actual API keys or make live API calls.
"""

import json
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add repo root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestBingSearchService(unittest.TestCase):
    """Test BingSearchService with mocked dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock secrets and LLM router
        self.mock_secrets = Mock()
        self.mock_secrets.get.return_value = "mock-api-key"
        
        self.mock_router = Mock()

    @patch('services.search_service.get_secrets_service')
    @patch('services.search_service.ModelRouter')
    def test_initialization(self, mock_router_class, mock_secrets_func):
        """Test service initialization."""
        from services.search_service import BingSearchService
        
        mock_secrets_func.return_value = self.mock_secrets
        mock_router_class.return_value = self.mock_router
        
        service = BingSearchService()
        
        # Verify API key was loaded
        self.mock_secrets.get.assert_called_with("bing-search-key", required=True)
        self.assertEqual(service.bing_api_key, "mock-api-key")

    @patch('services.search_service.get_secrets_service')
    @patch('services.search_service.ModelRouter')
    def test_credibility_scoring(self, mock_router_class, mock_secrets_func):
        """Test domain credibility scoring."""
        from services.search_service import BingSearchService
        
        mock_secrets_func.return_value = self.mock_secrets
        mock_router_class.return_value = self.mock_router
        
        service = BingSearchService()
        
        # Test high credibility domains
        self.assertEqual(service.calculate_credibility("https://stanford.edu/research"), 0.9)
        self.assertEqual(service.calculate_credibility("https://www.cdc.gov/health"), 0.9)
        
        # Test medium-high credibility
        self.assertEqual(service.calculate_credibility("https://nature.org/science"), 0.7)
        self.assertEqual(service.calculate_credibility("https://www.bbc.com/news"), 0.7)
        
        # Test medium credibility
        self.assertEqual(service.calculate_credibility("https://example.com/page"), 0.5)
        
        # Test low credibility
        self.assertEqual(service.calculate_credibility("https://random-blog.xyz/post"), 0.3)

    @patch('services.search_service.get_secrets_service')
    @patch('services.search_service.ModelRouter')
    @patch('services.search_service.requests.get')
    def test_search(self, mock_get, mock_router_class, mock_secrets_func):
        """Test Bing search with mocked API response."""
        from services.search_service import BingSearchService
        
        mock_secrets_func.return_value = self.mock_secrets
        mock_router_class.return_value = self.mock_router
        
        # Mock Bing API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "webPages": {
                "value": [
                    {
                        "name": "Python Programming",
                        "url": "https://www.python.org",
                        "snippet": "Official Python website"
                    },
                    {
                        "name": "Stanford AI Courses",
                        "url": "https://stanford.edu/ai",
                        "snippet": "Learn AI at Stanford"
                    }
                ]
            }
        }
        mock_get.return_value = mock_response
        
        service = BingSearchService()
        results = service.search("python programming", count=2)
        
        # Verify results
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["title"], "Python Programming")
        self.assertEqual(results[0]["url"], "https://www.python.org")
        self.assertIn("credibility", results[0])
        
        # Verify API was called correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertIn("Ocp-Apim-Subscription-Key", call_args[1]["headers"])

    @patch('services.search_service.get_secrets_service')
    @patch('services.search_service.ModelRouter')
    def test_extract_claims(self, mock_router_class, mock_secrets_func):
        """Test claim extraction with mocked LLM response."""
        from services.search_service import BingSearchService
        
        mock_secrets_func.return_value = self.mock_secrets
        
        # Mock LLM response
        mock_router = Mock()
        mock_router.call.return_value = json.dumps([
            "Python was created by Guido van Rossum",
            "Python was first released in 1991",
            "Python is used for data science"
        ])
        mock_router_class.return_value = mock_router
        
        service = BingSearchService()
        
        sample_text = """
        Python is a programming language created by Guido van Rossum.
        It was first released in 1991 and is widely used for data science.
        """
        
        claims = service.extract_claims(sample_text)
        
        # Verify claims
        self.assertEqual(len(claims), 3)
        self.assertIn("Guido van Rossum", claims[0])
        self.assertIn("1991", claims[1])
        
        # Verify LLM was called with correct task type
        mock_router.call.assert_called_once()
        call_args = mock_router.call.call_args
        self.assertEqual(call_args[1]["task_type"], "structured")

    @patch('services.search_service.get_secrets_service')
    @patch('services.search_service.ModelRouter')
    def test_validate_outline_pass(self, mock_router_class, mock_secrets_func):
        """Test outline validation with passing confidence."""
        from services.search_service import BingSearchService
        
        mock_secrets_func.return_value = self.mock_secrets
        
        # Mock LLM for claim extraction
        mock_router = Mock()
        mock_router.call.return_value = json.dumps([
            "Python was created by Guido van Rossum",
            "Python was released in 1991"
        ])
        mock_router_class.return_value = mock_router
        
        service = BingSearchService()
        
        # Mock search method to return credible sources
        service.search = Mock(return_value=[
            {
                "title": "Python.org",
                "url": "https://www.python.org/history",
                "snippet": "Python history",
                "credibility": 0.9
            },
            {
                "title": "Stanford CS",
                "url": "https://stanford.edu/python",
                "snippet": "Python course",
                "credibility": 0.9
            },
            {
                "title": "Wikipedia",
                "url": "https://wikipedia.org/python",
                "snippet": "Python programming",
                "credibility": 0.7
            }
        ])
        
        outline = "Python was created by Guido van Rossum and released in 1991."
        report = service.validate_outline(outline)
        
        # Verify report structure
        self.assertIn("claims", report)
        self.assertIn("sources", report)
        self.assertIn("confidence", report)
        self.assertIn("passed", report)
        self.assertIn("details", report)
        
        # With 2 claims and 3 sources each call = 6 total sources
        # Confidence = 6 / 2 = 3.0, normalized to min(3.0/2, 1.0) = 1.0
        self.assertEqual(report["confidence"], 1.0)
        self.assertTrue(report["passed"])

    @patch('services.search_service.get_secrets_service')
    @patch('services.search_service.ModelRouter')
    def test_validate_outline_fail(self, mock_router_class, mock_secrets_func):
        """Test outline validation with failing confidence."""
        from services.search_service import BingSearchService
        
        mock_secrets_func.return_value = self.mock_secrets
        
        # Mock LLM for claim extraction
        mock_router = Mock()
        mock_router.call.return_value = json.dumps([
            "Unverifiable claim about future events",
            "Another unverifiable claim"
        ])
        mock_router_class.return_value = mock_router
        
        service = BingSearchService()
        
        # Mock search method to return few/no credible sources
        service.search = Mock(return_value=[
            {
                "title": "Low credibility site",
                "url": "https://random-blog.xyz/post",
                "snippet": "Random blog post",
                "credibility": 0.3  # Below 0.5 threshold
            }
        ])
        
        outline = "Some outline with unverifiable claims."
        report = service.validate_outline(outline)
        
        # Verify low confidence and fail status
        self.assertLess(report["confidence"], 0.7)
        self.assertFalse(report["passed"])


class TestCredibilityScoring(unittest.TestCase):
    """Focused tests for credibility scoring logic."""

    @patch('services.search_service.get_secrets_service')
    @patch('services.search_service.ModelRouter')
    def test_edu_domains(self, mock_router_class, mock_secrets_func):
        """Test .edu domain scoring."""
        from services.search_service import BingSearchService
        
        mock_secrets = Mock()
        mock_secrets.get.return_value = "mock-key"
        mock_secrets_func.return_value = mock_secrets
        
        service = BingSearchService()
        
        # Test various .edu formats
        self.assertEqual(service.calculate_credibility("https://mit.edu"), 0.9)
        self.assertEqual(service.calculate_credibility("https://www.harvard.edu/page"), 0.9)
        self.assertEqual(service.calculate_credibility("http://cs.stanford.edu/ai"), 0.9)

    @patch('services.search_service.get_secrets_service')
    @patch('services.search_service.ModelRouter')
    def test_news_domains(self, mock_router_class, mock_secrets_func):
        """Test major news site scoring."""
        from services.search_service import BingSearchService
        
        mock_secrets = Mock()
        mock_secrets.get.return_value = "mock-key"
        mock_secrets_func.return_value = mock_secrets
        
        service = BingSearchService()
        
        # Test known news sites
        self.assertEqual(service.calculate_credibility("https://www.bbc.com/news"), 0.7)
        self.assertEqual(service.calculate_credibility("https://reuters.com/article"), 0.7)
        self.assertEqual(service.calculate_credibility("https://www.nytimes.com/2024/story"), 0.7)


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)

