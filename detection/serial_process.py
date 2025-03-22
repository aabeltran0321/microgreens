import serial
import time
from datetime import datetime

# Initialize serial connection (adjust port as needed)
ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)
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

light_sch1 = Scheduler(1000)
# Define thresholds
thresholds = {
    "Temperature": (20, 30),
    "Humidity": (50, 70),
    "EC": (1.2, 2.4),
    "PH": (6.0, 7.5),
    "ORP": (200, 400)
}

def check_threshold(parameter, value):
    min_val, max_val = thresholds[parameter]
    if value < min_val:
        print(f"{parameter} LOW: {value} (Threshold: {min_val}-{max_val})")
    elif value > max_val:
        print(f"{parameter} HIGH: {value} (Threshold: {min_val}-{max_val})")
    else:
        print(f"{parameter} OPTIMUM: {value} (Threshold: {min_val}-{max_val})")

def control_solenoid(command):
    if command == "ON":
        print("Turning solenoid ON")
        ser.write(b'SVLV,1?')  # Send 'O' to turn ON
    elif command == "OFF":
        print("Turning solenoid OFF")
        ser.write(b'SVLV,1?')  # Send 'o' to turn OFF

def control_lights():
    """Control lights between 6 PM and 6 AM."""
    current_hour = datetime.now().hour
    if 18 <= current_hour or current_hour < 6:
        print("Lights ON")
        ser.write(b'LGT1,1?')  #  turn lights ON
        ser.write(b'LGT2,1?')  #  turn lights ON
        ser.write(b'LGT3,1?')  #  turn lights ON
    else:
        print("Lights OFF")
        ser.write(b'LGT1,0?')  #  turn lights OFF
        ser.write(b'LGT2,0?')  #  turn lights OFF
        ser.write(b'LGT3,0?')  #  turn lights OFF
try:
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            if "Float Switch:" in line:
                state = line.split()[-1]
                control_solenoid(state)

            elif "Temperature:" in line:
                temperature = float(line.split()[-1])
                check_threshold("Temperature", temperature)
            elif "Humidity:" in line:
                humidity = float(line.split()[-1])
                check_threshold("Humidity", humidity)
            elif "EC:" in line:
                ec_value = float(line.split()[-1])
                check_threshold("EC", ec_value)
            elif "PH:" in line:
                ph_value = float(line.split()[-1])
                check_threshold("PH", ph_value)
            elif "ORP:" in line:
                orp_value = float(line.split()[-1])
                check_threshold("ORP", orp_value)
        if light_sch1.Event():
            control_lights()
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Exiting...")
    ser.close()
