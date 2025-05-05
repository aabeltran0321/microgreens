import requests

# URL endpoint
url = "https://bigboysautomation.pythonanywhere.com/tupmicrogreens/hilo"

# Example payload — replace with actual expected data
data = {
    "key1": "value1",
    "key2": "value2"
}

# Send POST request
response = requests.post(url, verify=False)

# Print response
print("Status Code:", response.status_code)
print("Response JSON:", response.text)
