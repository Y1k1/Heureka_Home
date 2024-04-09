import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Change directory to the script directory
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

def list_files_in_folder(folder_id):
    response = drive_service.files().list(
        q=f"'{folder_id}' in parents and mimeType contains 'image/'",
        spaces='drive',
        fields='files(id, name)'
    ).execute()
    return response.get('files', [])

def create_html_file(file_list, html_file_name):
    with open(html_file_name, 'w') as file:
        file.write('<html><head><title>Drive Folder Images</title></head><body>\n')
        file.write('<h1>Google Drive Folder Images</h1>\n')
        for f in file_list:
            iframe_src = f"https://drive.google.com/file/d/{f['id']}/preview"
            file.write(f"<h3>{f['name']}</h3>\n")
            file.write(f"<iframe src='{iframe_src}' width='640' height='480'></iframe>\n")
        file.write('</body></html>')

# Specify the Google Drive folder ID
folder_id = '19UUOOlr4D9ZCsi7shaJR8bsItMZV3vKD'

# List files and create HTML file
files_in_folder = list_files_in_folder(folder_id)
create_html_file(files_in_folder, 'teikyo_image.html')

print("HTML file created as 'teikyo_image.html'")

import requests

def upload_file(url, file_path):
    with open(file_path, 'rb') as f:
        # Extract just the filename
        filename = file_path.split('/')[-1]
        files = {'file': (filename, f)}
        response = requests.post(url, files=files)
        return response.text

if __name__ == "__main__":
    base_url = 'https://yk-fuku.onrender.com'  # Change to your Flask app's URL
    file_path = 'teikyo_image.html'  # Change to the path of the file to upload
    print(upload_file(f'{base_url}/upsave_file', file_path))
