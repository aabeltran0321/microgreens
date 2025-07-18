import requests
from Parser_WTA import Parser
import time
import time
from datetime import datetime, time as dt_time
from threading import Thread
import json
import base64
import cv2

domain1 = "https://bigboysautomation.pythonanywhere.com"
tupmParser = Parser("TUPM,", "\r", 1, 200)
tupmParser1 = Parser("TUPM,", "\n", 1, 200)

floatParser = Parser("Float", "\r", 1, 200)
floatParser1 = Parser("Float", "\n", 1, 200)

switch = {
    "ON": 1,
    "OFF": 0
}

params_dict = {
    "Solution A": "PPU3",
    "Solution B": "PPU4",
    "pH Up": "PPU1",
    "pH Down": "PPU2",
    "Water Pump": "WATR",
    "Humidifier": "DEHU",
    "Ozone Generator": "OZON",
    "Solenoid Valve": "SVLV",
    "Fan 1": "FAN1",
    "Fan 2": "FAN2",
    "Fan 3": "FAN3",
    "Light 1": "LGT1",
    "Light 2": "LGT2",
    "Light 3": "LGT3",
    "Light 4": "LGT4",
}

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
    url = f"{domain1}/tupmicrogreens/hilo"
    # Send POST request
    response = requests.post(url, verify=False)

    return response.json()
def upload_base64_image(image_path):
    
    # Endpoint for uploading base64 image
    url = f"{domain1}/tupmicrogreens/api/upload"

    # Read and encode the image as base64
    with open(image_path, "rb") as img_file:
        b64_string = base64.b64encode(img_file.read()).decode("utf-8")

    # POST request with form data
    response = requests.post(url, data={"base64str": b64_string}, verify=False)

    return response.text

def get_manual_controls():
    # URL endpoint
    url = f"{domain1}/tupmicrogreens/api/controls"
    # Send POST request
    response = requests.get(url, verify=False)

    return response.json()

def get_machine_mode():
    # URL endpoint
    url = f"{domain1}/tupmicrogreens/api/machinemode"
    # Send POST request
    response = requests.get(url, verify=False)

    return response.json()["machine_mode"]

def post2db(parameter, value):


    url = f'{domain1}/tupmicrogreens/log'  # Change to your server address

    payload = {
        'parameter': parameter,  # Example parameter
        'value': value               # Example value
    }

    headers = {'Content-Type': 'application/json'}

    response = requests.post(url, data=json.dumps(payload), headers=headers)

    print('Status Code:', response.status_code)
    print('Response:', response.text)

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
        print("tupm: ",data)
        return dict1, [float(d) for d in data]
    return {},[]
    
runningOnce = False
phRunningOnce = False
def EC_process():
    global Serial1, EC_Trigg, runningOnce
    sch1 = Scheduler(1000)
    isRunning = True
    ECcnt = 0
    vol_time_amount = 34
    print("starting ec process")
    while isRunning:
        if sch1.Event():
            if ECcnt == 0:
                Serial1.println("CMD,PPU3,1")
                time.sleep(1)
                Serial1.println("CMD,PPU4,0")
            elif ECcnt == vol_time_amount:
                Serial1.println("CMD,PPU3,0")
                time.sleep(1)
                Serial1.println("CMD,PPU4,0")
            elif ECcnt == (300 + vol_time_amount):
                Serial1.println("CMD,PPU3,0")
                time.sleep(1)
                Serial1.println("CMD,PPU4,1")
            elif ECcnt == (300 + vol_time_amount + vol_time_amount):
                Serial1.println("CMD,PPU3,0")
                time.sleep(1)
                Serial1.println("CMD,PPU4,0")
            elif ECcnt == (900 + vol_time_amount + vol_time_amount):
                isRunning = False
                EC_Trigg = False
                
            ECcnt +=1
    runningOnce = False

def phProcess(val,high,low):
    global phRunningOnce
    sch2 = Scheduler(1000)
    phCnt = 0
    while True:
        if sch2.Event():
            if phCnt == 0:
                if val > high:
                    Serial1.println("CMD,PPU2,1")
                    time.sleep(1)
                    Serial1.println("CMD,PPU1,0")
                    time.sleep(1)

                elif val < low:
                    Serial1.println("CMD,PPU1,1")
                    time.sleep(1)
                    Serial1.println("CMD,PPU2,0")
                    time.sleep(1)
                else:
                    Serial1.println("CMD,PPU2,0")
                    time.sleep(1)
                    Serial1.println("CMD,PPU1,0")
                    time.sleep(1)
                    return
            if phCnt == 20:
                Serial1.println("CMD,PPU2,0")
                time.sleep(1)
                Serial1.println("CMD,PPU1,0")
                time.sleep(1)
            if phCnt == 300:
                phRunningOnce = True
                return

            phCnt +=1




# image_path = "1747581330826.jpg"
# print(upload_base64_image(image_path))

with open("./test.csv", "r", encoding="utf8") as f:
    Serial2 = f.read()
    f.close
from serialport import HardwareSerial


#Serial Port
dev_tty = "/dev/ttyACM0"
Serial1 = HardwareSerial(dev_tty=dev_tty)
Serial1.begin(9600)
minSch1 = Scheduler(30000)
irrSch1 = Scheduler(60000)
irrCnt = 0
manual_control_sch = Scheduler(3000)
image_upload_sch = Scheduler(5000)
machine_mode = ""
EC_Trigg = False
try:
    cap = cv2.VideoCapture(0)
except:
    cap = cv2.VideoCapture(1)
frame = None
while True:

    ret, frame = cap.read()

    if ret:
        print("capturing frames from webcam")
        cv2.imshow("frame", frame)
        cv2.waitKey(1)

    if manual_control_sch.Event():

       machine_mode = get_machine_mode()

       controls_dict = get_manual_controls()

       for params in controls_dict:
           ret, frame = cap.read()
           if ret:
               print("capturing frames from webcam")
               cv2.imshow("frame", frame)
               cv2.waitKey(1)
           
           val = switch[controls_dict[params]]
           header = params_dict[params]
           
           if machine_mode == "manual":
               command11 = f"CMD,{header},{val}?"
               Serial1.println(command11)
               time.sleep(1)
           if header == "LGT4":
               command11 = f"CMD,{header},{val}?"
               Serial1.println(command11)
               time.sleep(1)
               

    if image_upload_sch.Event():
        if frame is None:
            continue
        image_path = "temp_frame.jpg"
        cv2.imwrite(image_path, frame.copy())
        print(upload_base64_image(image_path))

    EC_value = 0.0
    data = ""
    while Serial1.available():
        c = Serial1.read()
        c = c.decode()
        print("serial: ", c)
        dict1, data = ParsingProcess(c)
        
        if floatParser.available(c) or floatParser1.available(c):
            if "on" in floatParser.data.lower() or "on" in floatParser1.data.lower():
                Serial1.println("CMD,SVLV,0")
                time.sleep(1)
            if "off" in floatParser.data.lower() or "off" in floatParser1.data.lower():
                Serial1.println("CMD,SVLV,1")
                time.sleep(1)
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
                post2db(k, val)
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
                    print(val,high,low)
                    if not(phRunningOnce):
                        phRunningOnce = True
                        Thread2 = Thread(target=phProcess, args=(val, high, low))
                        Thread2.start()
                    

                elif k == "EC" and not(EC_Trigg) and machine_mode == "preset":
                    if val < low:
                        if not(runningOnce):
                            runningOnce = True
                            Thread1 = Thread(target=EC_process)
                            Thread1.start()

                if isinstance(command, str) and len(command) and machine_mode == "preset":
                    Serial1.println("CMD,"+command)
                    time.sleep(1)
                else:
                    for cmd in command:
                        Serial1.println("CMD,"+cmd)
                        time.sleep(1)
    if irrSch1.Event():
        irrCnt += 1
        if irrCnt == 1:
            Serial1.println("CMD,WATR,1")
        if irrCnt == 16:
            Serial1.println("CMD,WATR,0")
        if irrCnt == 30:
            irrCnt = 0
    if minSch1.Event():
        now = datetime.now().time()
        if dt_time(6, 0) <= now <= dt_time(18, 0):
            print("It is between 6 AM and 6 PM.")
            Serial1.println("CMD,LGT1,0")
            time.sleep(1)
            Serial1.println("CMD,LGT2,0")
            time.sleep(1)
            Serial1.println("CMD,LGT3,0")
            time.sleep(1)
        else:
            print("It is outside 6 AM to 6 PM.")
            Serial1.println("CMD,LGT1,1")
            time.sleep(1)
            Serial1.println("CMD,LGT2,1")
            time.sleep(1)
            Serial1.println("CMD,LGT3,1")
            time.sleep(1)
        
