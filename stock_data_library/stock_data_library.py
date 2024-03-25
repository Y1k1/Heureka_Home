import requests
from bs4 import BeautifulSoup
import csv
import os

script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)
os.chdir(script_dir)

# Function to check if a string contains a percentage value
def contains_percentage(text):
    return "%" in text

# Function to get URLs, titles, and numbers from a single page
def get_urls_titles_numbers(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Find all hyperlink elements with either 'green' or 'red' class
            hyperlink_elements = soup.find_all('a', class_=['green', 'red'])

            # Initialize a list to store URL, title, and number pairs
            url_title_number_list = []

            for element in hyperlink_elements:
                # Extract URL from the 'href' attribute
                href = element.get('href')

                # Ensure that the URL suffix is appended with "https://walletinvestor.com/"
                if not href.startswith("https://walletinvestor.com/"):
                    href = "https://walletinvestor.com/" + href

                # Extract title and number from the text content
                title_with_number = element.text.strip()
                title = title_with_number.split('(')[0].strip()
                number = title_with_number.split('(')[-1].replace(')', '').strip()

                # Check if the title does not contain "Join Now!" or a percentage value
                if title != "Join Now!" and not contains_percentage(title):
                    # Append URL, title, and number to the list
                    url_title_number_list.append((href, title, number))

            return url_title_number_list
        else:
            print(f"Failed to fetch URL. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Function to scrape data from all pages and save to a CSV file
def scrape_and_save_to_csv(base_url, num_pages, output_file):
    all_data = []
    for page in range(1, num_pages + 1):
        url = f"{base_url}?page={page}&per-page=100"
        page_data = get_urls_titles_numbers(url)
        if page_data:
            all_data.extend(page_data)
    
    # Save the data to a CSV file
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Title', 'Number', 'URL'])
        for data in all_data:
            csv_writer.writerow([data[1], data[2], data[0]])

# Example usage:
base_url = "https://walletinvestor.com/tse-stock-forecast"
num_pages = 40  # Specify the number of pages to scrape
output_file = "stock_data.csv"  # Specify the output CSV file name

scrape_and_save_to_csv(base_url, num_pages, output_file)
print(f"Data scraped and saved to {output_file}")

import requests
from bs4 import BeautifulSoup
import csv
import os

script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)
os.chdir(script_dir)

# Function to read existing stock numbers from the CSV file
def read_existing_numbers(filename):
    existing_numbers = set()
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            for row in csv_reader:
                if row:  # Check if row is not empty
                    existing_numbers.add(row[1])  # Assuming number is in the second column
    except FileNotFoundError:
        pass  # If file doesn't exist, we just start with an empty set
    return existing_numbers

# Function to scrape data from a single page
def get_stock_data(url, existing_numbers):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            stock_elements = soup.find_all('td', class_='name')

            stock_data_list = []
            for element in stock_elements:
                link = element.find('a')
                if link:
                    href = "https://www.marketwatch.com" + link.get('href')
                    title = link.text.strip().split(' (')[0].strip()
                    number = link.text.strip().split(' (')[-1].replace(')', '').strip()
                    if number not in existing_numbers:
                        stock_data_list.append((title, number, href))

            return stock_data_list
        else:
            print(f"Failed to fetch URL. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Function to scrape data from all pages and save to a CSV file
def scrape_and_save_to_csv(base_url, num_pages, output_file):
    existing_numbers = read_existing_numbers(output_file)
    all_data = []
    for page in range(1, num_pages + 1):
        url = f"{base_url}/{page}"
        page_data = get_stock_data(url, existing_numbers)
        if page_data:
            all_data.extend(page_data)

    # Save the new data to the CSV file
    with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        for data in all_data:
            csv_writer.writerow([data[0], data[1], data[2]])

# Example usage:
base_url = "https://www.marketwatch.com/tools/markets/stocks/country/japan"
num_pages = 27
output_file = "stock_data.csv"

scrape_and_save_to_csv(base_url, num_pages, output_file)
print(f"Data scraped and updated in {output_file}")
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

