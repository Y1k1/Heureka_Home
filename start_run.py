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

# Send a GET request to the URL
response = requests.get(url)

# Print the status code (200 means success)
print("Status Code:", response.status_code)

# Print the response content
print("Response Content:", response.content)
