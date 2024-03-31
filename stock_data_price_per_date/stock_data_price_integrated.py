import os
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Load client secrets from the credentials.json file
credentials = service_account.Credentials.from_service_account_file(
    'credentials.json',
    scopes=['https://www.googleapis.com/auth/drive']
)

# Build the Google Drive API client
drive_service = build('drive', 'v3', credentials=credentials)

def download_folder(folder_name):
    # Find the folder by name
    folder_response = drive_service.files().list(
        q=f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}'",
        spaces='drive',
        fields='files(id, name)'
    ).execute()
    folders = folder_response.get('files', [])

    if not folders:
        print(f'Folder "{folder_name}" not found.')
        return

    folder_id = folders[0]['id']

    # List all files in the folder
    file_response = drive_service.files().list(
        q=f"'{folder_id}' in parents",
        spaces='drive',
        fields='files(id, name)'
    ).execute()
    files = file_response.get('files', [])

    if not files:
        print(f'No files found in folder "{folder_name}".')
        return

    # Create a folder to save files
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    for file in files:
        file_id = file['id']
        file_name = file['name']
        request = drive_service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Downloading {file_name} {int(status.progress() * 100)}%.")
        fh.seek(0)

        with open(os.path.join(folder_name, file_name), 'wb') as f:
            f.write(fh.read())
        print(f'Downloaded {file_name}')

# Specify the name of the folder
folder_name = 'stock_data_price_per_date'

# Download all files from the specified folder
download_folder(folder_name)




import os
import zipfile

def unzip_and_delete_all_in_folder(folder_path):
    # Iterate over all files in the directory
    for filename in os.listdir(folder_path):
        if filename.endswith('.zip'):
            # Construct the full file path
            file_path = os.path.join(folder_path, filename)
            
            # Unzip the file
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                # Extract all the contents into the same directory
                zip_ref.extractall(folder_path)
                print(f"Unzipped: {filename}")

            # Delete the zip file
            os.remove(file_path)
            print(f"Deleted: {filename}")

# Replace with the path to your 'stock_data_price_per_date' folder
folder_path = 'stock_data_price_per_date'
unzip_and_delete_all_in_folder(folder_path)

import os
import pandas as pd

# Directory containing the CSV files
directory = 'stock_data_price_per_date'

# Prepare a list to store the newest data from each DataFrame
newest_data = []

# Iterate over each file in the directory
for filename in os.listdir(directory):
    if filename.endswith('.csv'):
        # Construct the full file path
        filepath = os.path.join(directory, filename)

        # Read the CSV file into a DataFrame
        df = pd.read_csv(filepath)

        # Check if the DataFrame is not empty
        if not df.empty:
            # Extract the stock number from the filename (assuming the format is like '130A_past.csv')
            stock_number = filename.split('_')[0]

            # Replace the 'Date' column with the stock number
            df['Date'] = stock_number

            # Rename the 'Date' column to 'Stock Number'
            df.rename(columns={'Date': 'Stock Number'}, inplace=True)

            # Append the first row (newest data) of this DataFrame to the list
            newest_data.append(df.iloc[0])

# Concatenate all the newest data into a single DataFrame
combined_newest_data = pd.concat(newest_data, axis=1).transpose()

# Save the combined newest data to a new CSV file
combined_newest_data.to_csv('stock_data_price_per_date_integrated.csv', index=False)

import pandas as pd

# Load the CSV file
df = pd.read_csv('stock_data_price_per_date_integrated.csv')

# Convert columns with numeric values that include commas
df['終値'] = df['終値'].replace(',', '', regex=True).astype(float)
df['売買高(株)'] = df['売買高(株)'].replace(',', '', regex=True).astype(int)

# Apply the filters
filtered_df = df[(df['終値'] >= 500) & (df['終値'] <= 2500) & (df['売買高(株)'] > 10000)]

# Save the filtered data to a new CSV file
filtered_df.to_csv('stock_data_price_per_date_integrated_filtered.csv', index=False)

print("Filtered data saved to 'stock_data_price_per_date_integrated_filtered.csv'")

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os

script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)
os.chdir(script_dir)

def upload_or_update_file(drive_service, folder_id, file_path):
    file_name = os.path.basename(file_path)
    query = f"name = '{file_name}' and '{folder_id}' in parents and trashed = false"
    response = drive_service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    files = response.get('files', [])

    file_metadata = {'name': file_name}
    media = MediaFileUpload(file_path, mimetype='text/csv')

    if files:
        file_id = files[0].get('id')
        updated_file = drive_service.files().update(
            fileId=file_id,
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        print(f'Updated File ID: {updated_file.get("id")}')
    else:
        file_metadata['parents'] = [folder_id]
        new_file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        print(f'New File ID: {new_file.get("id")}')

# Load client secrets from the credentials.json file
credentials = service_account.Credentials.from_service_account_file(
    'credentials.json',  # Update the path to your credentials.json file
    scopes=['https://www.googleapis.com/auth/drive']
)

# Build the Google Drive API client
drive_service = build('drive', 'v3', credentials=credentials)

# Specify the folder ID and files to upload
folder_id = '1AMu-_CnZE07uwk57Hb-ZzL9wthrQUQX1'  # Replace with your folder ID
csv_files = ['stock_data_price_per_date_integrated.csv', 'stock_data_price_per_date_integrated_filtered.csv']

# Iterate over each file and upload/update it
for csv_file in csv_files:
    file_path = f'{csv_file}'  # Update the path to your CSV files
    upload_or_update_file(drive_service, folder_id, file_path)
