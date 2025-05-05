import unittest
from unittest.mock import patch, MagicMock
import json
import http.client
import os

# Assuming the function is in a file named 'serper_tools.py'
# If it's in the same file, you can remove the 'serper_tools.' prefix
#from serper_tools import serp_google_search
from .serper_tools import serp_google_search

# Store original environment variable if it exists
ORIGINAL_SERPER_API_KEY = os.environ.get('SERPER_API_KEY')

class TestSerpGoogleSearch(unittest.TestCase):

    def setUp(self):
        """Set up for test methods."""
        # Ensure a consistent state for SERPER_API_KEY environment variable
        # Set a dummy key for most tests
        os.environ['SERPER_API_KEY'] = 'test_api_key_123'
        self.dummy_api_key = 'test_api_key_123'

    def tearDown(self):
        """Clean up after test methods."""
        # Restore original environment variable state
        if ORIGINAL_SERPER_API_KEY is not None:
            os.environ['SERPER_API_KEY'] = ORIGINAL_SERPER_API_KEY
        elif 'SERPER_API_KEY' in os.environ:
            del os.environ['SERPER_API_KEY']

    @patch('http.client.HTTPSConnection')
    def test_successful_search_default_params(self, mock_conn_constructor):
        """Test a successful search with default location and country."""
        query = "test query"
        expected_response_data = {"results": ["result1", "result2"]}
        expected_response_str = json.dumps(expected_response_data)

        # Configure the mock connection and response
        mock_response = MagicMock()
        mock_response.read.return_value = expected_response_str.encode('utf-8')
        mock_response.status = 200 # Optional: Check status if needed

        mock_conn_instance = MagicMock()
        mock_conn_instance.getresponse.return_value = mock_response
        mock_conn_constructor.return_value = mock_conn_instance

        # Call the function
        result = serp_google_search(q=query)

        # Assertions
        mock_conn_constructor.assert_called_once_with("google.serper.dev")

        expected_payload = json.dumps({
            "q": query,
            "location": "Switzerland", # Function currently hardcodes this
            "gl": "ch", # Default country
        })
        expected_headers = {
            'X-API-KEY': self.dummy_api_key,
            'Content-Type': 'application/json'
        }
        mock_conn_instance.request.assert_called_once_with(
            "POST", "/search", expected_payload, expected_headers
        )
        mock_conn_instance.getresponse.assert_called_once()
        mock_response.read.assert_called_once()
        self.assertEqual(result, expected_response_str)

    @patch('http.client.HTTPSConnection')
    def test_successful_search_custom_country(self, mock_conn_constructor):
        """Test a successful search with a custom country."""
        query = "another query"
        custom_country = "us"
        expected_response_data = {"results": ["usa result"]}
        expected_response_str = json.dumps(expected_response_data)

        # Configure mocks
        mock_response = MagicMock()
        mock_response.read.return_value = expected_response_str.encode('utf-8')
        mock_conn_instance = MagicMock()
        mock_conn_instance.getresponse.return_value = mock_response
        mock_conn_constructor.return_value = mock_conn_instance

        # Call the function with custom country
        result = serp_google_search(q=query, country=custom_country)

        # Assertions
        mock_conn_constructor.assert_called_once_with("google.serper.dev")

        expected_payload = json.dumps({
            "q": query,
            "location": "Switzerland", # Function currently hardcodes this
            "gl": custom_country, # Custom country used here
        })
        expected_headers = {
            'X-API-KEY': self.dummy_api_key,
            'Content-Type': 'application/json'
        }
        mock_conn_instance.request.assert_called_once_with(
            "POST", "/search", expected_payload, expected_headers
        )
        self.assertEqual(result, expected_response_str)

    @patch('http.client.HTTPSConnection')
    def test_successful_search_custom_location_ignored(self, mock_conn_constructor):
        """Test that custom location parameter is currently ignored by the implementation."""
        query = "location query"
        custom_location = "United States" # This should be ignored
        custom_country = "us"
        expected_response_data = {"results": ["location ignored result"]}
        expected_response_str = json.dumps(expected_response_data)

        # Configure mocks
        mock_response = MagicMock()
        mock_response.read.return_value = expected_response_str.encode('utf-8')
        mock_conn_instance = MagicMock()
        mock_conn_instance.getresponse.return_value = mock_response
        mock_conn_constructor.return_value = mock_conn_instance

        # Call the function with custom location and country
        result = serp_google_search(q=query, location=custom_location, country=custom_country)

        # Assertions
        mock_conn_constructor.assert_called_once_with("google.serper.dev")

        # Verify that the hardcoded location is still used in the payload
        expected_payload = json.dumps({
            "q": query,
            "location": "Switzerland", # Hardcoded value is expected
            "gl": custom_country,
        })
        expected_headers = {
            'X-API-KEY': self.dummy_api_key,
            'Content-Type': 'application/json'
        }
        mock_conn_instance.request.assert_called_once_with(
            "POST", "/search", expected_payload, expected_headers
        )
        self.assertEqual(result, expected_response_str)

    @patch('http.client.HTTPSConnection')
    @patch('os.getenv')
    def test_api_key_missing(self, mock_getenv, mock_conn_constructor):
        """Test behavior when SERPER_API_KEY environment variable is not set."""
        # Ensure getenv returns None for the API key
        mock_getenv.return_value = None

        query = "no api key query"
        expected_response_data = {"error": "API key missing simulation"} # Simulate potential error
        expected_response_str = json.dumps(expected_response_data)

        # Configure mocks
        mock_response = MagicMock()
        mock_response.read.return_value = expected_response_str.encode('utf-8')
        mock_conn_instance = MagicMock()
        mock_conn_instance.getresponse.return_value = mock_response
        mock_conn_constructor.return_value = mock_conn_instance

        # Call the function - it will reload the SERPER_API_KEY value
        # Need to reload the module or mock the global variable directly if not using getenv inside
        # For this structure, mocking os.getenv is sufficient as it's called at module load time
        # *Correction*: os.getenv is called *outside* the function. We need to patch the global SERPER_API_KEY
        # or re-import the module after setting the mock. A simpler way is to patch where it's used.
        # Let's patch the value directly within the test scope if possible, or just test the header.

        # Re-importing or patching the global directly can be complex.
        # Let's test the *effect*: the header should contain None for the key.
        # We need to reset the module-level variable for this test.
        # This is tricky. A better approach would be for the function to *get* the key itself.
        # Given the current code, let's simulate the effect by setting the env var to None *before* import
        # Or, more simply, just check the header sent.

        # Resetting the environment variable for this specific test
        if 'SERPER_API_KEY' in os.environ:
            del os.environ['SERPER_API_KEY']
        # We need to ensure the module re-reads this. The easiest way is to patch the *value* used.
        # Let's patch the constant within the module's scope for this test.
        #with patch('serper_tools.SERPER_API_KEY', None):
        with patch('_common.lib.serper_tools.SERPER_API_KEY', None):
            result = serp_google_search(q=query)

            # Assertions
            mock_conn_constructor.assert_called_once_with("google.serper.dev")

            expected_payload = json.dumps({
                "q": query,
                "location": "Switzerland",
                "gl": "ch",
            })
            # Verify that None is sent as the API key in the header
            expected_headers = {
                'X-API-KEY': None, # Key is None
                'Content-Type': 'application/json'
            }
            mock_conn_instance.request.assert_called_once_with(
                "POST", "/search", expected_payload, expected_headers
            )
            self.assertEqual(result, expected_response_str)

        # Restore env var if needed after the 'with' block (handled by tearDown)


    @patch('http.client.HTTPSConnection')
    @patch('builtins.print') # Mock print to suppress debug output
    def test_http_error_handling(self, mock_print, mock_conn_constructor):
        """Test how the function behaves with an HTTP error (it should still decode)."""
        query = "http error query"
        # Simulate an error response body (e.g., HTML error page or plain text)
        error_response_str = "Internal Server Error"

        # Configure the mock connection and response to simulate an error
        mock_response = MagicMock()
        mock_response.read.return_value = error_response_str.encode('utf-8')
        mock_response.status = 500 # Simulate server error

        mock_conn_instance = MagicMock()
        mock_conn_instance.getresponse.return_value = mock_response
        mock_conn_constructor.return_value = mock_conn_instance

        # Call the function
        result = serp_google_search(q=query)

        # Assertions
        # The function currently doesn't check the status code, it just reads and decodes.
        mock_conn_constructor.assert_called_once_with("google.serper.dev")
        mock_conn_instance.request.assert_called_once()
        mock_conn_instance.getresponse.assert_called_once()
        mock_response.read.assert_called_once()
        # It should return the decoded error string
        self.assertEqual(result, error_response_str)
        # Check if debug print was called
        mock_print.assert_called_with(error_response_str)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
