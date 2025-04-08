from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import datetime
import os

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def get_calendar_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        print("🌐 Opening browser for Google login...")
        creds = flow.run_local_server(port=8080)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('calendar', 'v3', credentials=creds)
    return service

# 建立測試事件
def create_test_event():
    service = get_calendar_service()
    now = datetime.datetime.utcnow()
    start_time = now.isoformat() + 'Z'
    end_time = (now + datetime.timedelta(hours=1)).isoformat() + 'Z'

    event = {
        'summary': '🔬 Lab Booking Test',
        'start': {'dateTime': start_time, 'timeZone': 'Asia/Taipei'},
        'end': {'dateTime': end_time, 'timeZone': 'Asia/Taipei'},
    }

    created_event = service.events().insert(calendarId='primary', body=event).execute()
    print('✅ Event created:', created_event.get('htmlLink'))

create_test_event()
