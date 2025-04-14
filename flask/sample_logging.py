import requests
import random
import time

# Flask server URL
url = 'http://127.0.0.1:5000/log'

# Sample parameters
parameters = ['pH Level', 'EC', 'ORP', 'Temperature', 'Humidity']

# Send 5 logs (one for each parameter)
for param in parameters:
    value = round(random.uniform(5.0, 9.0), 2) if param == 'pH Level' else round(random.uniform(100, 500), 2)

    payload = {
        'parameter': param,
        'value': value
    }

    response = requests.post(url, json=payload)

    print(f'Logged: {param} = {value} -> {response.status_code} | {response.json()}')

    time.sleep(0.1)
