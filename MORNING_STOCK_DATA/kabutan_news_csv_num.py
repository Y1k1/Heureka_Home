import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
from collections import Counter
import csv

# Function to scrape and get news content
def scrape_news():
    base_url = 'https://kabutan.jp'
    ranking_url = urljoin(base_url, '/info/accessranking/2_1')
    response = requests.get(ranking_url)
    
    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    td_elements = soup.find_all('td', class_='acrank_title')

    urls = [urljoin(base_url, td.find('a', href=True)['href']) for td in td_elements[:30] if td.find('a', href=True)]

    data = {}
    for url in urls:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            div_body = soup.find('div', class_='body')
            if div_body:
                text_inside_div = div_body.get_text(strip=True)
                unique_key = url.split('/')[-1]
                data[unique_key] = text_inside_div
        else:
            print(f"Failed to retrieve content from {url}, status code: {response.status_code}")

    return data

# Function to process the scraped data
def process_data(data):
    number_counter = Counter()

    for text in data.values():
        numbers = re.findall(r'\b\d{4}\b', text)
        number_counter.update(numbers)

    return number_counter

# Function to save data to CSV
# Function to save data to CSV
def save_to_csv(counter, csv_file_path):
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Stock Number'])
        for number in counter.keys():
            writer.writerow([number])

# The rest of your code remains the same


# Main function to integrate all steps
def main():
    data = scrape_news()
    number_counter = process_data(data)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file_path = os.path.join(script_dir, 'stock_kabutan_collectible.csv')
    save_to_csv(number_counter, csv_file_path)
    print(f"CSV file saved: {csv_file_path}")

if __name__ == "__main__":
    main()
