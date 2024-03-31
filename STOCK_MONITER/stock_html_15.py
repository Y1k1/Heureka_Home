import csv
import os
import json
import html
import requests
import base64

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

def save_results_html(stock_numbers, titles, output_file, first_half, later_half):
    with open(output_file, 'w') as file:
        file.write('<!DOCTYPE html><html><head><style>')
        file.write('.grid-container {display: grid; grid-template-columns: auto auto; padding: 0; margin: 0;}')
        file.write('.grid-item {padding: 10px;}')
        file.write('.title {text-align: center; font-size: 1.2em;}')
        file.write('iframe {width: 100%; height: 100vh; border: none;}')
        file.write('</style></head><body><div class="grid-container">')

        for stock_number in stock_numbers:
            title = titles.get(stock_number, "Unknown Title")
            iframe_url = f"{first_half}{stock_number}{later_half}"
            file.write(f'<div class="grid-item"><div class="title">{html.escape(title)}</div><iframe src="{html.escape(iframe_url)}"></iframe></div>')

        file.write('</div></body></html>')

# New function to upload file to GitHub
def upload_file_to_github(file_name, path, pat):
    with open(file_name, 'rb') as file:
        content = base64.b64encode(file.read()).decode()

    url = f'https://api.github.com/repos/{username}/{repo}/contents/{path}'

    response = requests.get(url, headers={'Authorization': f'token {pat}'})
    sha = None
    if response.status_code == 200:
        sha = response.json()['sha']

    data = {
        'message': f'Upload {os.path.basename(file_name)}',
        'content': content,
        'branch': 'master',
    }

    if sha:
        data['sha'] = sha

    response = requests.put(url, headers={'Authorization': f'token {pat}'}, json=data)

    if response.status_code in (200, 201):
        print('File uploaded successfully.')
    else:
        print('Failed to upload file:', response.content)

# Main execution logic
if __name__ == "__main__":
    # Paths and files configuration
    directory = 'stock_chart_data_csv'
    csv_file = 'stock_data_var2_complete.csv'
    json_file = 'src_data_stock_url.json'
    html_output_file = 'result.html'
    git_pat_path = 'git_pat.json'
    repo = 'Heureka_Home'
    username = 'Y1k1'
    path_in_repo = 'STOCK_MONITER/result.html'

    # Process stock data and generate HTML
    first_half, later_half = read_json(json_file)
    stock_numbers = compare_base_heights(directory, first_half, later_half)
    titles = read_stock_titles(csv_file, stock_numbers)
    save_results_html(stock_numbers, titles, html_output_file, first_half, later_half)
    print("Comparison complete. Check result.html for output.")

    # Load GitHub PAT and upload the file
    with open(git_pat_path, 'r') as pat_file:
        pat_data = json.load(pat_file)
        pat = pat_data['pat']

    upload_file_to_github(html_output_file, path_in_repo, pat)
