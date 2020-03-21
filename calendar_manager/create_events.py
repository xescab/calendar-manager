import json
from datetime import datetime, timedelta, date, time
from cal_setup import get_calendar_service
from read_gspread import open_calendar_worksheet, read_month, get_event_templates, get_caregivers

# https://developers.google.com/calendar/v3/reference/events
TIMEZONE = 'Europe/Madrid'
CALENDAR = '0nv7r8l3d0h9vp2av45nudjj5s@group.calendar.google.com'


def get_caregiver_name(caregiver_code, caregivers):
    return caregivers[caregiver_code]['name']

def get_caregiver_color(caregiver_code, caregivers):
    return caregivers[caregiver_code]['color']


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
                print("Found event '{}' with id {} created by {}".format(event['summary'], event['id'], event['creator']['email']))
                return event['id']

        except KeyError:
            # skip manually created events which will not have the extendedProperty template_name
            continue

    return None


def create_event(service, event_template, event_date, event_color):

    event_body={
        "extendedProperties": { "private": { "template_name": event_template.name } },
        "summary": event_template.summary,
        "description": event_template.description,
        "start": all_day_event(event_date) if event_template.all_day else event_datetime(event_date, event_template.start_time),
        "end": all_day_event(event_date) if event_template.all_day else event_datetime(event_date, event_template.end_time),
        "colorId": event_color,
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


def delete_event(service, event_template, event_date):
    """Delete event created on `event_date` based on `event_template`.
    """
    event_id = get_event_id(service, event_template, event_date)

    if event_id:
        print("Deleting event '{}' with id {} ...".format(event_template.summary, event_id))
        event_result = service.events().delete(calendarId=CALENDAR, eventId=event_id).execute()
    else:
        print("DEBUG: Event '{}' not found. Not deleted.".format(event_template.summary))


def schedule_events(year, month, custody_days, event_templates, caregivers):

    cal = get_calendar_service()

    for day, caregiver_code in custody_days.items():
        event_date = date(year, month, int(day))
        caregiver = get_caregiver_name(caregiver_code,caregivers)
        color = get_caregiver_color(caregiver_code,caregivers)
        weekday = event_date.weekday()

        print("Schedule events for {}. Caregiver is {}. Weekday is {}".format(event_date, caregiver, weekday))

        # Schedule events for templates that match current weekday and caregiver
        for event_tmpl in event_templates:
            print(event_tmpl)
            if weekday in event_tmpl.weekdays and caregiver_code in event_tmpl.caregivers:
                print("DEBUG: {} matches weekday {}".format(event_tmpl.name, weekday))
                print("DEBUG: {} matches caregiver {}".format(event_tmpl.name, caregiver_code))
                create_event(cal, event_tmpl, event_date, color)
            else:
                print("DEBUG: {} does not match weekday {} or caregiver {}".format(event_tmpl.name, weekday, caregiver_code))
                delete_event(cal, event_tmpl, event_date)

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


def schedule_events_from_spreadsheet(calendar_file_name, calendar_school_period, month_name):

    cal_sheet = open_calendar_worksheet(calendar_file_name, calendar_school_period)
    all_cells = cal_sheet.get_all_values()

    caregivers = get_caregivers(all_cells)
    event_templates = get_event_templates(all_cells)
    month_data = read_month(all_cells, calendar_school_period, month_name)
    print(json.dumps(month_data, sort_keys=True, indent=4))

    schedule_events(month_data['year'], month_data['month'], month_data['days'], event_templates, caregivers)
