# lib/ricc_cloud_run_test.py

'''
Test me:  just test-cloud-run
'''

import unittest
from unittest.mock import patch, MagicMock
from google.cloud import run_v2
from google.api_core.exceptions import NotFound
from .ricc_cloud_run import get_cloud_run_revisions, _get_cache_path, _write_cache, _read_cache, _is_cache_valid, get_cloud_run_logs
import os
from pathlib import Path
import json
import tempfile

class TestGetCloudRunVersions(unittest.TestCase):

    def setUp(self):
        pass
        # temp_cache_dir = '.cache_unit_tests/'
        # # Create a temporary directory for the cache
        # self.temp_cache_dir = Path(temp_cache_dir) # tempfile.TemporaryDirectory()
        # # Patch the CACHE_DIR to use the temporary directory
        # self.original_cache_dir = Path(".cache")
        # #Path(".cache").replace(Path(self.temp_cache_dir.name))
        # Path(".cache").replace(Path(temp_cache_dir))
        # Create a dummy cache file
        #self.dummy_cache_path = _get_cache_path("test-project", "test-region", "test-service", data_type="versions.json")
        #self.dummy_cache_path.parent.mkdir(parents=True, exist_ok=True)
        #with open(self.dummy_cache_path, "w") as f:
        #    json.dump([{"name": "test-revision-1", "create_time": "2023-01-01T00:00:00Z", "image": "test-image-1"}], f)

    def tearDown(self):
        pass
        # Clean uptest-cloud-run the temporary cache directory
        #Path(self.temp_cache_dir.name).replace(self.original_cache_dir)
        #self.temp_cache_dir.cleanup()

        # @patch("lib.ricc_cloud_run.run_v2.RevisionsClient")
    def doesnt_work_test_get_cloud_run_revisions_success_api(self, mock_revisions_client):
        """Test successful API call to get Cloud Run versions."""
        # Mock the RevisionsClient and its list_revisions method
        mock_revision = MagicMock(spec=run_v2.Revision)
        mock_revision.name = "projects/test-project/locations/test-region/services/test-service/revisions/test-revision-1"
        mock_revision.create_time = MagicMock(rfc3339=lambda: "2023-01-01T00:00:00Z")
        mock_revision.containers = [MagicMock(image="test-image-1")]
        mock_revisions_client.return_value.list_revisions.return_value = [mock_revision]

        result = get_cloud_run_revisions("test-project", "test-region", "test-service", ignore_cache=True)

        self.assertEqual(result["status"], "success_api")
        self.assertEqual(len(result["revisions"]), 1)
        self.assertEqual(result["revisions"][0]["name"], "test-revision-1")

    #@patch("lib.ricc_cloud_run.run_v2.RevisionsClient")
    def doesnt_work_test_get_cloud_run_revisions_not_found(self, mock_revisions_client):
        """Test handling of service not found."""
        # Mock the RevisionsClient to raise a NotFound exception
        mock_revisions_client.return_value.list_revisions.side_effect = NotFound("Service not found")

        result = get_cloud_run_revisions("test-project", "test-region", "test-service", ignore_cache=True)

        self.assertEqual(result["status"], "error")
        self.assertIn("not found", result["message"].lower())

    #@patch("lib.ricc_cloud_run.run_v2.RevisionsClient")
    def doesnt_work_test_get_cloud_run_revisions_success_cache(self, mock_revisions_client):
        """Test successful retrieval of Cloud Run versions from cache."""
        # Mock the RevisionsClient and its list_revisions method
        mock_revision = MagicMock(spec=run_v2.Revision)
        mock_revision.name = "projects/test-project/locations/test-region/services/test-service/revisions/test-revision-1"
        mock_revision.create_time = MagicMock(rfc3339=lambda: "2023-01-01T00:00:00Z")
        mock_revision.containers = [MagicMock(image="test-image-1")]
        mock_revisions_client.return_value.list_revisions.return_value = [mock_revision]

        result = get_cloud_run_revisions("test-project", "test-region", "test-service", ignore_cache=False)

        self.assertEqual(result["status"], "success_cache")
        self.assertEqual(len(result["revisions"]), 1)
        self.assertEqual(result["revisions"][0]["name"], "test-revision-1")

    #@patch("lib.ricc_cloud_run.run_v2.RevisionsClient")
    def doesnt_work_test_get_cloud_run_revisions_api_error(self, mock_revisions_client):
        """Test handling of generic API error."""
        # Mock the RevisionsClient to raise a generic exception
        mock_revisions_client.return_value.list_revisions.side_effect = Exception("Generic API error")

        result = get_cloud_run_revisions("test-project", "test-region", "test-service", ignore_cache=True)

        self.assertEqual(result["status"], "error")
        self.assertIn("failed to list revisions", result["message"].lower())

    def doesnt_work_test_get_cloud_run_revisions_cache_expired(self):
        """Test handling of expired cache."""
        # Create an expired cache file
        expired_cache_path = _get_cache_path("test-project", "test-region", "test-service", data_type="versions.json")
        expired_cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(expired_cache_path, "w") as f:
            json.dump([{"name": "test-revision-1", "create_time": "2023-01-01T00:00:00Z", "image": "test-image-1"}], f)
        # Modify the file's modification time to be older than the cache obsolescence time
        os.utime(expired_cache_path, (time.time() - 3601, time.time() - 3601))

        # Check if the cache is considered invalid
        self.assertFalse(_is_cache_valid(expired_cache_path))

        # Clean up the expired cache file
        os.remove(expired_cache_path)

    #@patch("lib.ricc_cloud_run.run_v2.RevisionsClient")
    def test_invoke_revisions_on_well_known_gemni_news_crawler_prod_endpoint(self):
        cloudrun_region = 'europe-west1'
        project = 'palladius-genai'
        service = 'gemini-news-crawler-prod'
        current_revisions = 20 # total: 186
        ret = get_cloud_run_revisions(project, cloudrun_region, service, max_results=20, ignore_cache=True)
        #print(ret)
        self.assertEqual(ret["status"], "success_api")
        self.assertEqual(len(ret["revisions"]), current_revisions) # as of 3apr25, there are 186 revisions :)

    #   get_cloud_run_logs
    def test_invoke_logs_on_well_known_last_revision(self):
        cloudrun_region = 'europe-west1'
        project = 'palladius-genai'
        service = 'gemini-news-crawler-prod'
        expected_last_revision_name = 'gemini-news-crawler-prod-00186-lls'
        revisions_ret = get_cloud_run_revisions(project, cloudrun_region, service, max_results=1, ignore_cache=True)
        self.assertEqual(revisions_ret["status"], "success_api")
        self.assertEqual(len(revisions_ret["revisions"]), 1)
        last_revision_name = revisions_ret["revisions"][0]["name"]
        #print(f"revisions={revisions}")
        self.assertEqual(last_revision_name, expected_last_revision_name)
        logs = get_cloud_run_logs(project, cloudrun_region, service, last_revision_name, ignore_cache=True)
        self.assertEqual(logs["status"], "success_api")
        self.assertIn("logs", logs)




if __name__ == "__main__":
    unittest.main()
