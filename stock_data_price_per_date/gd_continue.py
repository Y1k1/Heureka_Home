import os
import io
import zipfile
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)
os.chdir(script_dir)

# Load client secrets from the credentials.json file
credentials = service_account.Credentials.from_service_account_file(
    'credentials.json',
    scopes=['https://www.googleapis.com/auth/drive']
)

# Build the Google Drive API client
drive_service = build('drive', 'v3', credentials=credentials)

def download_file_from_drive(file_name, folder_id):
    # Search for the file in the specified folder
    response = drive_service.files().list(
        q=f"name='{file_name}' and '{folder_id}' in parents",
        spaces='drive',
        fields='files(id, name)'
    ).execute()
    files = response.get('files', [])

    if files:
        file_id = files[0].get('id')
        request = drive_service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%.")
        fh.seek(0)

        # Save the zip file
        with open(file_name, 'wb') as f:
            f.write(fh.read())
        print(f'Downloaded {file_name}')

        # Extract the zip file
        with zipfile.ZipFile(file_name, 'r') as zip_ref:
            extract_folder = script_dir  # Extracting directly to the script directory
            zip_ref.extractall(extract_folder)
            print(f'Extracted {file_name} in {extract_folder}')

    else:
        print(f'File {file_name} not found in folder {folder_id}')

# Specify the name of the file and the Google Drive folder ID
file_name = 'stock_data_price_per_date_pre.zip'
folder_id = '1AMu-_CnZE07uwk57Hb-ZzL9wthrQUQX1'

# Download the file and extract it
download_file_from_drive(file_name, folder_id)
