from config import app
from flask import json, request, abort, current_app, jsonify
from src.models import ZoomClientConfig
import src.logger as logger
import re, requests
from requests.exceptions import HTTPError
from typing import Dict, List, Optional
from datetime import datetime, timedelta

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

        try:
            response = requests.post(self.TOKEN_URL, data=data)
            response.raise_for_status()
            token_data = response.json()

            self.access_token = token_data["access_token"]
            self.token_expiry = datetime.now() + timedelta(seconds=token_data["expires_in"])

            return self.access_token
        except HTTPError as http_err:
            if response.status_code == 400:
                error_message = "Failed to obtain Zoom access token. Please check your Zoom credentials and ensure your Marketplace App is activated."
                logger.log(f"{error_message} Details: {response.text}")
                raise ZoomAuthenticationError(error_message) from http_err
            else:
                logger.log(f"HTTP error occurred: {http_err}")
                raise
        except Exception as err:
            logger.log(f"An error occurred while obtaining Zoom access token: {err}")
            raise
            
class ZoomAuthenticationError(Exception):
    """Custom exception for Zoom authentication errors."""
    pass

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
        with app.app_context():
            zoom_config = ZoomClientConfig.query.get(1)
            if not zoom_config:
                raise ValueError("Zoom client configuration not found in the database")
        return ZoomClient()
    except Exception as e:
        logger.log(f"Error creating ZoomClient: {str(e)}")
        raise

def get_meeting_recordings(meeting_id: str) -> Dict:
    """
    Retrieve the cloud recordings for a specific meeting.
    """
    try:
        verify_access_key()
        client = get_zoom_client()
        endpoint = f"meetings/{meeting_id}/recordings"
        logger.log(f"Getting recordings for meeting {meeting_id}")
        return client._make_request("GET", endpoint)
    except ZoomAuthenticationError as auth_err:
        logger.log(f"Zoom authentication error: {str(auth_err)}")
        return jsonify({
            "error": "Zoom Authentication Error",
            "message": str(auth_err),
            "details": "Please check your Zoom credentials and ensure your Marketplace App is activated."
        }), 401
    except Exception as e:
        logger.log(f"Error retrieving meeting recordings: {str(e)}")
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred while retrieving meeting recordings."
        }), 500

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

def get_transcript_content(transcript_download_url: str, access_token: str) -> Optional[str]:
    """
    Download and return the content of the transcript file.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get(transcript_download_url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logger.log(f"Error retrieving transcript: {str(e)}")
        return None

# def get_meeting_transcript(meeting_id: str) -> Optional[str]:
#     """
#     Retrieve the transcript for a specific meeting.
#     """
#     client = get_zoom_client()
#     recordings = get_meeting_recordings(meeting_id)
#     recording_files = recordings.get("recording_files", [])
    
#     transcript_file = find_transcript_file(recording_files)
#     if not transcript_file:
#         return None
    
#     download_url = transcript_file.get("download_url")
#     if not download_url:
#         return None
    
#     return get_transcript_content(download_url, client.oauth.get_access_token())

def validate_access_key(apikey, required_scopes=None, request=None):
    with app.app_context():
        zoom_config = ZoomClientConfig.query.get(1)
        if zoom_config and zoom_config.require_access_key:
            if apikey and apikey == zoom_config.access_key:
                return {'sub': 'zoom_api_user'}
    return None

def verify_access_key():
    with app.app_context():
        zoom_config = ZoomClientConfig.query.get(1)
        if zoom_config and zoom_config.require_access_key:
            access_key = request.headers.get("X-Access-Key")
            if not validate_access_key(access_key):
                abort(401, description="Invalid or missing Access Key")

def get_meeting_transcript(meeting_id: str) -> Dict[str, Optional[List[Dict[str, str]]]]:
    """
    Retrieve the transcript for a specific meeting and convert it to JSON format.
    """
    try:
        verify_access_key()
        client = get_zoom_client()
        recordings = get_meeting_recordings(meeting_id)

        # Check if recordings is a tuple (error response) or a dict (success response)
        if isinstance(recordings, tuple):
            # This is an error response, return it directly
            return recordings

        recording_files = recordings.get("recording_files", [])
        
        transcript_file = find_transcript_file(recording_files)
        if not transcript_file:
            logger.log(f"No transcript file found for meeting {meeting_id}")
            return {"transcript": None}
        
        download_url = transcript_file.get("download_url")
        if not download_url:
            logger.log(f"No download URL found for transcript of meeting {meeting_id}")
            return {"transcript": None}
        
        webvtt_content = get_transcript_content(download_url, client.oauth.get_access_token())
        if not webvtt_content:
            logger.log(f"Failed to retrieve transcript content for meeting {meeting_id}")
            return {"transcript": None}
        
        json_transcript = json.loads(webvtt_to_json(webvtt_content))
        logger.log(f"Parsed JSON transcript for meeting {meeting_id}")
        
        return {"transcript": json_transcript}
    except ZoomAuthenticationError as auth_err:
        logger.log(f"Zoom authentication error: {str(auth_err)}")
        return jsonify({
            "error": "Zoom Authentication Error",
            "message": str(auth_err),
            "details": "Please check your Zoom credentials and ensure your Marketplace App is activated."
        }), 401
    except Exception as e:
        logger.log(f"Error retrieving meeting transcript: {str(e)}")
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred while retrieving the meeting transcript."
        }), 500

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
    verify_access_key()
    client = get_zoom_client()
    meeting_details = get_meeting_details(meeting_id)
    
    result = {
        "meeting_details": meeting_details,
        "canvas_course_id": meeting_details.get('lms_course_id')
    }
    
    return result

def webvtt_to_json(webvtt_content: str) -> str:
    captions = re.split(r'\r\n\r\n', webvtt_content.strip())
    
    json_data = []
    
    for caption in captions:
        if caption.strip().upper() == 'WEBVTT':
            continue
        
        lines = caption.split('\r\n')
        if len(lines) >= 3:
            index = lines[0]
            timing = lines[1]
            text = ' '.join(lines[2:])
            
            try:
                start, end = timing.split(' --> ')
            except ValueError:
                continue  # Skip this caption if timing is malformed
            
            caption_obj = {
                "index": index,
                "start": start,
                "end": end,
                "text": text
            }
            
            json_data.append(caption_obj)
    
    return json.dumps(json_data, indent=2)