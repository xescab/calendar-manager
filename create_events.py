import json
from datetime import datetime, timedelta, date, time
from cal_setup import get_calendar_service
from read_gspread import open_calendar_worksheet, read_month, get_event_templates

# https://developers.google.com/calendar/v3/reference/events
TIMEZONE = 'Europe/Madrid'
CALENDAR = '0nv7r8l3d0h9vp2av45nudjj5s@group.calendar.google.com'


def get_caregiver_name(caregiver_code):
    if 'X' in caregiver_code:
        return 'Dad'
    elif 'A' in caregiver_code:
        return 'Mum'


def all_day_event(event_date):
    return { "date": event_date.isoformat(), "timeZone": TIMEZONE }


def event_datetime(event_date, event_time):
    return { "dateTime": datetime.combine(event_date, event_time).isoformat(), "timeZone": TIMEZONE }


def get_event_id(service, event_template, event_date):
    """Look for existing events with `event_summary` on `event_date`
    """
    events_result = service.events().list(calendarId=CALENDAR,
                                        timeMin=datetime.combine(event_date, time(0,0)).isoformat() + 'Z',
                                        timeMax=datetime.combine(event_date, time(23,59)).isoformat() + 'Z',
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    for event in events:
        try:
            if event['extendedProperties']['private']['template_name'] == event_template.name:
                print("Found existing event '{}' with id {} created by {}".format(event['summary'], event['id'], event['creator']['email']))
                return event['id']

        except KeyError:
            continue

    return None


def create_event(service, event_template, event_date):

    event_body={
        "extendedProperties": { "private": { "template_name": event_template.name } },
        "summary": event_template.summary,
        "description": event_template.description,
        "start": all_day_event(event_date) if event_template.all_day else event_datetime(event_date, event_template.start_time),
        "end": all_day_event(event_date) if event_template.all_day else event_datetime(event_date, event_template.end_time),
    }

    print("Scheduling event '{}' ...".format(event_template.summary))
    event_id = get_event_id(service, event_template, event_date)

    if event_id:
        print("Updating existing event {} ...".format(event_id))
        event_result = service.events().update(calendarId=CALENDAR, eventId=event_id, body=event_body).execute()
    else:
        print("Creating new event ...")
        event_result = service.events().insert(calendarId=CALENDAR, body=event_body).execute()

    print("id: ", event_result['id'])
    print("summary: ", event_result['summary'])
    print("starts at: ", event_result['start'])
    print("ends at: ", event_result['end'])
    #print("DEBUG: ", event_result)


def schedule_events(year, month, custody_days, event_templates):

    cal = get_calendar_service()

    for day, caregiver_code in custody_days.items():
        event_date = date(year, month, int(day))
        caregiver = get_caregiver_name(caregiver_code)
        weekday = event_date.weekday()

        print("Schedule events for {}. Caregiver is {}. Weekday is {}".format(event_date, caregiver, weekday))

        # Schedule events for templates that match current weekday and caregiver
        for event_tmpl in event_templates:
            print(event_tmpl)
            if weekday in event_tmpl.weekdays:
                print("{} matches weekday {}".format(event_tmpl.name, weekday))
                if caregiver_code in event_tmpl.caregivers:
                    print("{} matches caregiver {}".format(event_tmpl.name, caregiver_code))
                    create_event(cal, event_tmpl, event_date)

        print("-----------------------------------------------")


def schedule_events_from_testdata():

    year  = 2019
    month = 9

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
        25: 'A',
        26: 'X',
        27: 'X',
        28: 'XD',
        29: 'XD',
      }
    }

    calendar_file_name = 'Calendario de custodia compartida Elena'
    calendar_school_period = '2019-2020'

    cal_sheet = open_calendar_worksheet(calendar_file_name, calendar_school_period)
    event_templates = get_event_templates(cal_sheet)

    schedule_events(year, month, month_dict['days'], event_templates)


def schedule_events_from_spreadsheet():

    calendar_file_name = 'Calendario de custodia compartida Elena'
    calendar_school_period = '2019-2020'
    month_name = 'October'

    cal_sheet = open_calendar_worksheet(calendar_file_name, calendar_school_period)

    event_templates = get_event_templates(cal_sheet)
    month_data = read_month(cal_sheet, calendar_school_period, month_name)
    print(json.dumps(month_data, sort_keys=True, indent=4))

    schedule_events(month_data['year'], month_data['month'], month_data['days'], event_templates)


if __name__ == '__main__':

    schedule_events_from_spreadsheet()
