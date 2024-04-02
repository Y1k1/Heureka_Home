import os
import pandas as pd
import subprocess

script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)
os.chdir(script_dir)
         
def run_script(script_name):
    subprocess.run(['python3', script_name], check=True)

def combine_csv_files():
    # The directory is already set by os.chdir in main, so just use the current directory
    directory = os.getcwd()

    # List all CSV files in this directory
    csv_files = [file for file in os.listdir(directory) if file.endswith('.csv')]

    # Initialize a list to store the values from each DataFrame
    values_list = []

    # Read each CSV file, stack its values, and add them to the list
    for file in csv_files:
        file_path = os.path.join(directory, file)
        df = pd.read_csv(file_path)
        stacked_values = df.stack()
        values_list.append(stacked_values)

    # Combine all values into a single column and remove duplicates
    combined_values = pd.concat(values_list, ignore_index=True).drop_duplicates().reset_index(drop=True)

    # Save the unique values to a new CSV file in the same directory
    output_path = os.path.join(directory, 'morning_stock.csv')
    combined_values.to_csv(output_path, index=False, header=False)

def main():
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    os.chdir(script_dir)

    scripts = ['kabutan_news_csv_num.py', 'trend_stock_num.py', 'yahoo_csv_num.py']
    for script in scripts:
        run_script(script)

    # Now combine all CSV files into one
    combine_csv_files()

if __name__ == "__main__":
    main()

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
csv_files = ['morning_stock.csv']

# Iterate over each file and upload/update it
for csv_file in csv_files:
    file_path = f'{csv_file}'  # Update the path to your CSV files
    upload_or_update_file(drive_service, folder_id, file_path)
