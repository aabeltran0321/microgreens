import requests
from Parser_WTA import Parser
import time
import time
from datetime import datetime, time as dt_time
from threading import Thread
tupmParser = Parser("TUPM,", "\r", 1, 200)
tupmParser1 = Parser("TUPM,", "\n", 1, 200)

floatParser = Parser("Float", "\r", 1, 200)
floatParser1 = Parser("Float", "\n", 1, 200)

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
        dict1 = get_hilo()
        return dict1, [float(d) for d in data]
    return {},[]

def EC_process():
    global Serial1, EC_Trigg
    sch1 = Scheduler(1000)
    isRunning = True
    ECcnt = 0
    vol_time_amount = 34
    while isRunning:
        if sch1.Event():
            if ECcnt == 0:
                Serial1.println("PPU3,1")
                Serial1.println("PPU4,0")
            elif ECcnt == vol_time_amount:
                Serial1.println("PPU3,0")
                Serial1.println("PPU4,0")
            elif ECcnt == (300 + vol_time_amount):
                Serial1.println("PPU3,0")
                Serial1.println("PPU4,1")
            elif ECcnt == (300 + vol_time_amount + vol_time_amount):
                Serial1.println("PPU3,0")
                Serial1.println("PPU4,0")
            elif ECcnt == (900 + vol_time_amount + vol_time_amount):
                isRunning = False
                EC_Trigg = False



with open("./test.csv", "r", encoding="utf8") as f:
    Serial2 = f.read()
    f.close
from serialport import HardwareSerial


#Serial Port
dev_tty = "COM2"
Serial1 = HardwareSerial(dev_tty=dev_tty)
Serial1.begin(9600)
minSch1 = Scheduler(60000)
irrSch1 = Scheduler(60000)
irrCnt = 0

EC_Trigg = False
while True:
    EC_value = 0.0
    if Serial1.available():
        c = Serial1.read()
        c = c.decode()
        dict1, data = ParsingProcess(c)

        if floatParser.available(c) or floatParser1.available(c):
            if "on" in floatParser.data.lower() or "on" in floatParser1.data.lower():
                Serial1.println("SVLV,0")
            if "off" in floatParser.data.lower() or "off" in floatParser1.data.lower():
                Serial1.println("SVLV,1")
        if len(data):
            dict2 = {}
            dict2['Temperature'] = data[0]
            dict2['Humidity'] = data[1]
            dict2['EC'] = data[2]
            dict2['pH Level'] = data[3]
            dict2['ORP'] = data[4]
            EC_value = data[2]

            
            for k in dict1:
                low = float(dict1[k]['low'])
                high = float(dict1[k]['high'])
                val = dict2[k]
                command = ""
                if k == "Humidity":
                    if val > high:
                        command = "DEHU,1"
                    else:
                        command = "DEHU,0"
                elif k == "ORP":
                    if val < low:
                        command = "OZON,1"
                    else:
                        command = "OZON,0"

                elif k == "Temperature":
                    if val > high:
                        command = ["FAN1,1","FAN2,1", "FAN3,1"]
                    else:
                        command = ["FAN1,0","FAN2,0", "FAN3,0"]

                elif k == "pH Level":
                    if val > high:
                        command = ["PPU2,1", "PPU1,0"]

                    if val < low:
                        command = ["PPU1,1", "PPU2,0"]
                    else:
                        command = ["PPU1,0", "PPU2,0"]

                elif k == "EC" and not(EC_Trigg):
                    if val < low:
                        Thread1 = Thread(target=EC_process)
                        Thread1.start()


                if isinstance(command, str):
                    Serial1.println(command)
                else:
                    for cmd in command:
                        Serial1.println(cmd)
    if irrSch1.Event():
        irrCnt += 1
        if irrCnt == 1:
            Serial1.println("WATR,1")
        if irrCnt == 16:
            Serial1.println("WATR,0")
        if irrCnt == 30:
            irrCnt = 0
    if minSch1.Event():
        now = datetime.now().time()
        if dt_time(6, 0) <= now <= dt_time(18, 0):
            print("It is between 6 AM and 6 PM.")
            Serial1.println("LGT1,0")
            time.sleep(0.1)
            Serial1.println("LGT2,0")
            time.sleep(0.1)
            Serial1.println("LGT3,0")
            time.sleep(0.1)
        else:
            print("It is outside 6 AM to 6 PM.")
            Serial1.println("LGT1,1")
            time.sleep(0.1)
            Serial1.println("LGT2,1")
            time.sleep(0.1)
            Serial1.println("LGT3,1")
            time.sleep(0.1)

        
        Serial1.println("GETDATA")
        
