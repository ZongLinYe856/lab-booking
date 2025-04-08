from flask import Flask, render_template, request, redirect, flash
from datetime import datetime, timedelta
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 可改成更安全的字串

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def get_calendar_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=8080)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        instrument = request.form['instrument']
        datetime_str = request.form['datetime']
        duration = int(request.form['duration'])

        try:
            dt_start = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M")
            dt_end = dt_start + timedelta(minutes=duration)

            service = get_calendar_service()
            event = {
                'summary': f'{instrument} Booking - {name}',
                'description': f'Booked by {name} ({email})',
                'start': {'dateTime': dt_start.isoformat(), 'timeZone': 'Asia/Taipei'},
                'end': {'dateTime': dt_end.isoformat(), 'timeZone': 'Asia/Taipei'},
                'attendees': [{'email': email}],
            }
            service.events().insert(calendarId='primary', body=event).execute()
            flash('✅ Booking created and added to Google Calendar.', 'success')
        except Exception as e:
            print("Error:", e)
            flash('❌ Failed to create booking.', 'danger')
    return render_template('index.html')

@app.route('/bookings')
def bookings():
    try:
        service = get_calendar_service()
        events_result = service.events().list(
            calendarId='primary',
            timeMin=datetime.utcnow().isoformat() + 'Z',
            maxResults=50,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])

        booking_list = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', '')
            name = summary.split(" - ")[-1] if " - " in summary else ""
            instrument = summary.split(" Booking")[0] if " Booking" in summary else ""
            booking_list.append({
                'start': start.replace('T', ' ')[:16],
                'instrument': instrument,
                'name': name
            })

        return render_template('bookings.html', bookings=booking_list)
    except Exception as e:
        return f"Error fetching bookings: {e}"
if __name__ == '__main__':
    app.run(debug=True)
