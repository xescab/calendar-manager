import pytest
from calendar_manager.event_template import EventTemplate
from calendar_manager.event_scheduler import EventScheduler


# Define test data common for all tests

test_calendar_id = '0nv7r8l3d0h9vp2av45nudjj5s@group.calendar.google.com'
test_calendar_timezone = 'Europe/Madrid'
test_event_templates = [
    # name, summary, description, datetypes, weekdays, start_time=None, end_time=None
    EventTemplate('all_weekdays','Work day', '', ["A","B"], [0,1,2,3,4]),
    EventTemplate('sport_activity','Sports', 'Sports on Tue and Thu weekdays', ["A","B"], [1,3], '17:00', '19:00'),
    EventTemplate('sunday_service','Sunday service', 'Sunday service at Rev. place', ["AWE"], [6], '12:00', '13:25'),
]
test_date_types = {
    "A" : { "name": "Weekday A", "color": "1" },
    "AWE" : { "name": "Weekend A", "color": "2" },
    "B" : { "name": "Weekday B", "color": "3" },
    "BWE" : { "name": "Weekend B", "color": "4" },
}
test_event_data = {
    "caregivers": {
        "A": 11,
        "AWE": 5,
        "B": 8,
        "BWE": 6
    },
    "days": {
        "1": "A",
        "10": "BWE",
        "11": "BWE",
        "12": "BWE",
        "13": "BWE",
        "14": "A",
        "15": "A",
        "16": "A",
        "17": "A",
        "18": "AWE",
        "19": "AWE",
        "2": "A",
        "20": "B",
        "21": "B",
        "22": "B",
        "23": "B",
        "24": "B",
        "25": "BWE",
        "26": "AWE",
        "27": "A",
        "28": "A",
        "29": "A",
        "3": "A",
        "30": "A",
        "4": "AWE",
        "5": "AWE",
        "6": "B",
        "7": "B",
        "8": "B",
        "9": "BWE"
    },
    "month": 4,
    "weeks": [
        {
            "1": "A",
            "2": "A",
            "3": "A",
            "4": "AWE",
            "5": "AWE",
            "week_number": "14"
        },
        {
            "10": "BWE",
            "11": "BWE",
            "12": "BWE",
            "6": "B",
            "7": "B",
            "8": "B",
            "9": "BWE",
            "week_number": "15"
        },
        {
            "13": "BWE",
            "14": "A",
            "15": "A",
            "16": "A",
            "17": "A",
            "18": "AWE",
            "19": "AWE",
            "week_number": "16"
        },
        {
            "20": "B",
            "21": "B",
            "22": "B",
            "23": "B",
            "24": "B",
            "25": "BWE",
            "26": "AWE",
            "week_number": "17"
        },
        {
            "27": "A",
            "28": "A",
            "29": "A",
            "30": "A",
            "week_number": "18"
        }
    ],
    "year": 2020
}

# NOTE: these tests will only work if you have credentials set, as they involve Google API calls
test_scheduler = EventScheduler('test_creds.json', test_calendar_id, test_calendar_timezone, test_event_templates, test_date_types, test_event_data)

def test_list_upcoming_events_from_today():
    # No upcoming events should be returned when testing from future
    assert test_scheduler.list_upcoming_events() == []

def test_list_upcoming_events_from_date():
    # At least 1 result should be listed
    # FIXME 3 according to current events on calendar!
    assert len(test_scheduler.list_upcoming_events(start_date='2020-04-30')) == 3

def test_list_events_to_be_scheduled(capsys):
    test_scheduler.list_events_to_be_scheduled()
    captured = capsys.readouterr()
    assert "Sun 2020-04-19: 12:00:00 Sunday service" in captured.out
    assert "Tue 2020-04-21: All day Work day, 17:00:00 Sports" in captured.out
    assert "Wed 2020-04-22: All day Work day, 17:00:00 Sports" not in captured.out

# TODO: add more tests!