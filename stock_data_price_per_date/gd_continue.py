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

import os
import random

def select_and_delete_csv_files(folder_path, keep_count=2):
    # Check if the folder exists
    if not os.path.exists(folder_path):
        print(f"Folder not found: {folder_path}")
        return

    # List all CSV files in the folder
    all_csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

    # Check if there are enough files to keep
    if len(all_csv_files) <= keep_count:
        print("Not enough files to delete, keeping all files.")
        return

    # Randomly select files to keep
    files_to_keep = random.sample(all_csv_files, keep_count)

    # Delete all other files
    for file in all_csv_files:
        if file not in files_to_keep:
            os.remove(os.path.join(folder_path, file))
            print(f"Deleted file: {file}")

# Folder path
folder_path = os.path.join(script_dir, 'stock_data_price_per_date_pre')

# Call the function
select_and_delete_csv_files(folder_path)


import zipfile
import os

def remove_csv_from_zip(zip_file_path, folder_path):
    # Check if the zip file exists
    if not os.path.exists(zip_file_path):
        print(f"ZIP file not found: {zip_file_path}")
        return

    # Check if the folder exists
    if not os.path.exists(folder_path):
        print(f"Folder not found: {folder_path}")
        return

    # List all CSV files in the folder
    folder_csv_files = set(f for f in os.listdir(folder_path) if f.endswith('.csv'))

    # Create a temporary zip file
    temp_zip_path = zip_file_path + '.tmp'
    
    with zipfile.ZipFile(zip_file_path, 'r') as zip_read:
        with zipfile.ZipFile(temp_zip_path, 'w') as zip_write:
            for item in zip_read.infolist():
                # Copy files to the new zip file except the ones we want to remove
                if item.filename.endswith('.csv') and item.filename.split('/')[-1] in folder_csv_files:
                    print(f"Removing file from zip: {item.filename}")
                    continue
                zip_write.writestr(item, zip_read.read(item.filename))

    # Replace the old zip file with the new one
    os.remove(zip_file_path)
    os.rename(temp_zip_path, zip_file_path)
    print(f"Updated ZIP file saved: {zip_file_path}")

# Paths
zip_file_path = os.path.join(script_dir, 'stock_data_price_per_date_pre.zip')
folder_path = os.path.join(script_dir, 'stock_data_price_per_date_pre')

# Call the function
remove_csv_from_zip(zip_file_path, folder_path)

from googleapiclient.http import MediaFileUpload

def upload_file_to_drive(file_path, folder_id):
    file_name = os.path.basename(file_path)

    # Search for the file with the same name in the specified folder
    search_response = drive_service.files().list(
        q=f"name='{file_name}' and '{folder_id}' in parents",
        spaces='drive',
        fields='files(id, name)'
    ).execute()
    files = search_response.get('files', [])

    # Create a MediaFileUpload object for the file
    media = MediaFileUpload(file_path, mimetype='application/zip')

    if files:
        # File found, update (overwrite) it
        file_id = files[0].get('id')
        updated_file = drive_service.files().update(
            fileId=file_id,
            media_body=media
        ).execute()
        print(f"Updated file with ID: {updated_file['id']}")
    else:
        # File not found, create a new file
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        created_file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        print(f"Uploaded new file with ID: {created_file.get('id')}")

# Usage example
zip_file_path = os.path.join(script_dir, 'stock_data_price_per_date_pre.zip')
# Call the function to upload the file
upload_file_to_drive(zip_file_path, folder_id)
