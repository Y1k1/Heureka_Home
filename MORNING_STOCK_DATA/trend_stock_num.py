import requests
from bs4 import BeautifulSoup
import csv
import os

script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)
os.chdir(script_dir)

# Fetch the HTML content of the webpage
url = "https://kabutan.jp/info/accessranking/3_2"
response = requests.get(url)
html_content = response.text

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(html_content, "html.parser")

# Find all <td> elements
td_elements = soup.find_all("td")

# Initialize an empty list to store the extracted codes
codes = []

# Iterate through each <td> element
for td in td_elements:
    # Find all <a> elements within the <td> element
    a_elements = td.find_all("a")
    # Iterate through each <a> element
    for a in a_elements:
        # Extract the 'href' attribute value
        href = a.get("href")
        # Check if the 'href' attribute value matches the specified pattern
        if href and href.startswith("/stock/?code="):
            # Extract the code from the 'href' attribute value
            code = href.split("=")[-1]
            # Append the extracted code to the list
            codes.append(code)

# Save the codes into a CSV file
with open("stock_codes_collectible.csv", "w", newline="") as file:
    writer = csv.writer(file)
    # Write the header
    writer.writerow(["Stock Code"])
    # Write each code as a new row
    for code in codes:
        writer.writerow([code])

print("Stock codes saved to stock_codes.csv")
