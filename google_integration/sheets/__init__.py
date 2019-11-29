from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from bot.settings_interface import get_config_document

# If modifying these scopes, delete the file token.pickle.
__DIR = os.path.join(os.path.dirname(__file__), '..')

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = f'{__DIR}/credentials/quickstart.json'
TOKEN_FILE = f'{__DIR}/credentials/token.pickle'

__config = get_config_document()

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = __config.spreadsheet_id
RANGE_NAME = f'{__config.spreadsheet_users_sheet}!A1:H'

# The file token.pickle stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
__creds = None
if os.path.exists(TOKEN_FILE):
    with open(TOKEN_FILE, 'rb') as token:
        __creds = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
if not __creds or not __creds.valid:
    if __creds and __creds.expired and __creds.refresh_token:
        __creds.refresh(Request())
    else:
        __creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    # Save the credentials for the next run
    with open(TOKEN_FILE, 'wb') as token:
        pickle.dump(__creds, token)

__service = build('sheets', 'v4', credentials=__creds)

# Call the Sheets API
gsheets = __service.spreadsheets()

