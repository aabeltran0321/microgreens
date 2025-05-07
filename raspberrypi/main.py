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


def ParsingProcess(c):
    if tupmParser.available(c) or tupmParser1.available(c):
        if len(tupmParser.data):
            data = tupmParser.data.replace("\r","")
            data = data.replace("\n", "")
            data = data.split(",")
            
        elif len(tupmParser1.data):
            data = tupmParser.data.replace("\r", "")
            data = data.replace("\n", "")
            data = data.split(",")

        return [float(d) for d in data]
    return []

with open("./test.csv", "r", encoding="utf8") as f:
    Serial2 = f.read()
    f.close
from serialport import HardwareSerial


#Serial Port
dev_tty = "COM2"
#Serial1 = HardwareSerial(dev_tty=dev_tty)
#Serial1.begin(9600)

dict1 = get_hilo()

commands = {
    'ORP': 'OZON',
    'EC': 'PPU3',
    'pH Level': 'PPU1',
}

for c in Serial2:
    data = ParsingProcess(c)
    if len(data):
        dict2 = {}
        dict2['Temperature'] = data[0]
        dict2['Humidity'] = data[1]
        dict2['EC'] = data[2]
        dict2['pH Level'] = data[3]
        dict2['ORP'] = data[4]

        
        for k in dict1:
            low = dict1[k]['low']
            high = dict1[k]['high']
            val = dict2[k]
            print(val, k,low < val < high)
        break