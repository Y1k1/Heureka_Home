import os
import zipfile
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Load client secrets from the credentials.json file
credentials = service_account.Credentials.from_service_account_file(
    'credentials.json',
    scopes=['https://www.googleapis.com/auth/drive']
)

# Build the Google Drive API client
drive_service = build('drive', 'v3', credentials=credentials)

# Function to zip the directory
def zip_directory(folder_path, output_filename):
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
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

# Function to process a folder
def process_folder(folder_name, target_folder_id):
    folder_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), folder_name)
    zip_file_name = f'{folder_name}.zip'
    zip_directory(folder_path, zip_file_name)
    upload_file_to_drive(zip_file_name, target_folder_id)

# Define the target Google Drive folder ID
target_folder_id = '1AMu-_CnZE07uwk57Hb-ZzL9wthrQUQX1'

# Process each folder
process_folder('stock_data_price_per_date', target_folder_id)
process_folder('stock_data_price_per_date_pre', target_folder_id)
