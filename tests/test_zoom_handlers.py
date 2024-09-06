import unittest
from unittest.mock import patch, MagicMock
from zoom_handlers import ZoomClient, ZoomOAuth, get_meeting_recordings, get_meeting_transcript, extract_canvas_course_id
from models import ZoomClientConfig

class TestZoomHandlers(unittest.TestCase):

    def setUp(self):
        self.mock_config = ZoomClientConfig(
            zoom_client_id="mock_client_id",
            zoom_client_secret="mock_client_secret",
            zoom_account_id="mock_account_id"
        )

    @patch('zoom_handlers.ZoomOAuth.get_config')
    @patch('requests.post')
    def test_zoom_oauth_get_access_token(self, mock_post, mock_get_config):
        mock_get_config.return_value = self.mock_config
        mock_post.return_value.json.return_value = {
            "access_token": "mock_access_token",
            "expires_in": 3600
        }

        oauth = ZoomOAuth()
        token = oauth.get_access_token()

        self.assertEqual(token, "mock_access_token")
        mock_post.assert_called_once()

    @patch('zoom_handlers.ZoomClient._make_request')
    def test_get_meeting_recordings(self, mock_make_request):
        mock_make_request.return_value = {"recording_files": [{"id": "123", "file_type": "TRANSCRIPT"}]}
        
        client = ZoomClient()
        result = get_meeting_recordings(client, "mock_meeting_id")

        self.assertEqual(result["recording_files"][0]["id"], "123")
        mock_make_request.assert_called_once_with("GET", "meetings/mock_meeting_id/recordings")

    def test_extract_canvas_course_id(self):
        meeting_details = {
            "topic": "Meeting for Canvas Course ID: 12345",
            "agenda": "Discuss project for Canvas Course",
            "settings": {
                "custom_keys": [
                    {"key": "canvas_course_id", "value": "67890"}
                ]
            }
        }

        course_id = extract_canvas_course_id(meeting_details)
        self.assertEqual(course_id, "12345")

        # Test with course ID in custom attributes
        meeting_details["topic"] = "Regular meeting"
        course_id = extract_canvas_course_id(meeting_details)
        self.assertEqual(course_id, "67890")

        # Test with no course ID
        meeting_details["settings"]["custom_keys"] = []
        course_id = extract_canvas_course_id(meeting_details)
        self.assertIsNone(course_id)

if __name__ == '__main__':
    unittest.main()