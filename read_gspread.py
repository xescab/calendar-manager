import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)

gc = gspread.authorize(credentials)


# Open calendar sheet
wks = gc.open("Calendario de custodia compartida Elena").worksheet('2019-2020')

# Get number of days with custody
# - We substract the cell that is used as legend in the sheet
complete_days_A = len(wks.findall('AD')) - 1
complete_days_X = len(wks.findall('XD')) - 1
school_days_A = len(wks.findall('A')) - 1
school_days_X = len(wks.findall('X')) - 1


print 'A has {} complete days and {} school days'.format(complete_days_A, school_days_A)
print 'X has {} complete days and {} school days'.format(complete_days_X, school_days_X)
