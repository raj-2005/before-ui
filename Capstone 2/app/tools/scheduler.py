# app/tools/scheduler.py

import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def schedule_task(task_name: str, time_str: str) -> str:
    creds = None
    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        # Create the event object
        # Google expects ISO format: YYYY-MM-DDTHH:MM:SSZ
        start_time = time_str.replace(" ", "T") + ":00"
        
        event = {
            'summary': task_name,
            'description': 'Scheduled by Gemini AI Agent',
            'start': {
                'dateTime': start_time,
                'timeZone': 'UTC', # Change to your timezone, e.g., 'Asia/Kolkata'
            },
            'end': {
                'dateTime': start_time, # You can add duration logic here
                'timeZone': 'UTC',
            },
        }

        event = service.events().insert(calendarId='primary', body=event).execute()
        return f"✅ Task scheduled in Google Calendar! Link: {event.get('htmlLink')}"

    except Exception as e:
        return f"Error connecting to Google Calendar: {str(e)}"