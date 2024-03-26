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

# Function to check if folder exists on Drive and create if not
def create_drive_folder_if_not_exists(folder_name, parent_id=None):
    # Check if folder exists
    response = drive_service.files().list(
        q=f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false" + (f" and '{parent_id}' in parents" if parent_id else ""),
        spaces='drive',
        fields='files(id, name)'
    ).execute()
    folders = response.get('files', [])

    # If folder does not exist, create it
    if not folders:
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            folder_metadata['parents'] = [parent_id]

        folder = drive_service.files().create(body=folder_metadata, fields='id').execute()
        return folder.get('id')
    return folders[0].get('id')

# Function to zip files in a directory
def zip_files(folder_path, output_filename, file_extension='.csv'):
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in os.listdir(folder_path):
            if file.endswith(file_extension):
                zipf.write(os.path.join(folder_path, file), file)

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

def process_folder(folder_name, target_folder_id, zip_only_files=False):
    folder_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), folder_name)
    base_zip_file_name = f'{folder_name}'
    zip_file_index = 1

    # Create a unique zip file name by incrementing the index if the file already exists
    zip_file_name = f'{base_zip_file_name}_{zip_file_index}.zip'
    while os.path.exists(zip_file_name):
        zip_file_index += 1
        zip_file_name = f'{base_zip_file_name}_{zip_file_index}.zip'

    if zip_only_files:
        zip_files(folder_path, zip_file_name)
    else:
        zip_directory(folder_path, zip_file_name)

    upload_file_to_drive(zip_file_name, target_folder_id)

# Define the target Google Drive folder ID
target_folder_id = '1AMu-_CnZE07uwk57Hb-ZzL9wthrQUQX1'

# Create 'stock_data_price_per_date' folder on Drive if not exists
stock_data_folder_id = create_drive_folder_if_not_exists('stock_data_price_per_date', target_folder_id)

# Process the folder 'stock_data_price_per_date'
process_folder('stock_data_price_per_date', stock_data_folder_id, zip_only_files=True)
