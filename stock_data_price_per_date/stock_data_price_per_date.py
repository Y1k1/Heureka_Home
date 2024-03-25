# Filename of the output file
output_filename = "output_file.txt"

# Number of lines to write
num_lines = 100

# Open the file in write mode
with open(output_filename, "w") as file:
    # Write 100 lines
    for i in range(1, num_lines + 1):
        file.write(f"Line {i}\n")

print(f"File '{output_filename}' has been written with {num_lines} lines.")
