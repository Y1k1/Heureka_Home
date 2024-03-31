import csv
import os
import json
import html

def read_json(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)
    return data['first_half'], data['later_half']

def compare_base_heights(directory, first_half, later_half):
    stock_numbers = []
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            filepath = os.path.join(directory, filename)
            with open(filepath, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                try:
                    rows = list(reader)
                    stick_num_1_height = int(rows[0]['Base_Height'])
                    stick_num_2_height = int(rows[1]['Base_Height'])
                    if stick_num_2_height > stick_num_1_height:
                        stock_number = filename.split('_')[-1].split('.')[0]
                        stock_numbers.append(stock_number)
                except (IndexError, ValueError):
                    print(f"Error in file format: {filename}")
    return stock_numbers

def read_stock_titles(csv_file, stock_numbers):
    titles = {}
    with open(csv_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['Number'] in stock_numbers:
                titles[row['Number']] = row['Title']
    return titles

def save_results_html(stock_numbers, titles, output_file, first_half_15_image, later_half_15_image):
    with open(output_file, 'w') as file:
        file.write('<!DOCTYPE html><html><head><style>')
        file.write('.grid-container {display: grid; grid-template-columns: auto auto; padding: 0; margin: 0;}')
        file.write('.grid-item {padding: 10px;}')
        file.write('.title {text-align: center; font-size: 1.2em;}')
        file.write('iframe {width: 100%; height: 100vh; border: none;}')
        file.write('</style></head><body><div class="grid-container">')

        for stock_number in stock_numbers:
            title = titles.get(stock_number, "Unknown Title")
            iframe_url = f"{first_half_15_image}{stock_number}{later_half_15_image}"
            file.write(f'<div class="grid-item"><div class="title">{html.escape(title)}</div><iframe src="{html.escape(iframe_url)}"></iframe></div>')

        file.write('</div></body></html>')

# Define file paths
directory = 'stock_chart_data_csv'
csv_file = 'stock_data_var2_complete.csv'
json_file = 'src_data_stock_url.json'
html_output_file = 'result_stock_git_15.html'

# Execute functions
first_half, later_half = read_json(json_file)
stock_numbers = compare_base_heights(directory, first_half, later_half)
titles = read_stock_titles(csv_file, stock_numbers)
save_results_html(stock_numbers, titles, html_output_file, first_half_15_image, later_half_15_image)

print("Comparison complete. Check result_stock_git_15.html for output.")

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
    file_path = 'result_stock_git_15.html'  # Change to the path of the file to upload
    print(upload_file(f'{base_url}/upsave_file', file_path))
