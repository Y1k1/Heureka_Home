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
        # File exists, so update it (without setting parents field)
        file_id = files[0].get('id')
        file_metadata = {'name': file_name}  # Only update the name
        updated_file = drive_service.files().update(
            fileId=file_id,
            body=file_metadata,
            media_body=media
        ).execute()
        print(f'Updated {file_name} with File ID: {updated_file.get("id")}')
    else:
        # File does not exist, so create it (with parents field)
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



# Define the path to the 'stock_data_price_per_date' folder
folder_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'stock_data_price_per_date')

# Define the name for the zipped folder
zip_file_name = 'stock_data_price_per_date.zip'

# Zip the folder
zip_directory(folder_path, zip_file_name)

# Define the target Google Drive folder ID
target_folder_id = '1AMu-_CnZE07uwk57Hb-ZzL9wthrQUQX1'

# Upload the zipped folder to Google Drive
upload_file_to_drive(zip_file_name, target_folder_id)

import os
import shutil

# Get the directory of the current script
script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)

# Change the current working directory to the script's directory
os.chdir(script_dir)

# File and folder names
file_name = 'stock_data_price_per_date.zip'
folder_name = 'stock_data_price_per_date'

# Delete the file
if os.path.exists(file_name):
    try:
        os.remove(file_name)
        print(f"File '{file_name}' has been successfully deleted.")
    except OSError as e:
        print(f"Error deleting file: {e.strerror}")
else:
    print(f"File '{file_name}' does not exist.")

# Delete the folder
if os.path.exists(folder_name) and os.path.isdir(folder_name):
    try:
        shutil.rmtree(folder_name)
        print(f"Folder '{folder_name}' has been successfully deleted.")
    except OSError as e:
        print(f"Error deleting folder: {e.strerror}")
else:
    print(f"Folder '{folder_name}' does not exist or is not a folder.")
