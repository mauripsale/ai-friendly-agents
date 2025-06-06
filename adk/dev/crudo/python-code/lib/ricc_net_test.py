import unittest
from unittest.mock import patch, MagicMock
import requests
from .ricc_net import check_url_endpoint

class TestCheckUrlEndpoint(unittest.TestCase):

    @patch('requests.get')
    def test_check_url_endpoint_success(self, mock_get):
        """Test successful URL check."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Test page content"
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_get.return_value = mock_response

        result = check_url_endpoint("http://google.com")

        self.assertIsNotNone(result)
        self.assertEqual(result["http_response"], 200)
        self.assertIn("latency", result)
        self.assertEqual(result["page"], "Test page content")

    @patch('requests.get')
    def test_check_url_endpoint_timeout(self, mock_get):
        """Test URL check timeout."""
        mock_get.side_effect = requests.exceptions.Timeout

        result = check_url_endpoint("http://google.com", timeout=0.001)

        self.assertIsNone(result)

    @patch('requests.get')
    def test_check_url_endpoint_connection_error(self, mock_get):
        """Test URL check connection error."""
        mock_get.side_effect = requests.exceptions.ConnectionError

        result = check_url_endpoint("http://doesnt_exist.com")

        self.assertIsNone(result)

    @patch('requests.get')
    def test_check_url_endpoint_non_text_content(self, mock_get):
        """Test URL check with non-text content."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'image/png'}
        mock_get.return_value = mock_response

        result = check_url_endpoint("http://google.com")

        self.assertIsNotNone(result)
        self.assertEqual(result["page"], "Content is not text-based.")

    def test_riccardo_real_wget_gugol_com(self):
        #pass
        #print("ciao")
        result = check_url_endpoint("http://google.com")
        #print(result)
        self.assertIn("latency", result)
        self.assertIn("http_response", result)
        self.assertIn("page", result)
        self.assertEqual(result["http_response"], 200)
        #self.assertEqual(result["page"], "Content is not text-based.")
        self.assertLess(result["latency"], 1.0, 'less than one second.. i hope')
        #self.assertEqual(result["page"], "Test page content")
        self.assertIn("Google", result["page"], "Page should mention Google")
        self.assertIn("search", result["page"], "Page should mention Search")
        #self.assertIn("offered in", result["page"], "Page should mention Search")
        #self.assertIn("Lucky", result["page"], "Page should mention Im feeling lucky")



if __name__ == '__main__':
    unittest.main()
