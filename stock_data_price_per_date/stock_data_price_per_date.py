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

# Function to process each CSV file
# Function to process each CSV file
def process_file(file_name):
    with open(file_name, "r", newline="", encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header
        for row in reader:
            number = row[1]
            url = f"https://s.kabutan.jp/stocks/{number}/historical_prices/daily/"
            data_for_past_week = scrape_stock_data(url)
            time.sleep(1)  # Polite delay

            # Create a directory to store results if it doesn't exist
            result_dir = "stock_data_price_per_date"
            if not os.path.exists(result_dir):
                os.makedirs(result_dir)

            # Write the scraped data to a new CSV file
            with open(os.path.join(result_dir, f"{number}_past.csv"), "w", newline="", encoding='utf-8') as resultfile:
                writer = csv.writer(resultfile)
                writer.writerow(["Date", "始値", "高値", "安値", "終値", "売買高(株)"])
                writer.writerows(data_for_past_week)
            print(f"Data for Number {number} saved to {result_dir}/{number}_past.csv")

# Directory containing the split CSV files
input_dir = "stock_data_price_per_date_pre"

# Counter for the number of processed files
processed_files_count = 0

# Maximum number of files to process
max_files_to_process = 2

# Iterate over each file in the directory
for file_name in os.listdir(input_dir):
    try:
        full_path = os.path.join(input_dir, file_name)
        if os.path.isfile(full_path) and file_name.startswith("stock_data_var2_complete_"):
            process_file(full_path)
            os.remove(full_path)  # Delete the file after processing
            processed_files_count += 1  # Increment the counter
            time.sleep(5)  # Wait for 5 seconds after deleting the file

            # Break the loop after processing max_files_to_process
            if processed_files_count >= max_files_to_process:
                break
    except Exception as e:
        print(f"An error occurred while processing {file_name}: {e}")


print(f"{processed_files_count} files processed and removed.")
