import requests
from bs4 import BeautifulSoup
import json
import os

script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)
os.chdir(script_dir)

# URL of the website to scrape
url = "https://site3.sbisec.co.jp/ETGate/?_ControlID=WPLETsiR001Control&_PageID=WPLETsiR001Idtl30&_DataStoreID=DSWPLETsiR001Control&_ActionID=DefaultAID&s_rkbn=2&s_btype=&i_stock_sec=1345&i_dom_flg=1&i_exchange_code=JPN&i_output_type=2&exchange_code=TKY&stock_sec_code_mul=1345&ref_from=1&ref_to=20&wstm4130_sort_id=&wstm4130_sort_kbn=&qr_keyword=1&qr_suggest=1&qr_sort=4"

response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    iframe = soup.find('iframe', {'src': True, 'width': '100%', 'height': '617px', 'marginwidth': '0', 'marginheight': '0', 'framespacing': '0', 'frameborder': '0', 'scrolling': 'no'})
    
    if iframe:
        src = iframe.get('src')
        split_str = ".T&mode=D&main=C&sub=V&TP=1&DispNum=120&style=main_domestic_chart&size=0&investor=visitor"
        
        if split_str in src:
            first_half, latter_half = src.split(split_str)
            first_half = first_half.replace('=1345', '=')
            latter_half = latter_half.replace('=1345', '=')
            
            # Saving both halves in one JSON file
            data = {"first_half": first_half, "later_half": split_str + latter_half}
            with open('src_data_stock_url.json', 'w') as file:
                json.dump(data, file)
            
            print("Both halves of URL modified and saved in one JSON file.")
        else:
            print("Split string not found in the src URL.")
    else:
        print("Desired iframe not found on the page.")
else:
    print("Failed to retrieve page:", response.status_code)

import os.path
import requests
from bs4 import BeautifulSoup
import json
import os

script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)
os.chdir(script_dir)

# Check if the JSON file exists for constructing the initial URL
if os.path.exists('src_data_stock_url.json'):
    # Load data from JSON file for initial URL
    with open('src_data_stock_url.json', 'r') as file:
        data = json.load(file)
    first_half = data.get("first_half", "")
    later_half = data.get("later_half", "")
    stock_code = "2330.T"
    url = f"{first_half}{stock_code}{later_half}"
else:
    print("JSON file for initial URL not found.")
    url = ""

# Only proceed if a URL is successfully constructed
if url:
    # The base substring you are looking for in URLs
    base_substring = 'https://chart.iris.sbisec.co.jp/sbi/as/Mchart-mchart.html?'

    # Additional parameters to append
    additional_params = "&mode=15&DaysNum=1&main=C&addon=None"

    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Iterate through all tags
        for tag in soup.find_all(True):
            # Iterate through all attributes of the tag
            for attr in tag.attrs:
                attr_value = str(tag[attr])
                # Check if the attribute contains the base URL and ends with 'size=0'
                if attr_value.startswith(base_substring) and attr_value.endswith('size=0'):
                    final_url = attr_value + additional_params
                    print("Found URL:", final_url)

                    # Split the URL at '=2330'
                    split_url = final_url.split("=2330.T")

                    first_half_15_image = split_url[0] + "="
                    latter_half_15_image = split_url[1].replace("2330.T", ".T")  # Replacing '2330.T' with '.T'

                    # Update the existing JSON data with new data
                    data["first_half_15_image"] = first_half_15_image
                    data["later_half_15_image"] = latter_half_15_image

                    # Saving the updated data in a JSON file
                    with open('src_data_stock_url.json', 'w') as file:
                        json.dump(data, file, indent=4)
    else:
        print("Failed to retrieve the webpage")
else:
    print("URL was not constructed.")

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
csv_files = ['src_data_stock_url.json']

# Iterate over each file and upload/update it
for csv_file in csv_files:
    file_path = f'{csv_file}'  # Update the path to your CSV files
    upload_or_update_file(drive_service, folder_id, file_path)
