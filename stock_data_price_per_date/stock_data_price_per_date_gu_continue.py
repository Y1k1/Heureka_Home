import os
import zipfile
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload


# Load client secrets from the credentials.json file
credentials = service_account.Credentials.from_service_account_file(
    'credentials.json',
    scopes=['https://www.googleapis.com/auth/drive']
)

def download_file_from_drive(file_id, file_path):
    request = drive_service.files().get_media(fileId=file_id)
    with open(file_path, "wb") as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))

# Build the Google Drive API client
drive_service = build('drive', 'v3', credentials=credentials)

def zip_directory(folder_path, output_filename, append=False):
    mode = 'a' if append and os.path.exists(output_filename) else 'w'
    with zipfile.ZipFile(output_filename, mode, zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                zipf.write(os.path.join(root, file), 
                           os.path.relpath(os.path.join(root, file), 
                                           os.path.join(folder_path, '..')))

def upload_file_to_drive(file_path, target_folder_id):
    file_name = os.path.basename(file_path)

    # Search for existing file with the same name in the target folder
    response = drive_service.files().list(
        q=f"name='{file_name}' and '{target_folder_id}' in parents",
        spaces='drive',
        fields='files(id, name)'
    ).execute()
    files = response.get('files', [])

    media = MediaFileUpload(file_path, mimetype='application/zip')

    if files:
        # File exists, so update it
        file_id = files[0].get('id')
        file_metadata = {'name': file_name}
        updated_file = drive_service.files().update(
            fileId=file_id,
            body=file_metadata,
            media_body=media
        ).execute()
        print(f'Updated {file_name} with File ID: {updated_file.get("id")}')
    else:
        # File does not exist, so create it
        file_metadata = {
            'name': file_name,
            'parents': [target_folder_id]
        }
        uploaded_file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        print(f'Uploaded {file_name} with File ID: {uploaded_file.get("id")}')

def process_folder(folder_name, target_folder_id, append_to_zip=False):
    folder_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), folder_name)
    zip_file_name = f'{folder_name}.zip'

    # Check if the file exists on Google Drive and download it if append_to_zip is True
    if append_to_zip:
        response = drive_service.files().list(
            q=f"name='{zip_file_name}' and '{target_folder_id}' in parents",
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        files = response.get('files', [])

        if files:
            file_id = files[0].get('id')
            download_file_from_drive(file_id, zip_file_name)

    zip_directory(folder_path, zip_file_name, append=append_to_zip)
    upload_file_to_drive(zip_file_name, target_folder_id)


target_folder_id = '1AMu-_CnZE07uwk57Hb-ZzL9wthrQUQX1'

# Process each folder
process_folder('stock_data_price_per_date', target_folder_id, append_to_zip=True)
process_folder('stock_data_price_per_date_pre', target_folder_id)
