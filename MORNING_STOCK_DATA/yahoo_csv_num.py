import requests
import re
import os

script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)
os.chdir(script_dir)
# URLs to be opened
urls = ["https://finance.yahoo.co.jp/stocks/ranking/bbs?market=all&term=daily&page=1",
        "https://finance.yahoo.co.jp/stocks/ranking/bbs?market=all&term=daily&page=2"]

all_numbers = []

for url in urls:
    response = requests.get(url)
    if response.status_code == 200:
        # Extract numbers from the response text
        numbers = re.findall(r'<li class="vv_mrYM6">(\d+)</li>', response.text)
        all_numbers.extend(numbers)
    else:
        print(f"Error accessing {url}")

# Saving the numbers to a CSV file
csv_content = "\n".join(all_numbers)
with open("extracted_numbers.csv", "w") as file:
    file.write(csv_content)

print("Numbers extracted and saved to 'extracted_numbers.csv'")
