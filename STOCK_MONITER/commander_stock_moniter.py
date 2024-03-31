import requests

def download_file(url, filename):
    try:
        with requests.get(url, stream=True) as response:
            # Check if the request was successful
            if response.status_code == 200:
                with open(filename, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192): 
                        file.write(chunk)
                return f"File downloaded successfully: {filename}"
            else:
                return f"Failed to download file. Status code: {response.status_code}"
    except Exception as e:
        return f"An error occurred: {e}"

# Example usage
url = "https://yk-fuku.onrender.com/downrequp_a_t"
filename = "git_pat.json"  # Replace with the appropriate file extension
result = download_file(url, filename)
print(result)

import subprocess
import threading
import time

def run_periodically():
    global run_thread
    while run_thread:
        subprocess.call(["python3", "stock_html_15.py"])
        time.sleep(30)

# Start the recurring process in a separate thread
run_thread = True
thread = threading.Thread(target=run_periodically)
thread.start()

# Start the first script
p1 = subprocess.Popen(["python3", "analyze_colored_15.py"])

# Start the second script
p2 = subprocess.Popen(["python3", "url_image_15.py"])

# Wait for both scripts to complete
p1.wait()
p2.wait()

# Stop the recurring process
run_thread = False
thread.join()

# Run the recurring process one last time, if it hasn't run already
subprocess.call(["python3", "stock_html_15.py"])
