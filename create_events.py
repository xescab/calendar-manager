from datetime import datetime, timedelta, date, time
from cal_setup import get_calendar_service
from read_gspread import get_month_number

# https://developers.google.com/calendar/v3/reference/events
TIMEZONE = 'Europe/Madrid'
CALENDAR = '0nv7r8l3d0h9vp2av45nudjj5s@group.calendar.google.com'


def is_schoolday(caregiver_code):
    return 'D' not in caregiver_code


def get_event_caregiver(caregiver_code):
    if 'X' in caregiver_code:
        return 'Dad'
    elif 'A' in caregiver_code:
        return 'Mum'


def get_event_summary(event_type, caregiver_code):
    """
    Returns an event summary depending on `event_type` and `caregiver_code`.
    """
    summary = 'Event type {} not defined'.format(event_type)

    if event_type == 'custody_day':
        summary = get_event_caregiver(caregiver_code)

    elif event_type == 'music':
        summary = 'Music'

    elif event_type == 'swimming':
        summary = 'Swimming'

    elif event_type == 'theatre':
        summary = 'Theatre'

    return summary


def get_event_description(event_type, caregiver_code):
    """
    Returns an event description depending on `event_type` and `caregiver_code`.
    """
    description = 'Event type {} not defined'.format(event_type)

    if event_type == 'custody_day':

        if caregiver_code == 'X':
            description = 'School day with Dad'
        elif caregiver_code == 'XD':
            description = 'Non-School day with Dad'
        elif caregiver_code == 'A':
            description = 'School day with Mum'
        elif caregiver_code == 'AD':
            description = 'Non-School day with Mum'

    elif event_type == 'music':
        description = 'Music class'

    elif event_type == 'swimming':
        description = 'Swimming pool class'

    elif event_type == 'theatre':
        description = 'Theatre class'

    return description


def get_event_start(event_type, event_date):
    """
    Returns the start nested object based on `event_type` and the event date.
    """
    start = { "date": event_date.isoformat(), "timeZone": TIMEZONE }

    if event_type == 'custody_day':
        start = { "date": event_date.isoformat(), "timeZone": TIMEZONE }
    elif event_type == 'music':
        start = { "dateTime": datetime.combine(event_date, time(16,30)).isoformat(), "timeZone": TIMEZONE }
    elif event_type == 'theatre':
        start = { "dateTime": datetime.combine(event_date, time(16,30)).isoformat(), "timeZone": TIMEZONE }
    elif event_type == 'swimming':
        start = { "dateTime": datetime.combine(event_date, time(16,30)).isoformat(), "timeZone": TIMEZONE }

    return start


def get_event_end(event_type, event_date):
    """
    Returns the end nested object based on `event_type` and the event date.
    """
    end = { "date": event_date.isoformat(), "timeZone": TIMEZONE }

    if event_type == 'custody_day':
        end = { "date": event_date.isoformat(), "timeZone": TIMEZONE }
    elif event_type == 'music':
        end = { "dateTime": datetime.combine(event_date, time(17,30)).isoformat(), "timeZone": TIMEZONE }
    elif event_type == 'theatre':
        end = { "dateTime": datetime.combine(event_date, time(17,30)).isoformat(), "timeZone": TIMEZONE }
    elif event_type == 'swimming':
        end = { "dateTime": datetime.combine(event_date, time(18,20)).isoformat(), "timeZone": TIMEZONE }

    return end


def get_activity(event_date):
    weekday = event_date.weekday()
    if weekday == 0:    # Monday
        return 'music'
    elif weekday == 1:  # Tuesday
        return 'swimming'
    elif weekday == 3:  # Thursday
        return 'theatre'
    return None


def get_event_id(service, event_date, event_summary):
    """Look for existing events with `event_summary` on `event_date`
    """
    events_result = service.events().list(calendarId=CALENDAR,
                                        timeMin=datetime.combine(event_date, time(0,0)).isoformat() + 'Z',
                                        timeMax=datetime.combine(event_date, time(23,59)).isoformat() + 'Z',
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    for event in events:
        if event['summary'] == event_summary:
            print("Found similar event '{}' with id {} created by {}".format(event['summary'], event['id'], event['creator']['email']))
            return event['id']

    return None


def create_event(service, event_type, event_date, caregiver_code):

    # Get existing event_id
    event_summary = get_event_summary(event_type, caregiver_code)
    event_id = get_event_id(service, event_date, event_summary)

    # Define body of event
    event_body={
        "summary": event_summary,
        "description": get_event_description(event_type, caregiver_code),
        "start": get_event_start(event_type, event_date),
        "end": get_event_end(event_type, event_date),
    }

    if event_id:
        event_result = service.events().update(calendarId=CALENDAR, eventId=event_id, body=event_body).execute()
    else:
        event_result = service.events().insert(calendarId=CALENDAR, body=event_body).execute()

    print("created/updated event")
    print("id: ", event_result['id'])
    print("summary: ", event_result['summary'])
    print("starts at: ", event_result['start'])
    print("ends at: ", event_result['end'])
    print("")


if __name__ == '__main__':

    year  = 2019
    month = get_month_number('September')

    month_dict = {
      'days': {
        16: 'A',
        17: 'A',
        18: 'X',
        19: 'A',
        20: 'A',
        21: 'AD',
        22: 'AD',
        23: 'X',
        24: 'XD',
      }
    }

    service = get_calendar_service()

    for day, caregiver_code in month_dict['days'].items():
        event_date = date(year, month, day)
        event_caregiver = get_event_caregiver(caregiver_code)

        print("{}'s caregiver is {}".format(event_date, event_caregiver))
        create_event(service, 'custody_day', event_date, caregiver_code)

        if is_schoolday(caregiver_code):
            print("{} is a school day. Creating activity and transport events.\n".format(event_date))
            #create_event_transport_morning
            activity = get_activity(event_date)
            if activity:
                create_event(service, activity, event_date, caregiver_code)
                #create_event_transport_evening
        else:
            print("{} is NOT a school day. Skipping activity and transport events.\n".format(event_date))
