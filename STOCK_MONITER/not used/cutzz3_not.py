from PIL import Image
import numpy as np
import os
import pandas as pd
import shutil

# Function to safely delete a directory
def safe_delete_directory(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)
        
# Function to check if a pixel is red or blue
def is_red_or_blue(pixel, red_threshold=60, blue_threshold=60):
    red = pixel[0] > red_threshold and pixel[1] < red_threshold and pixel[2] < red_threshold
    blue = pixel[2] > blue_threshold and pixel[0] < blue_threshold and pixel[1] < blue_threshold
    return red or blue

# Function to process and save the image and CSV
def process_and_save_image(filename, input_folder, output_folder, modified_folder):
    # Load the image
    img_path = os.path.join(input_folder, filename)
    img = Image.open(img_path)
    img_array = np.array(img)

    # Apply the color filter
    color_mask = np.apply_along_axis(is_red_or_blue, 2, img_array)

    # Check for the presence of red or blue structures
    color_coords = np.argwhere(color_mask)
    if color_coords.size == 0:
        print(f"No red or blue-colored structures detected in {filename}. Skipping.")
        return

    # Find the boundaries of each structure
    structure_x_indices = np.where(color_mask.any(axis=0))[0]
    structure_boundaries = np.diff(structure_x_indices) > 1
    structure_starts = structure_x_indices[np.concatenate(([True], structure_boundaries))]
    structure_ends = structure_x_indices[np.concatenate((structure_boundaries, [True]))]

    # Prepare the dictionary to store the height information
    all_sticks_height_data = {
        'Stick_Number': [],
        'Top_Height': [],
        'Base_Height': [],
        'Height_Difference': []
    }

    # Process each stick, marking the image and saving height data
    for stick_number, (start, end) in enumerate(reversed(list(zip(structure_starts, structure_ends))), start=1):
        structure_mask = color_mask[:, start:end]
        vertical_indices = np.where(structure_mask.any(axis=1))[0]
        top = vertical_indices.min()
        base = vertical_indices.max()
        height_difference = base - top

        # Save height data
        all_sticks_height_data['Stick_Number'].append(f'Stick_Num_{stick_number}')
        all_sticks_height_data['Top_Height'].append(top)
        all_sticks_height_data['Base_Height'].append(base)
        all_sticks_height_data['Height_Difference'].append(height_difference)

        # Mark the image
        middle_x = (start + end) // 2
        img_array[top:base+1, middle_x] = [0, 144, 148]  # Middle line
        img_array[top, start:end+1] = [255, 170, 51]  # Top line
        img_array[base, start:end+1] = [0, 255, 0]  # Base line

    # Save modified image
    modified_img = Image.fromarray(img_array)
    modified_img.save(os.path.join(modified_folder, filename))

    # Save CSV
    all_sticks_height_df = pd.DataFrame(all_sticks_height_data)
    csv_file_name = filename.replace('.png', '.csv')
    all_sticks_height_df.to_csv(os.path.join(output_folder, csv_file_name), index=False)

# Delete existing output and modified directories
safe_delete_directory("stock_chart_data_csv")
safe_delete_directory("stock_chart_modified")

# Directories
input_folder = "stock_chart_original"
output_folder = "stock_chart_data_csv"
modified_folder = "stock_chart_modified"

# Create directories
os.makedirs(output_folder, exist_ok=True)
os.makedirs(modified_folder, exist_ok=True)

# Process each PNG file in the folder
for filename in os.listdir(input_folder):
    if filename.endswith(".png"):
        process_and_save_image(filename, input_folder, output_folder, modified_folder)
        print(f"Processed and saved {filename}")
