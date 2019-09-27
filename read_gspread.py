import json
import gspread
import calendar
from oauth2client.service_account import ServiceAccountCredentials
from events import EventTemplate


def merge_weeks(dict_list):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_list:
        result.update(dictionary)
    del result['week_number']
    return result


def open_calendar_worksheet(calendar_file_name, calendar_school_period):
    """Returns a gspread worksheet from file `calendar_file_name` containing
    a calendar for `calendar_school_period` using credentials in `creds.json`.
    """
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    credentials = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)

    gc = gspread.authorize(credentials)

    return gc.open(calendar_file_name).worksheet(calendar_school_period)


def get_month_number(month_name):
    "Returns the number of the month, 0 it the month could not be found"
    for i in range(1,13):
        if calendar.month_name[i] == month_name:
            return i
    return 0


def get_year(calendar_school_period, month_name):
    """Returns the year of the month according to a custom school period, where
    days from July and August are distributed at the beiginning of the school
    period.
    TODO: June is a special month split the weekend just after the school ends.
    """
    (first_year, second_year) = calendar_school_period.split('-')
    return first_year if month_name in ['July','August','September','October','December','November'] else second_year


def read_month(cal, calendar_school_period, month_name):
    """Reads info from worksheet `cal` for a particular month and returns a
    dictionary with the distribution of days.
    """
    month_number = get_month_number(month_name)
    year = int(get_year(calendar_school_period, month_name))

    # Informative
    print(calendar.month(year, month_number))

    # Initiliaze data structure
    month_dict = { 'month': month_number, 'year': year, 'weeks': [] }

    cell_month = cal.find(month_name)
    month_row = cell_month.row
    month_col = cell_month.col

    for week_idx in range(0,5):
        week_row = month_row + week_idx*2 + 1
        week_number = cal.cell(week_row, month_col).value
        week_dict = { 'week_number': week_number }
        for day_idx in range(1,8):
            day_number = cal.cell(week_row, month_col + day_idx).value
            if day_number != '':
                day_caregiver =  cal.cell(week_row + 1, month_col + day_idx).value
                week_dict[day_number] = day_caregiver
        month_dict['weeks'].append(week_dict)

    month_dict['days'] = merge_weeks(month_dict['weeks'])

    month_dict['caregivers'] = {}
    for day, caregiver in month_dict['days'].items():
        if caregiver in month_dict['caregivers'].keys():
            month_dict['caregivers'][caregiver] += 1
        else:
            month_dict['caregivers'][caregiver] = 1

    return month_dict


def get_events(cal):
    """Reads event configuration from worksheet `cal` and returns a list with event types.
    """
    events_cell = cal.find('Event templates')
    events_list = []

    key_col = events_cell.col
    name_col = cal.find('Summary').col
    desc_col = cal.find('Description').col
    start_col = cal.find('Start').col
    end_col = cal.find('End').col
    caregivers_col = cal.find('Apply to caregivers').col
    weekdays_col = cal.find('Apply to weekdays').col

    row = events_cell.row + 1
    while True:
        event_key = cal.cell(row, key_col).value

        if event_key == "":
            print("No more event templates")
            break

        print("Found template: {}".format(event_key))
        summary = cal.cell(row, name_col).value
        desc = cal.cell(row, desc_col).value
        caregivers = cal.cell(row, caregivers_col).value.split(",")
        weekdays = cal.cell(row, weekdays_col).value.split(",")
        start = cal.cell(row, start_col).value
        end = cal.cell(row, end_col).value

        events_list.append(EventTemplate(event_key, summary, desc, caregivers, weekdays, start, end))
        row = row + 1

    return events_list


def get_caregivers(cal):
    """Reads caregiver codes and names to use for custody days and events.
    """
    caregivers_cell = cal.find('Caregivers')
    caregivers_list = []

    i = 1
    while True:
        next_caregiver_code = cal.cell(caregivers_cell.row + i, caregivers_cell.col).value
        if next_caregiver_code != "":
            caregivers_list.append({ "caregiver_code": next_caregiver_code, "caregiver_name": cal.cell(caregivers_cell.row + i, caregivers_cell.col + 1).value})
            i = i + 1
        else:
            break

    return caregivers_list


def main():
    "Demo code to read and print data from the calendar"

    calendar_file_name = 'Calendario de custodia compartida Elena'
    calendar_school_period = '2019-2020'

    cal = open_calendar_worksheet(calendar_file_name, calendar_school_period)

    print("Opened calendar for school period {} from {}".format(calendar_school_period, calendar_file_name))

    # Get number of days with custody
    # - We substract the cell that is used as legend in the sheet
    complete_days_A = len(cal.findall('AD')) - 1
    complete_days_X = len(cal.findall('XD')) - 1
    school_days_A = len(cal.findall('A')) - 1
    school_days_X = len(cal.findall('X')) - 1

    print('  A has {} complete days and {} school days'.format(complete_days_A, school_days_A))
    print('  X has {} complete days and {} school days'.format(complete_days_X, school_days_X))

    print("Monthly distribution")
    print(json.dumps(read_month(cal, calendar_school_period, 'August'), sort_keys=True, indent=4))


def test_get_caregivers():
    calendar_file_name = 'Calendario de custodia compartida Elena'
    calendar_school_period = '2019-2020'

    cal = open_calendar_worksheet(calendar_file_name, calendar_school_period)
    print("Opened calendar for school period {} from {}".format(calendar_school_period, calendar_file_name))
    print(get_caregivers(cal))


def test_get_events():
    calendar_file_name = 'Calendario de custodia compartida Elena'
    calendar_school_period = '2019-2020'

    cal = open_calendar_worksheet(calendar_file_name, calendar_school_period)
    print("Opened calendar for school period {} from {}".format(calendar_school_period, calendar_file_name))
    for event_tmpl in get_events(cal):
        print(event_tmpl)


if __name__ == "__main__":
    #main()
    #test_get_caregivers()
    test_get_events()
