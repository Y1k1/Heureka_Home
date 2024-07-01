import pandas as pd
import requests
from io import BytesIO
import os

script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)
os.chdir(script_dir)

# Step 1: Download the Excel file
url = "https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls"
response = requests.get(url)
response.raise_for_status()  # Ensure we notice bad responses

# Step 2: Read the Excel file from the response content
xls = pd.ExcelFile(BytesIO(response.content))

# Step 3: Extract necessary columns and create new DataFrame
data = []
for sheet_name in xls.sheet_names:
    df = pd.read_excel(xls, sheet_name=sheet_name)
    for index, row in df.iterrows():
        name = row['銘柄名']
        number = row['コード']
        data.append([name, number, 'URL_placeholder'])

# Step 4: Create new DataFrame
stock_data_df = pd.DataFrame(data, columns=['Title', 'Number', 'URL'])

# Step 5: Save to stock_data.csv
stock_data_df.to_csv('stock_data.csv', index=False, encoding='utf-8')

print("New stock_data.csv created successfully.")

#--newly----
#----------
import pandas as pd
import requests
from bs4 import BeautifulSoup
import csv
import os

script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)
os.chdir(script_dir)

# Function to scrape the Genre information from the HTML
def scrape_genre(soup):
    genre_element = soup.find('a', href=lambda href: href and '/themes/?industry=' in href)
    if genre_element:
        genre_text = genre_element.text.strip()
        return genre_text
    return None


# Load the CSV file
df = pd.read_csv('stock_data.csv')

# Prepare a list to store the new data
new_data = []

# Iterate through each row in the dataframe
for index, row in df.iterrows():
    # Construct the URL
    url = f"https://kabutan.jp/stock/?code={row['Number']}"

    # Perform the web scraping
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract the price, evaluation class, and genre
        price = soup.find('span', {'class': 'kabuka'}).text.replace('円', '').strip()
        evaluation_class = soup.find('img', {'title': '今期予想'})['src'].split('/')[-1]
        genre = scrape_genre(soup)

        # Append the scraped data to the list
        new_data.append([row['Title'], row['Number'], row['URL'], price, evaluation_class, genre])

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        new_data.append([row['Title'], row['Number'], row['URL'], None, None, None])

# Create a new dataframe with the new data
new_df = pd.DataFrame(new_data, columns=['Title', 'Number', 'URL', 'Price', 'EvaluationClass', 'Genre'])

# Save the new dataframe to a CSV file
new_df.to_csv('stock_data_var2.csv', index=False)

print("Data scraping and CSV creation completed.")

# Function to process the CSV file
# Function to process the CSV file
def process_csv(input_filename, output_filename):
    processed_data = []

    with open(input_filename, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        headers = next(reader)  # Reading the header row
        processed_data.append(headers)  # Use existing headers, do not append 'Genre' again

        for row in reader:
            if row:  # Checking if the row is not empty
                evaluation_class = row[4]  # Assuming the EvaluationClass is the fifth column
                if 'gyouseki_1.gif' in evaluation_class or 'gyouseki_2.gif' in evaluation_class:
                    row[4] = '上出来'
                elif 'gyouseki_3.gif' in evaluation_class:
                    row[4] = '普通'
                elif 'gyouseki_4.gif' in evaluation_class or 'gyouseki_5.gif' in evaluation_class:
                    row[4] = '悪い'
                # Do not append Genre information again, it's already there
                processed_data.append(row)

    with open(output_filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(processed_data)

# Process the CSV file
input_filename = 'stock_data_var2.csv'  # Replace with your actual input file name
output_filename = 'stock_data_var2_complete.csv'  # Replace with your desired output file name
process_csv(input_filename, output_filename)


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
csv_files = ['stock_data_var2_complete.csv', 'stock_data_var2.csv', 'stock_data.csv']

# Iterate over each file and upload/update it
for csv_file in csv_files:
    file_path = f'{csv_file}'  # Update the path to your CSV files
    upload_or_update_file(drive_service, folder_id, file_path)

import os

script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)
os.chdir(script_dir)

# List of file names to be deleted
files_to_delete = ["stock_data.csv", "stock_data_var2_complete.csv", "stock_data_var2.csv"]

# Loop through the list and delete each file
for file in files_to_delete:
    if os.path.exists(file):
        os.remove(file)
        print(f"Deleted {file}")
    else:
        print(f"{file} does not exist")

