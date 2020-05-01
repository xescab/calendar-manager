import json
import calendar
from datetime import datetime, timedelta, date, time
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials



class EventScheduler():
    """EventScheduler connects to Google Calendar service using credentials 
    from `credentials_filename`.
    
    It uses `calendar_id` and `calendar_timezone` to schedule events based 
    on a list of event templates, event datetypes and event data.

    Event templates can be read from a gspread, but could also be specified
    from somewhere else. They should contain info as the start and end time,
    summary, description, and which weekdays and datetypes they apply to.

    Date types is a list of date types applied to both event templates and data.
    Date types are keywords used to distinguish different kind of dates: holidays,
    weekends, custody days with dad, custody days with mum... Whatever you can imagine.

    Event data is currently a dictionary with year, month, and days which are
    associated to a date type.
    """
    def __init__(self, credentials_filename, calendar_id, calendar_timezone, event_templates, date_types, event_data):

        scope = ['https://www.googleapis.com/auth/calendar']
        creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_filename, scope)
        self.calendar_service = build('calendar', 'v3', credentials=creds)

        self.calendar_id = calendar_id
        self.calendar_timezone = calendar_timezone
        self.event_templates = event_templates
        self.date_types = date_types
        self.event_data = event_data


    def get_event_id(self, event_template, event_date):
        """Look for existing events with same `event_template`.
        We assume a maximum of 10 events per date and we return the first ocurrence.
        """
        events_result = self.calendar_service.events().list(calendarId=self.calendar_id,
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


    def create_event(self, event_template, event_date, event_color):

        def all_day_event(event_date):
            return { "date": event_date.isoformat(), "timeZone": self.calendar_timezone }

        def event_datetime(event_date, event_time):
            return { "dateTime": datetime.combine(event_date, event_time).isoformat(), "timeZone": self.calendar_timezone }

        event_body={
            "extendedProperties": { "private": { "template_name": event_template.name } }, # needed to overwrite existing events
            "summary": event_template.summary,
            "description": event_template.description,
            "start": all_day_event(event_date) if event_template.all_day else event_datetime(event_date, event_template.start_time),
            "end": all_day_event(event_date) if event_template.all_day else event_datetime(event_date, event_template.end_time),
            "colorId": event_color,
        }

        print("Scheduling event '{}' ...".format(event_template.summary))
        event_id = self.get_event_id(event_template, event_date)

        if event_id:
            print("Updating existing event {} ...".format(event_id))
            event_result = self.calendar_service.events().update(calendarId=self.calendar_id, eventId=event_id, body=event_body).execute()
        else:
            print("Creating new event ...")
            event_result = self.calendar_service.events().insert(calendarId=self.calendar_id, body=event_body).execute()

        print("id: ", event_result['id'])
        print("summary: ", event_result['summary'])
        print("starts at: ", event_result['start'])
        print("ends at: ", event_result['end'])
        #print("DEBUG: ", event_result)


    def delete_event(self, event_template, event_date):
        """Delete event created on `event_date` based on `event_template`.
        """
        event_id = self.get_event_id(event_template, event_date)

        if event_id:
            print("Deleting event '{}' with id {} ...".format(event_template.summary, event_id))
            self.calendar_service.events().delete(calendarId=self.calendar_id, eventId=event_id).execute()
        #else:
        #    print("DEBUG: Event '{}' not found. Not deleted.".format(event_template.summary))


    def schedule_events(self):

        year = self.event_data['year']
        month = self.event_data['month']
        custody_days = self.event_data['days']

        for day, datetype in custody_days.items():
            event_date = date(year, month, int(day))
            datetype_desc = self.date_types[datetype]['name']
            color = self.date_types[datetype]['color']
            weekday = event_date.weekday()

            print(f"Scheduling events for {calendar.day_abbr[weekday]} {event_date} ({datetype_desc}) ...")

            # Schedule events for templates that match current weekday and datetype
            # and delete those that no longer match
            for event_tmpl in self.event_templates:
                if weekday in event_tmpl.weekdays and datetype in event_tmpl.datetypes:
                    #print("DEBUG: {} matches weekday {}".format(event_tmpl.name, weekday))
                    #print("DEBUG: {} matches datetype {}".format(event_tmpl.name, datetype))
                    self.create_event(event_tmpl, event_date, color)
                else:
                    #print("DEBUG: {} does not match weekday {} or datetype {}".format(event_tmpl.name, weekday, datetype))
                    self.delete_event(event_tmpl, event_date)

            print("-----------------------------------------------")


    def list_upcoming_events(self, start_date=datetime.today().isoformat(), max_results=10): 
        """Lists upcoming events starting from date `start_date` (by default `today`).
        """
        start_datetime=datetime.fromisoformat(start_date).isoformat() + 'Z' # 'Z' indicates UTC time
        print(f"Getting (max {max_results}) upcoming events from {start_date} ...")
        events_result = self.calendar_service.events().list(calendarId=self.calendar_id,
                                            timeMin=start_datetime,
                                            maxResults=max_results, singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])

        return events


    def list_events_to_be_scheduled(self):
        """Lists events to be scheduled as per event data loaded when initialized.
        """
        year = self.event_data['year']
        month = self.event_data['month']

        # Print calendar view for a general overview
        print(f"\nPreview of events to be scheduled:\n")
        print(calendar.month(year, month))

        for day, dtype in self.event_data['days'].items():
            event_date = date(year, month, int(day))
            weekday = event_date.weekday()

            events = ", ".join(f"{tmpl.start_time} {tmpl.summary}" for tmpl in self.event_templates if weekday in tmpl.weekdays and dtype in tmpl.datetypes)
            print(f"{calendar.day_abbr[weekday]} {event_date}: {events}")


    def print_datetype_distribution(self):
        print(f"\nEvents distribution:\n")
        for datetype in self.date_types.keys():
            print(f" * {self.date_types[datetype]['name']} got {self.event_data['caregivers'][datetype]} days")