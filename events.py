from datetime import datetime

class EventTemplate:

    def __init__(self, name, summary, description, caregivers, weekdays, start_time=None, end_time=None):
        self.name = name
        self.summary = summary
        self.description = description
        self.weekdays = weekdays
        self.caregivers = caregivers
        if ":" in start_time:
            self.start_time = datetime.strptime(start_time, '%H:%M').time()
        else:
            self.start_time = None
        if ":" in end_time:
            self.end_time = datetime.strptime(end_time, '%H:%M').time()
        else:
            self.end_time = None
        self.all_day = not start_time or not end_time

    def __str__(self):
        return "{}: summary='{}', description='{}', weekdays={}, caregivers={}, start={}, end={}, all_day={}".format(
            self.name,
            self.summary,
            self.description,
            self.weekdays,
            self.caregivers,
            self.start_time if not None else "",
            self.end_time if not None else "",
            self.all_day,
        )
