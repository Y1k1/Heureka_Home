import os
import requests
from PIL import Image
import numpy as np
import csv
import json
import time

def is_not_gray(pixel, threshold=30):
    r, g, b = [int(val) for val in pixel[:3]]
    return abs(r - g) > threshold or abs(r - b) > threshold or abs(g - b) > threshold

result_path = 'stock_chart_original'
if not os.path.exists(result_path):
    os.makedirs(result_path)

# Load JSON data
with open('src_data_stock_url.json', 'r') as json_file:
    data = json.load(json_file)
    first_half_url = data['first_half_15_image']
    later_half_url = data['later_half_15_image']

def process_image(image_id):
    start_time = time.time()

    # Construct the full URL
    full_url = f"{first_half_url}{image_id}{later_half_url}"
    response = requests.get(full_url)
    temp_image_path = 'downloaded_image.png'
    if response.status_code == 200:
        with open(temp_image_path, 'wb') as f:
            f.write(response.content)
        with Image.open(temp_image_path) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img_array = np.array(img)
            filtered_image_array = np.zeros_like(img_array)
            for i in range(img_array.shape[0]):
                for j in range(img_array.shape[1]):
                    if is_not_gray(img_array[i, j]):
                        filtered_image_array[i, j] = img_array[i, j]
                    else:
                        filtered_image_array[i, j] = [255, 255, 255]
            filtered_image = Image.fromarray(filtered_image_array)
            filtered_image.save(os.path.join(result_path, f'filtered_sample_{image_id}.png'))
        os.remove(temp_image_path)
    else:
        print(f"Failed to download image for ID {image_id}.")

    # Calculate the remaining time to sleep for
    end_time = time.time()
    sleep_time = max(0.5 - (end_time - start_time), 0)
    time.sleep(sleep_time)

overall_start_time = time.time()  # Start time for the entire process

csv_folder = 'csv_to_run'
for file in os.listdir(csv_folder):
    if file.endswith('.csv'):
        with open(os.path.join(csv_folder, file), newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                image_id = row[0]
                process_image(image_id)

overall_end_time = time.time()  # End time for the entire process
total_time = overall_end_time - overall_start_time  # Total time calculation
print(f"Total processing time: {total_time:.2f} seconds.")  # Print total time

os.listdir(result_path)
