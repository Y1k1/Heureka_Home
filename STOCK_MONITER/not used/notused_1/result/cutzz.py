from PIL import Image
import numpy as np

img = Image.open("cropped_sample.png")

img_array = np.array(img)

def is_red_or_blue(pixel, red_threshold=60, blue_threshold=60):
    # Check if the pixel is either red or blue based on thresholds
    red_condition = pixel[0] > red_threshold and pixel[1] < red_threshold and pixel[2] < red_threshold
    blue_condition = pixel[2] > blue_threshold and pixel[0] < blue_threshold and pixel[1] < blue_threshold
    return red_condition or blue_condition

color_mask = np.apply_along_axis(is_red_or_blue, 2, img_array)

color_coords = np.argwhere(color_mask)

if color_coords.size == 0:
    raise ValueError("No red or blue-colored structures detected in the image.")

structure_x_indices = np.where(color_mask.any(axis=0))[0]

structure_boundaries = np.diff(structure_x_indices) > 1
structure_starts = structure_x_indices[np.concatenate(([True], structure_boundaries))]
structure_ends = structure_x_indices[np.concatenate((structure_boundaries, [True]))]


for start, end in zip(structure_starts, structure_ends):
    structure_mask = color_mask[:, start:end]
    vertical_indices = np.where(structure_mask.any(axis=1))[0]
    top = vertical_indices.min()
    base = vertical_indices.max()

    middle_x = (start + end) // 2
    img_array[top:base+1, middle_x] = [0, 144, 148]  

    img_array[top, start:end+1] = [255, 170, 51]  # Blue line for the top
    img_array[base, start:end+1] = [0, 255, 0]  # Green line for the base


marked_image = Image.fromarray(img_array)

modified_image_path = "cropped_sample_marked.png"
marked_image.save(modified_image_path)

modified_image_path
