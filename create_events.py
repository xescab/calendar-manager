from datetime import datetime, timedelta, date, time
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

        if 'X' in caregiver:
            summary = 'Dad'
        elif 'A' in caregiver:
            summary = 'Mum'

    elif event_type == 'music':
        summary = 'Music'

    elif event_type == 'swimming':
        summary = 'Swimming pool'

    elif event_type == 'theatre':
        summary = 'Theatre'

    return summary


def get_event_description(event_type, caregiver):
    """
    Returns an event description depending on `event_type` and `caregiver`.
    """
    description = 'Event type {} not defined'.format(event_type)

    if event_type == 'custody_day':

        if caregiver == 'X':
            description = 'School day with Dad'
        elif caregiver == 'XD':
            description = 'Non-School day with Dad'
        elif caregiver == 'A':
            description = 'School day with Mum'
        elif caregiver == 'AD':
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


def create_event(service, event_type, event_date, caregiver):

    event_result = service.events().insert(calendarId=CALENDAR,
        body={
            "summary": get_event_summary(event_type, caregiver),
            "description": get_event_description(event_type, caregiver),
            "start": get_event_start(event_type, event_date),
            "end": get_event_end(event_type, event_date),
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
        16: 'A',
        17: 'A',
        18: 'X',
        19: 'A',
        20: 'A',
        21: 'AD',
        22: 'AD',
      }
    }

    service = get_calendar_service()

    for day, caregiver in month_dict['days'].items():
        event_date = date(year, month, day)
        create_event(service, 'custody_day', event_date, caregiver)
        activity = get_activity(event_date)
        if activity:
            create_event(service, activity, event_date, caregiver)


