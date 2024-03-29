import os
from PIL import Image
import numpy as np

# Function to check if a pixel is not gray
def is_not_gray(pixel, threshold=30):
    # Calculate if a pixel is gray by checking if the RGB values are close to each other
    r, g, b = pixel[:3]
    return abs(r - g) > threshold or abs(r - b) > threshold or abs(g - b) > threshold

# Print the current working directory
print("Current working directory:", os.getcwd())

# Path for the result directory
result_path = 'result'

# Check if the result directory exists, if not, create it
if not os.path.exists(result_path):
    os.makedirs(result_path)

# Open the image file
with Image.open('sample.png') as img:
    # Define the crop size
    left = 0
    top = 0
    right = 638
    bottom = 197

    # Crop the image
    cropped_img = img.crop((left, top, right, bottom))

    # Convert to RGB if it's in a different mode (like P or L)
    if cropped_img.mode != 'RGB':
        cropped_img = cropped_img.convert('RGB')

    # Convert image to numpy array
    cropped_array = np.array(cropped_img)

    # Create a new array to store the filtered image
    filtered_image_array = np.zeros_like(cropped_array)

    # Apply the filter to remove gray parts
    for i in range(cropped_array.shape[0]):
        for j in range(cropped_array.shape[1]):
            if is_not_gray(cropped_array[i, j]):
                filtered_image_array[i, j] = cropped_array[i, j]
            else:
                filtered_image_array[i, j] = [255, 255, 255]  # Set gray pixels to white

    # Convert the filtered array back to an image
    filtered_image = Image.fromarray(filtered_image_array)

    # Save the cropped and filtered image in the result directory
    filtered_image.save(os.path.join(result_path, 'cropped_sample.png'))

# The directory result should now contain the processed image
os.listdir(result_path)
