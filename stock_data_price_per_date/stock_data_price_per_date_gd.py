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

        with open(file_name, 'wb') as f:
            f.write(fh.read())
        print(f'Downloaded {file_name}')
    else:
        print(f'File {file_name} not found in folder {folder_id}')

# Specify the name of the file and the Google Drive folder ID
file_name = 'stock_data_var2_complete.csv'
folder_id = '1AMu-_CnZE07uwk57Hb-ZzL9wthrQUQX1'

# Download the file
download_file_from_drive(file_name, folder_id)

import pandas as pd
import os

# File path for the original CSV file
file_path = 'stock_data_var2_complete.csv'

# Folder where the split files will be saved
save_folder = 'stock_data_price_per_date_pre'

# Create the folder if it doesn't exist
if not os.path.exists(save_folder):
    os.makedirs(save_folder)

# Read the data
data = pd.read_csv(file_path)

# Split data into chunks of 50 rows
chunk_size = 50
num_chunks = len(data) // chunk_size + (1 if len(data) % chunk_size else 0)

for i in range(num_chunks):
    # Define the start and end of each chunk
    start = i * chunk_size
    end = start + chunk_size

    # Extract the chunk
    chunk = data.iloc[start:end]

    # Define the chunk file name, including the folder
    chunk_file_name = os.path.join(save_folder, f'stock_data_var2_complete_{i + 1}.csv')

    # Save the chunk to a new CSV file
    chunk.to_csv(chunk_file_name, index=False)

print(f'Done! Data has been split into {num_chunks} files in the "{save_folder}" folder.')
 
