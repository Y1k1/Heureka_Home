from PIL import Image
import numpy as np
import pandas as pd
import os

# Define the function to check if a pixel is red or blue
def is_red_or_blue(pixel, red_threshold=60, blue_threshold=60):
    red_condition = pixel[0] > red_threshold and pixel[1] < red_threshold and pixel[2] < red_threshold
    blue_condition = pixel[2] > blue_threshold and pixel[0] < blue_threshold and pixel[1] < blue_threshold
    return red_condition or blue_condition

# Define the folders for processing and output
input_folder = "stock_chart_original"
output_folder = "stock_chart_data_csv"
os.makedirs(output_folder, exist_ok=True)

# Process each PNG file in the folder
for filename in os.listdir(input_folder):
    if filename.endswith(".png"):
        img_path = os.path.join(input_folder, filename)
        img = Image.open(img_path)
        img_array = np.array(img)
        color_mask = np.apply_along_axis(is_red_or_blue, 2, img_array)

        # Check for the presence of red or blue structures
        color_coords = np.argwhere(color_mask)
        if color_coords.size == 0:
            print(f"No red or blue-colored structures detected in {filename}. Skipping.")
            continue

        # Find the boundaries of each structure
        structure_x_indices = np.where(color_mask.any(axis=0))[0]
        structure_boundaries = np.diff(structure_x_indices) > 1
        structure_starts = structure_x_indices[np.concatenate(([True], structure_boundaries))]
        structure_ends = structure_x_indices[np.concatenate((structure_boundaries, [True]))]

        # Prepare the dictionary to store the height information
        all_sticks_height_data = {
            'Stick_Number': [],
            'Base_Height': [],
            'Top_Height': [],
            'Height_Difference': []
        }

        # Process each stick, saving height data
        for stick_number, (start, end) in enumerate(zip(structure_starts, structure_ends), start=1):
            structure_mask = color_mask[:, start:end]
            vertical_indices = np.where(structure_mask.any(axis=1))[0]
            top = vertical_indices.min()
            base = vertical_indices.max()
            height_difference = base - top

            # Save height data
            all_sticks_height_data['Stick_Number'].append(f'Stick_Num_{stick_number}')
            all_sticks_height_data['Base_Height'].append(top)
            all_sticks_height_data['Top_Height'].append(base)
            all_sticks_height_data['Height_Difference'].append(height_difference)

        # Convert the height data dictionary to a DataFrame and save as CSV
        all_sticks_height_df = pd.DataFrame(all_sticks_height_data)
        csv_file_name = filename.replace('.png', '.csv')
        csv_file_path = os.path.join(output_folder, csv_file_name)
        all_sticks_height_df.to_csv(csv_file_path, index=False)

        # Output paths
        print(f"Processed {filename}. CSV file saved to: {csv_file_path}")
