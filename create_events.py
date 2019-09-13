from datetime import datetime, timedelta, date
from cal_setup import get_calendar_service
from read_gspread import get_month_number

# https://developers.google.com/calendar/v3/reference/events
TIMEZONE = 'Europe/Madrid'
CALENDAR = '0nv7r8l3d0h9vp2av45nudjj5s@group.calendar.google.com'


def get_event_summary(event_type, caregiver):
    """
    Returns an event summary depending on `event_type` and `caregiver`.
    """
    summary = 'Event type {} not defined'.format(event_type)

    if event_type == 'custody_day':

        if caregiver == 'X':
            summary = 'School day with Dad'
        elif caregiver == 'XD':
            summary = 'Non-School day with Dad'
        elif caregiver == 'A':
            summary = 'School day with Mum'
        elif caregiver == 'AD':
            summary = 'Non-School day with Mum'

    return summary


def get_event_start(event_type, event_datetime):
    """
    Returns the start nested object based on `event_type` and the event date.
    """
    start = { "date": event_datetime.isoformat(), "timeZone": TIMEZONE }

    if event_type == 'custody_day':
        start = { "date": event_datetime.isoformat(), "timeZone": TIMEZONE }

    return start


def get_event_end(event_type, event_datetime):
    """
    Returns the end nested object based on `event_type` and the event date.
    """
    end = { "date": event_datetime.isoformat(), "timeZone": TIMEZONE }

    if event_type == 'custody_day':
        end = { "date": event_datetime.isoformat(), "timeZone": TIMEZONE }

    return end


def create_event(service, event_type, year, month, day, caregiver, hour=None, minute=None):

    if hour and minute:
        event_datetime = datetime(year, month, day, hour, minute)
    else:
        event_datetime = date(year, month, day)

    event_result = service.events().insert(calendarId=CALENDAR,
        body={
            "summary": get_event_summary(event_type, caregiver),
            "description": get_event_summary(event_type, caregiver),
            "start": get_event_start(event_type, event_datetime),
            "end": get_event_end(event_type, event_datetime),
        }
    ).execute()

    print("created event")
    print("id: ", event_result['id'])
    print("summary: ", event_result['summary'])
    print("starts at: ", event_result['start'])
    print("ends at: ", event_result['end'])


if __name__ == '__main__':

    year  = 2019
    month = get_month_number('September')

    month_dict = {
      'days': {
        12: 'A',
        13: 'X',
        14: 'XD',
        15: 'XD',
        16: 'A',
      }
    }

    service = get_calendar_service()

    for day, caregiver in month_dict['days'].items():
        create_event(service, 'custody_day', year, month, day, caregiver)

