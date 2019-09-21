from datetime import datetime, timedelta, date, time
from cal_setup import get_calendar_service
from read_gspread import open_calendar_worksheet, read_month

# https://developers.google.com/calendar/v3/reference/events
TIMEZONE = 'Europe/Madrid'
CALENDAR = '0nv7r8l3d0h9vp2av45nudjj5s@group.calendar.google.com'


class EventType:

    def __init__(self, summary, description, start_time=None, end_time=None):
        self.summary = summary
        self.description = description
        self.start_time = start_time
        self.end_time = end_time
        self.all_day = not start_time or not end_time



def is_schoolday(caregiver_code):
    return 'D' not in caregiver_code


def get_caregiver_name(caregiver_code):
    if 'X' in caregiver_code:
        return 'Dad'
    elif 'A' in caregiver_code:
        return 'Mum'


def all_day_event(event_date):
    return { "date": event_date.isoformat(), "timeZone": TIMEZONE }


def event_datetime(event_date, event_time):
    return { "dateTime": datetime.combine(event_date, event_time).isoformat(), "timeZone": TIMEZONE }


def get_event_id(service, event_type, event_date):
    """Look for existing events with `event_summary` on `event_date`
    """
    events_result = service.events().list(calendarId=CALENDAR,
                                        timeMin=datetime.combine(event_date, time(0,0)).isoformat() + 'Z',
                                        timeMax=datetime.combine(event_date, time(23,59)).isoformat() + 'Z',
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    for event in events:
        if event['summary'] == event_type.summary:
            print("Found existing event '{}' with id {} created by {}".format(event['summary'], event['id'], event['creator']['email']))
            return event['id']

    return None


def create_event(service, event_type, event_date):

    event_body={
        "summary": event_type.summary,
        "description": event_type.description,
        "start": all_day_event(event_date) if event_type.all_day else event_datetime(event_date, event_type.start_time),
        "end": all_day_event(event_date) if event_type.all_day else event_datetime(event_date, event_type.end_time),
    }

    print("Scheduling event '{}' ...".format(event_type.summary))
    event_id = get_event_id(service, event_type, event_date)

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


def schedule_events(year, month, custody_days):

    # Define event types
    # TODO: include this configuration in Google spreadsheet
    schoolday_mum = EventType('Mum','School day with Mum')
    schoolday_dad = EventType('Dad','School day with Dad')
    nonschoolday_mum = EventType('Mum','Non-School day with Mum')
    nonschoolday_dad = EventType('Dad','Non-School day with Dad')
    act_music = EventType('Music','Music class',time(16,30),time(17,30))
    act_swimming = EventType('Swimming','Swimming pool',time(16,30),time(18,20))
    act_theatre = EventType('Theatre','Theatre class',time(16,30),time(17,30))
    transport_morning = EventType('Ruta 5','Ruta 5 7:45',time(7,40),time(7,50))
    transport_afternoon = EventType('Ruta 3','Ruta 3 17:32',time(17,20),time(17,40))
    transport_activity = EventType('Ruta A','Ruta A 18:53',time(18,50),time(19,0))
    pickup_at_pool = EventType('Pickup','Pickup at pool',time(18,20),time(18,30))
    pickup_at_school = EventType('Pickup','Pickup at school',time(16,0),time(17,0))


    cal = get_calendar_service()

    for day, caregiver_code in custody_days.items():
        event_date = date(year, month, day)
        caregiver = get_caregiver_name(caregiver_code)

        print("Schedule events for {}. Caregiver is {}.".format(event_date,caregiver))

        if is_schoolday(caregiver_code):
            print("It is a school day. We will sechedule activity and transport events.".format(event_date))

            if caregiver == 'Mum':
                create_event(cal,schoolday_mum,event_date)
            else:
                create_event(cal,schoolday_dad,event_date)

            create_event(cal,transport_morning,event_date)

            weekday = event_date.weekday()

            if weekday == 0:    # Monday
                create_event(cal,act_music,event_date)
                create_event(cal,transport_activity,event_date)

            elif weekday == 1:  # Tuesday
                create_event(cal,act_swimming,event_date)
                create_event(cal,pickup_at_pool,event_date)

            elif weekday == 2:  # Wednesday
                if caregiver == 'Mum':
                    create_event(cal,transport_afternoon,event_date)
                else:
                    create_event(cal,pickup_at_school,event_date)

            elif weekday == 3:  # Thursday
                create_event(cal,act_theatre,event_date)
                create_event(cal,transport_activity,event_date)

            elif weekday == 4:  # Friday
                create_event(cal,transport_afternoon,event_date)

        else:
            print("It is NOT a school day. We will skip activity and transport events.".format(event_date))

            if caregiver == 'Mum':
                create_event(cal,nonschoolday_mum,event_date)
            else:
                create_event(cal,nonschoolday_dad,event_date)

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

    schedule_events(year, month, month_dict['days'])


def schedule_events_from_spreadsheet():

    calendar_file_name = 'Calendario de custodia compartida Elena'
    calendar_school_period = '2019-2020'
    month_name = 'September'

    cal = open_calendar_worksheet(calendar_file_name, calendar_school_period)

    month_data = read_month(cal, calendar_school_period, month_name)

    schedule_events(month_data['year'], month_data['month'], month_data['days'])


if __name__ == '__main__':

    schedule_events_from_testdata()
