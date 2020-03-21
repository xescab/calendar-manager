import json
import gspread
import calendar
from oauth2client.service_account import ServiceAccountCredentials
from calendar_manager.events import EventTemplate


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
    days from July and August are distributed at the beginning of the school
    period.
    TODO: June is a special month split the weekend just after the school ends.
    """
    (first_year, second_year) = calendar_school_period.split('-')
    return first_year if month_name in ['July','August','September','October','December','November'] else second_year


def find_cell(all_cells, keyword):
    """Returns the (row, col) position of a cell which value matches keyword
    or raises ValueError
    """
    for row in all_cells:
        if keyword in row:
            row_idx = all_cells.index(row)
            col_idx = row.index(keyword)
            print(f"Found {keyword} at row={row_idx}, column={col_idx}")
            return (row_idx, col_idx)

    raise ValueError(f"Cell with value '{keyword}' not found on sheet")


def get_table(all_cells, keyword, x_size, y_size):
    """Returns a (x_size * y_size) table starting from cell(x, y)
    """
    table = []

    # y = row_idx, x = col_idx 
    y, x = find_cell(all_cells, keyword)

    for row in all_cells[y:y+y_size]:
        print(row)
        row_filtered = [c for c in row[x:x+x_size]]
        print(row_filtered)
        table.append(row_filtered)

    print(table)
    return table


def read_month(all_cells, calendar_school_period, month_name):
    """Reads info for a particular month from cells read on a worksheet and returns a
    dictionary with the distribution of days.
    """
    month_number = get_month_number(month_name)
    year = int(get_year(calendar_school_period, month_name))

    # Informative
    print("Getting {} custody days from spreadsheet ...".format(month_name))
    print(calendar.month(year, month_number))

    # Initiliaze data structure
    month_dict = { 'month': month_number, 'year': year, 'weeks': [] }
    month_row, month_col = find_cell(all_cells, month_name)

    for week_idx in range(0,5):
        week_row = month_row + week_idx*2 + 1
        week_number = all_cells[week_row][month_col]
        week_dict = { 'week_number': week_number }
        for day_idx in range(1,8):
            day_number = all_cells[week_row][month_col + day_idx]
            if day_number != '' and day_number != ' ':
                day_caregiver = all_cells[week_row + 1][month_col + day_idx]
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


def get_event_templates(all_cells):
    """Reads event configuration from worksheet `all_cells` and returns a list with event types.
    """
    key_row, key_col = find_cell(all_cells, 'Event templates')
    events_list = []

    dummy, name_col = find_cell(all_cells, 'Summary')
    dummy, desc_col = find_cell(all_cells, 'Description')
    dummy, start_col = find_cell(all_cells, 'Start')
    dummy, end_col = find_cell(all_cells, 'End')
    dummy, caregivers_col = find_cell(all_cells, 'Apply to caregivers')
    dummy, weekdays_col = find_cell(all_cells, 'Apply to weekdays')

    print("Looking for event templates on spreadsheet ...")
    for row in all_cells[key_row+1:]:
        event_key = row[key_col]

        if event_key == "":
            print("No more event templates")
            break

        summary = row[name_col]
        desc = row[desc_col]
        caregivers = row[caregivers_col].split(",")
        weekdays = row[weekdays_col].split(",")
        start = row[start_col]
        end = row[end_col]

        event_tmpl = EventTemplate(event_key, summary, desc, caregivers, weekdays, start, end)
        print("Found template: {}".format(event_tmpl))
        events_list.append(event_tmpl)

    return events_list


def get_caregivers(all_cells):
    """Reads caregiver codes and names to use for custody days and events.
    """
    row_cg, col_cg = find_cell(all_cells, 'Caregivers')
    caregivers_dict = {}

    for row in all_cells[row_cg+1:]:
        next_caregiver_code = row[col_cg]
        if next_caregiver_code == "":
            break
        caregivers_dict[next_caregiver_code] = { "name": row[col_cg + 1], "color": row[col_cg + 2]}

    return caregivers_dict