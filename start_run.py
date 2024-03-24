import requests
import time

url = "https://api.render.com/v1/services/srv-ci1vivak728i8tc26chg/resume"

headers = {
    "accept": "application/json",
    "authorization": "Bearer rnd_6qDvOwR9I1AUFzV8Xv7IrRFBfjOL"
}

response = requests.post(url, headers=headers)

print(response.text)

time.sleep(3)

import requests

url = 'https://yk-fuku.onrender.com'

try:
    # Send a GET request to the URL with a timeout of 10 seconds
    response = requests.get(url, timeout=10)

    # Print the status code (200 means success)
    print("Status Code:", response.status_code)

    # Print the response content
    print("Response Content:", response.content)
except requests.exceptions.Timeout:
    # This code will be executed if the request takes longer than 10 seconds
    print("The request timed out after 10 seconds.")
except requests.exceptions.RequestException as e:
    # This code will handle other kinds of exceptions
    print(f"An error occurred: {e}")
