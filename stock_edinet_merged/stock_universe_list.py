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
file_name = 'stock_data.csv'
folder_id = '1AMu-_CnZE07uwk57Hb-ZzL9wthrQUQX1'

# Download the file
download_file_from_drive(file_name, folder_id)

import requests
import zipfile
import io
import os

script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)
os.chdir(script_dir)

# URL of the file
url = "https://disclosure2dl.edinet-fsa.go.jp/searchdocument/codelisteng/Edinetcode.zip"

# Download the file
response = requests.get(url)
if response.status_code == 200:
    # Open the downloaded zip file
    zipped_file = zipfile.ZipFile(io.BytesIO(response.content))
    # Extract the contents to the current directory
    zipped_file.extractall(".")
    print("File downloaded and extracted successfully.")
else:
    print("Failed to download the file.")

import csv
import requests
from bs4 import BeautifulSoup

script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)
os.chdir(script_dir)

def scrape_company_sites_from_csv(input_csv, output_csv):
    with open(input_csv, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        
        # Create a new CSV file for output
        with open(output_csv, 'w', newline='') as output_csvfile:
            fieldnames = ['number', 'Company Site URL']  # Change 'Number' to 'number'
            writer = csv.DictWriter(output_csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                stock_code = row['Number']
                company_site_url = scrape_company_site(stock_code)

                if company_site_url and "index.html" not in company_site_url:
                    # Save data to the new CSV file
                    writer.writerow({'number': stock_code, 'Company Site URL': company_site_url})  # Change 'Number' to 'number'
                else:
                    print(f"Skipping stock code {stock_code} with invalid or empty URL")

def scrape_company_site(stock_code):
    url = f"https://kabutan.jp/stock/?code={stock_code}"

    # Send an HTTP GET request to the URL
    response = requests.get(url)

    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the <th> tag with the text "会社サイト" (Company Site)
        company_site_th = soup.find('th', text='会社サイト')

        if company_site_th:
            # Find the corresponding <td> tag containing the company site URL
            company_site_td = company_site_th.find_next('td')

            if company_site_td:
                # Extract the company site URL from the <a> tag
                company_site_url = company_site_td.find('a')['href']

                print(f"Company Site URL for stock code {stock_code}: {company_site_url}")
                return company_site_url
            else:
                print(f"Company Site URL not found for stock code {stock_code}")
        else:
            print(f"Company Site information not found for stock code {stock_code}")
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")

# Example usage
scrape_company_sites_from_csv('stock_data.csv', 'stock_homepage_data.csv')

import os

# Get the absolute path of the current directory
current_directory = os.path.dirname(os.path.abspath(__file__))

# Specify the file paths
input_csv_path = os.path.join(current_directory, "EdinetcodeDlInfo.csv")
output_csv_path = os.path.join(current_directory, "Filtered_EdinetcodeDlInfo.csv")

# Open the input CSV file for reading with 'shift-jis' encoding
with open(input_csv_path, encoding="shift-jis", errors='replace') as file:
    lines = file.readlines()

# Extract the first and last second items for all lines, skipping the header
header = "edinetcode,number\n"
lines = lines[2:]  # Skip the second line

filtered_data = []
for line in lines:
    fields = line.strip().split(',')
    if len(fields) >= 2:
        edinet_code = fields[0].strip('"')
        last_second_item = fields[-2].strip('"')
        
        # Remove the last digit from the second item if it's a number
        if last_second_item.isdigit():
            last_second_item = last_second_item[:-1]
        
        key = f"{edinet_code},{last_second_item}"
        filtered_data.append(key)

# Save the filtered data to a new CSV file
with open(output_csv_path, 'w', encoding="utf-8") as file:
    # Write the new header
    file.write(header)
    
    # Write the filtered data
    for data in filtered_data:
        file.write(f'{data}\n')

import os
import pandas as pd

# Get the directory of the current script
script_directory = os.path.dirname(os.path.abspath(__file__))

# Define the file names
file1 = 'Filtered_EdinetcodeDlInfo.csv'
file2 = 'stock_homepage_data.csv'

# Create absolute paths for the CSV files
path1 = os.path.join(script_directory, file1)
path2 = os.path.join(script_directory, file2)

# Read the CSV files into dataframes
df1 = pd.read_csv(path1)
df2 = pd.read_csv(path2)

# Convert 'number' in df1 to integers
df1['number'] = pd.to_numeric(df1['number'], errors='coerce').fillna(0).astype(int)

# Convert 'number' in df2 to integers
df2['number'] = pd.to_numeric(df2['number'], errors='coerce').fillna(0).astype(int)

# Print column names for debugging
print("Columns in df1:", df1.columns)
print("Columns in df2:", df2.columns)

# Merge DataFrames based on the common column "number"
merged_df = pd.merge(df1, df2, on='number')

# Convert the 'number' column to integer in merged_df
merged_df['number'] = merged_df['number'].astype(int)

# Select only the required columns
result_df = merged_df[['edinetcode', 'number', 'Company Site URL']]

# Print the resulting DataFrame
print(result_df)

# Save the result to a new CSV file
result_df.to_csv(os.path.join(script_directory, 'merged_data.csv'), index=False)

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
csv_files = ['stock_homepage_data.csv', 'merged_data.csv']

# Iterate over each file and upload/update it
for csv_file in csv_files:
    file_path = f'{csv_file}'  # Update the path to your CSV files
    upload_or_update_file(drive_service, folder_id, file_path)

import os

def delete_files(file_list):
    for file in file_list:
        if os.path.exists(file):
            os.remove(file)
            print(f"File {file} has been deleted.")
        else:
            print(f"File {file} does not exist.")

# List of files to be deleted
files_to_delete = ['stock_data.csv', 'EdinetcodeDlInfo.csv', 'Filtered_EdinetcodeDlInfo.csv', 'stock_homepage_data.csv', 'merged_data.csv']

delete_files(files_to_delete)
