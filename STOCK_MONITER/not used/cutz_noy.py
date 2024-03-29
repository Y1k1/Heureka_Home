import os
import requests
from PIL import Image
import numpy as np
import csv

def is_not_gray(pixel, threshold=30):
    r, g, b = [int(val) for val in pixel[:3]]
    return abs(r - g) > threshold or abs(r - b) > threshold or abs(g - b) > threshold

result_path = 'result'
if not os.path.exists(result_path):
    os.makedirs(result_path)

# Function to process each image
def process_image(image_id):
    url = f'https://chart.iris.sbisec.co.jp/sbi/as/Mchart-mchart.html?ricCode={image_id}.T&type=real&hash=84a2f278917bab7efc0252c86fd36bacfef2c732&size=0&mode=15&DaysNum=1&main=C&addon=None'

    response = requests.get(url)
    if response.status_code == 200:
        with open('downloaded_image.png', 'wb') as f:
            f.write(response.content)

        with Image.open('downloaded_image.png') as img:
            left, top, right, bottom = 0, 0, 638, 197
            cropped_img = img.crop((left, top, right, bottom))
            if cropped_img.mode != 'RGB':
                cropped_img = cropped_img.convert('RGB')

            cropped_array = np.array(cropped_img)
            filtered_image_array = np.zeros_like(cropped_array)

            for i in range(cropped_array.shape[0]):
                for j in range(cropped_array.shape[1]):
                    if is_not_gray(cropped_array[i, j]):
                        filtered_image_array[i, j] = cropped_array[i, j]
                    else:
                        filtered_image_array[i, j] = [255, 255, 255]

            filtered_image = Image.fromarray(filtered_image_array)
            filtered_image.save(os.path.join(result_path, f'cropped_sample_{image_id}.png'))
    else:
        print(f"Failed to download image for ID {image_id}.")

# Read IDs from CSV and process each image
with open('filtered_stock_numbers-2.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        image_id = row[0]
        process_image(image_id)

# List the result directory
os.listdir(result_path)
