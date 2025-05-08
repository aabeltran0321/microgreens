import requests
from Parser_WTA import Parser
import time
tupmParser = Parser("TUPM,", "\r", 1, 200)
tupmParser1 = Parser("TUPM,", "\n", 1, 200)

class Scheduler:
    def __init__(self,millis):
        self.start_time = time.time()
        self.sec = 0.0
        self.sec=millis/1000
    def Event(self):
        if (time.time() - self.start_time) > self.sec:
            self.start_time = time.time()
            return True
        else:
            return False

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
            low = float(dict1[k]['low'])
            high = float(dict1[k]['high'])
            val = dict2[k]
            command = ""
            if k == "Humidity":
                if val > high:
                    command = "DEHU1"
                else:
                    command = "DEHU0"
            elif k == "ORP":
                if val < low:
                    command = "OZON1"
                else:
                    command = "OZON0"

            elif k == "Temperature":
                if val > high:
                    command = ["FAN11","FAN21", "FAN31"]
                else:
                    command = ["FAN10","FAN20", "FAN30"]

            elif k == "pH Level":
                if val > high:
                    command = ["PPU21", "PPU10"]

                if val < low:
                    command = ["PPU11", "PPU20"]
                else:
                    command = ["PPU10", "PPU20"]

            if isinstance(command, str):
                print(command)
            else:
                for cmd in command:
                    print(cmd)
        break