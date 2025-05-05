import requests
from Parser_WTA import Parser

tupmParser = Parser("TUPM,", "\r", 1, 200)
tupmParser1 = Parser("TUPM,", "\n", 1, 200)
def get_hilo():
    # URL endpoint
    url = "https://bigboysautomation.pythonanywhere.com/tupmicrogreens/hilo"
    # Send POST request
    response = requests.post(url, verify=False)

    return response.json()


with open("test.csv", "r", encoding="utf8") as f:
    Serial1 = f.read()
    f.close


for c in Serial1:
    if tupmParser.available(c) or tupmParser1.available(c):
        # hilo1 = get_hilo()


        # for data in hilo1:
        #     low_value = hilo1[data]["low"]
        #     hi_value = hilo1[data]["high"]

        #     print(hi_value, low_value)
        if len(tupmParser.data):
            data = tupmParser.data.replace("\r","")
            data = data.replace("\n", "")
            data = data.split(",")
            
        elif len(tupmParser1.data):
            data = tupmParser.data.replace("\r", "")
            data = data.replace("\n", "")
            data = data.split(",")

        print(data)
