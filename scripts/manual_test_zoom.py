import sys
import os

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.zoom_handlers import ZoomClient, get_meeting_with_lms_context, get_meeting_transcript
from config import app  # We will need to set the context for running this externally

def main():
    with app.app_context():  # Create an application context
        client = ZoomClient()
        meeting_id = input("Enter a Zoom meeting ID to test: ")

        print("Fetching meeting details and LMS context...")
        meeting_info = get_meeting_with_lms_context(client, meeting_id)
        
        print(f"Meeting Details: {meeting_info['meeting_details']}")
        print(f"Canvas Course ID: {meeting_info['canvas_course_id']}")
        
        print("\nAttempting to retrieve transcript...")
        transcript = get_meeting_transcript(client, meeting_id)
        if transcript:
            print("Transcript retrieved successfully:")
            print(transcript[:500] + "...") # Print first 500 characters
        else:
            print("No transcript found for this meeting.")

if __name__ == "__main__":
    main()