from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

CREDENTIALS_FILE = 'creds.json'

def get_calendar_service():

    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPES)

    service = build('calendar', 'v3', credentials=creds)
    return service
