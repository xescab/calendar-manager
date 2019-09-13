import datetime
from cal_setup import get_calendar_service

# FIXME change to variable
CALENDAR = '0nv7r8l3d0h9vp2av45nudjj5s@group.calendar.google.com'

def main():
    service = get_calendar_service()
    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting List o 10 events')
    events_result = service.events().list(calendarId=CALENDAR, timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])

if __name__ == '__main__':
    main()
