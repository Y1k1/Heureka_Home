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

import csv
import os
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta

script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)
os.chdir(script_dir)

# Function to scrape data from a given URL
def scrape_stock_data(url):
    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")
    rows = soup.find_all("tr")
    today_date = datetime.now()
    data_for_past_week = []
    for i in range(50):
        current_date = today_date - timedelta(days=i)
        current_date_str = current_date.strftime("%-m/%-d")
        start_price, high_price, low_price, end_price, trading_volume = None, None, None, None, None
        for row in rows:
            header_cell = row.find("th", class_="sticky")
            if header_cell:
                cell_text = header_cell.get_text(strip=True)
                if cell_text == current_date_str:
                    data_cells = row.find_all("td")
                    if len(data_cells) >= 7:
                        start_price = data_cells[0].get_text(strip=True)
                        high_price = data_cells[1].get_text(strip=True)
                        low_price = data_cells[2].get_text(strip=True)
                        end_price = data_cells[3].get_text(strip=True)
                        trading_volume = data_cells[6].get_text(strip=True).replace(",", "")
                    break
        if start_price is not None:
            data_for_past_week.append([current_date_str, start_price, high_price, low_price, end_price, trading_volume])
    return data_for_past_week

# Read the CSV file and process each row
with open("stock_data_var2_complete.csv", "r", newline="") as csvfile:
    reader = csv.reader(csvfile)
    next(reader)  # Skip header
    for row in reader:
        number = row[1]
        url = "https://s.kabutan.jp/stocks/{}/historical_prices/daily/".format(number)
        data_for_past_week = scrape_stock_data(url)
        time.sleep(0)
        # Create a directory to store results if it doesn't exist
        if not os.path.exists("stock_data_price_per_date"):
            os.makedirs("stock_data_price_per_date")
        # Write the scraped data to a new CSV file
        with open(os.path.join("stock_data_price_per_date", "{}_past.csv".format(number)), "w", newline="") as resultfile:
            writer = csv.writer(resultfile)
            writer.writerow(["Date", "始値", "高値", "安値", "終値", "売買高(株)"])
            writer.writerows(data_for_past_week)
        print("Data for Number {} saved to result/{}_past.csv".format(number, number))

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
