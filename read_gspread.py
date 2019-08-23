import json
import gspread
import calendar
from oauth2client.service_account import ServiceAccountCredentials


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
    print calendar.month(year, month_number)

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

    return month_dict


def main():
    "Demo code to read and print data from the calendar"

    calendar_file_name = 'Calendario de custodia compartida Elena'
    calendar_school_period = '2019-2020'

    cal = open_calendar_worksheet(calendar_file_name, calendar_school_period)

    print "Opened calendar for school period {} from {}".format(calendar_school_period, calendar_file_name)

    # Get number of days with custody
    # - We substract the cell that is used as legend in the sheet
    complete_days_A = len(cal.findall('AD')) - 1
    complete_days_X = len(cal.findall('XD')) - 1
    school_days_A = len(cal.findall('A')) - 1
    school_days_X = len(cal.findall('X')) - 1

    print '  A has {} complete days and {} school days'.format(complete_days_A, school_days_A)
    print '  X has {} complete days and {} school days'.format(complete_days_X, school_days_X)

    print "Monthly distribution"
    print json.dumps(read_month(cal, calendar_school_period, 'August'), sort_keys=True, indent=4)

    # TODO list complete and school days per caregiver


if __name__ == "__main__":
    main()
