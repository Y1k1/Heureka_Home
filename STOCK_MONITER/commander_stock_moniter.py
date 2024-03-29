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
