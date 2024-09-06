import re, requests
import src.logger as logger
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from src.models import ZoomClientConfig, db
from flask import current_app

class ZoomOAuth:
    TOKEN_URL = "https://zoom.us/oauth/token"

    def __init__(self):
        self.config = self.get_config()
        self.access_token = None
        self.token_expiry = None

    @staticmethod
    def get_config():
        return ZoomClientConfig.query.first()

    def get_access_token(self):
        if self.access_token and self.token_expiry and datetime.now() < self.token_expiry:
            return self.access_token

        config = self.get_config()
        if not config:
            raise ValueError("Zoom client configuration not found in the database")

        data = {
            "grant_type": "account_credentials",
            "account_id": config.zoom_account_id,
            "client_id": config.zoom_client_id,
            "client_secret": config.zoom_client_secret
        }

        response = requests.post(self.TOKEN_URL, data=data)
        response.raise_for_status()
        token_data = response.json()

        self.access_token = token_data["access_token"]
        self.token_expiry = datetime.now() + timedelta(seconds=token_data["expires_in"])

        return self.access_token

class ZoomClient:
    BASE_URL = "https://api.zoom.us/v2"

    def __init__(self):
        self.oauth = ZoomOAuth()

    def _get_headers(self):
        return {
            "Authorization": f"Bearer {self.oauth.get_access_token()}",
            "Content-Type": "application/json"
        }

    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict:
        url = f"{self.BASE_URL}/{endpoint}"
        response = requests.request(method, url, headers=self._get_headers(), params=params, json=data)
        response.raise_for_status()
        return response.json()

def get_zoom_client():
    try:
        with current_app.app_context():
            return ZoomClient()
    except Exception as e:
        logger.log(f"Error creating ZoomClient: {str(e)}")
        raise

def get_meeting_recordings(meeting_id: str) -> Dict:
    """
    Retrieve the cloud recordings for a specific meeting.
    """
    client = get_zoom_client()
    endpoint = f"meetings/{meeting_id}/recordings"
    logger.log(f"Getting transcript for meeting {meeting_id}")
    return client._make_request("GET", endpoint)

def get_meeting_details(meeting_id: str) -> Dict:
    """
    Retrieve details for a specific meeting, including potential LMS context.
    """
    client = get_zoom_client()
    endpoint = f"meetings/{meeting_id}"
    meeting_details = client._make_request("GET", endpoint)

    # Look for course ID in various potential locations
    course_id = None

    # Check custom fields
    custom_fields = meeting_details.get('settings', {}).get('custom_fields', [])
    for field in custom_fields:
        if field.get('name', '').lower() in ['course_id', 'canvas_course_id', 'lms_course_id']:
            course_id = field.get('value')
            break

    # Check tracking fields
    tracking_fields = meeting_details.get('tracking_fields', [])
    for field in tracking_fields:
        if field.get('field', '').lower() in ['course_id', 'canvas_course_id', 'lms_course_id']:
            course_id = field.get('value')
            break

    # Check topic and agenda for course ID pattern
    topic = meeting_details.get('topic', '')
    agenda = meeting_details.get('agenda', '')
    for text in [topic, agenda]:
        match = re.search(r'course[\s_-]?id:?\s*(\w+)', text, re.IGNORECASE)
        if match:
            course_id = match.group(1)
            break

    meeting_details['lms_course_id'] = course_id
    return meeting_details

def find_transcript_file(recording_files: List[Dict]) -> Optional[Dict]:
    """
    Find the transcript file in the list of recording files.
    """
    for file in recording_files:
        if file.get("file_type") == "TRANSCRIPT":
            return file
    return None

def get_transcript_content(transcript_download_url: str, access_token: str) -> str:
    """
    Download and return the content of the transcript file.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(transcript_download_url, headers=headers)
    response.raise_for_status()
    return response.text

def get_meeting_transcript(meeting_id: str) -> Optional[str]:
    """
    Retrieve the transcript for a specific meeting.
    """
    client = get_zoom_client()
    recordings = get_meeting_recordings(meeting_id)
    recording_files = recordings.get("recording_files", [])
    
    transcript_file = find_transcript_file(recording_files)
    if not transcript_file:
        return None
    
    download_url = transcript_file.get("download_url")
    if not download_url:
        return None
    
    return get_transcript_content(download_url, client.oauth.get_access_token())

def extract_canvas_course_id(meeting_details: Dict) -> Optional[str]:
    """
    Attempt to extract Canvas course ID from meeting details.
    """
    # Check the topic for course ID
    topic = meeting_details.get("topic", "")
    topic_match = re.search(r"Canvas Course ID: (\d+)", topic)
    if topic_match:
        return topic_match.group(1)
    
    # Check the agenda for course ID
    agenda = meeting_details.get("agenda", "")
    agenda_match = re.search(r"Canvas Course ID: (\d+)", agenda)
    if agenda_match:
        return agenda_match.group(1)
    
    # Check custom attributes if available
    settings = meeting_details.get("settings", {})
    custom_attributes = settings.get("custom_keys", [])
    for attr in custom_attributes:
        if attr.get("key") == "canvas_course_id":
            return attr.get("value")
    
    return None

def get_meeting_with_lms_context(meeting_id: str) -> Dict:
    """
    Retrieve meeting details and attempt to extract LMS context.
    """
    client = get_zoom_client()
    meeting_details = get_meeting_details(meeting_id)
    
    result = {
        "meeting_details": meeting_details,
        "canvas_course_id": meeting_details.get('lms_course_id')
    }
    
    return result