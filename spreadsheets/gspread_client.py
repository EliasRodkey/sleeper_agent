import gspread
from gspread import Spreadsheet
import logging
from oauth2client.service_account import ServiceAccountCredentials


logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


def list_service_account_drive_files(service_acct_file: str, scopes: list[str]) -> list:
    """Creates a list of files and their meta properties in the google drive"""

    from googleapiclient.discovery import build
    from google.oauth2 import service_account
    

    creds = service_account.Credentials.from_service_account_file(
        service_acct_file, scopes=scopes)

    drive_service = build('drive', 'v3', credentials=creds)

    # List files owned by the service account
    results = drive_service.files().list(
        q="'me' in owners",
        pageSize=100,
        fields="files(id, name, mimeType, size)"
    ).execute()

    items = results.get('files', [])
    if not items:
        print("No files found.")
    else:
        for item in items:
            print(f"{item['name']} ({item['mimeType']}) - {item.get('size', 'Unknown')} bytes")

    # List trashed files
    trashed_files = drive_service.files().list(
        q="trashed = true",
        fields="files(id, name)"
    ).execute()

    for file in trashed_files.get('files', []):
        print(f"Deleting trashed file: {file['name']}")
        drive_service.files().delete(fileId=file['id']).execute()

    return items


SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_FILE = 'spreadsheets/spreadsheet_credentials.json' 


def get_gspread_client(scopes: list[str]=SCOPES, service_acct: str=SERVICE_ACCOUNT_FILE):
    """Creates and returns an authorized gspread client connection"""
    logger.info(f"Creating connection to gspread client using credentials: {service_acct}")

    creds = ServiceAccountCredentials.from_json_keyfile_name(service_acct, scopes)

    try:
        return gspread.authorize(creds)
    except Exception as e:
        logger.error(f"Unable to create connection to gspread client, errors: {e}")


def get_spreadsheet(spreadsheet_name: str, scopes: list[str]=SCOPES, service_acct: str=SERVICE_ACCOUNT_FILE) -> Spreadsheet:
    """Retrieves a Spreadsheet object using the gspread client"""
    client = get_gspread_client(scopes=scopes, service_acct=service_acct)
    return client.open(spreadsheet_name)

        

if __name__ == "__main__":
    client = get_gspread_client()
    list_service_account_drive_files()

