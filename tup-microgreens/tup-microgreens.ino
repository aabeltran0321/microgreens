#include <DHT.h>
#include "DFRobot_EC10.h"
const int relayPins1[] = {40, 42, 44, 46, 22, 24, 26, 28}; // Relay Module 1
const int relayPins2[] = {30, 32, 34, 36, 38, 48};          // Relay Module 2
const int toggleSwitchPin = 6;
const int floatSwitchPin = 23;
const int dht22Pin = 2;
const int ecSensorPin = A0;
const int phSensorPin = A1;
const int orpSensorPin = A2;
bool toggleState = HIGH;
bool toggleState2 = HIGH;

DHT dht(dht22Pin, DHT22);

unsigned long int pHavgValue;  //Store the average value of the sensor feedback
float b;
int pHbuf[10],pHtemp;

float ecvoltage,ecValue,ectemperature = 25;
DFRobot_EC10 ec;

#define VOLTAGE 5.00    //system voltage
#define OFFSET 0        //zero drift voltage
#define LED 13         //operating instructions

double orpValue;

#define ArrayLenth  40    //times of collection
#define orpPin 2          //orp meter output,connect to Arduino controller ADC pin

int orpArray[ArrayLenth];
int orpArrayIndex=0;

double avergearray(int* arr, int number){
  int i;
  int max,min;
  double avg;
  long amount=0;
  if(number<=0){
    printf("Error number for the array to avraging!/n");
    return 0;
  }
  if(number<5){   //less than 5, calculated directly statistics
    for(i=0;i<number;i++){
      amount+=arr[i];
    }
    avg = amount/number;
    return avg;
  }else{
    if(arr[0]<arr[1]){
      min = arr[0];max=arr[1];
    }
    else{
      min=arr[1];max=arr[0];
    }
    for(i=2;i<number;i++){
      if(arr[i]<min){
        amount+=min;        //arr<min
        min=arr[i];
      }else {
        if(arr[i]>max){
          amount+=max;    //arr>max
          max=arr[i];
        }else{
          amount+=arr[i]; //min<=arr<=max
        }
      }//if
    }//for
    avg = (double)amount/(number-2);
  }//if
  return avg;
}





void setup() {
  Serial.begin(9600);
  pinMode(toggleSwitchPin, INPUT_PULLUP);
  pinMode(floatSwitchPin, INPUT_PULLUP);

  for (int pin : relayPins1) {
    pinMode(pin, OUTPUT);
    digitalWrite(pin, HIGH);
  }
  for (int pin : relayPins2) {
    pinMode(pin, OUTPUT);
    digitalWrite(pin, HIGH);
  }
  dht.begin();
  Serial.println("Microgreens");
}

void loop() {
  // Check toggle switch
  read_ec_value();
  read_orp_value();
  bool newToggleState = digitalRead(toggleSwitchPin);
  bool newToggleState2 = digitalRead(floatSwitchPin);
  if (newToggleState != toggleState) {
    toggleState = newToggleState;
    Serial.print("Toggle Switch: ");
    Serial.println(toggleState ? "OFF" : "ON");
  }

  if (newToggleState2 != toggleState2) {
    toggleState2 = newToggleState2;
    Serial.print("Float Switch: ");
    Serial.println(floatSwitchPin ? "OFF" : "ON");
  }

  // Handle serial commands
  if (Serial.available()) {
    String command = Serial.readStringUntil('?');
    command.trim();
    
    if (command == "GETDATA") {
      float temperature = dht.readTemperature();
      float humidity = dht.readHumidity();
      float phValue = phLevel();


      // Temperature, Humidity, EC, PH, ORP
      Serial.print("TUPM,");
      Serial.print(temperature);
      Serial.print(",");
      Serial.print(humidity);
      Serial.print(",");
      Serial.print(ecValue);
      Serial.print(",");
      Serial.print(phValue);
      Serial.print(",");
      Serial.println(orpValue);
    } else if (command.length() == 6 && command[4] == ',') {
      
      String device = command.substring(0, 4);
      int state = command.substring(5).toInt();
      int pin = -1;
      if (device == "SVLV") pin = 40;
      else if (device == "FAN1") pin = 42;
      else if (device == "FAN2") pin = 44;
      else if (device == "FAN3") pin = 46;
      else if (device == "PPU1") pin = 22;
      else if (device == "PPU2") pin = 24;
      else if (device == "PPU3") pin = 26;
      else if (device == "PPU4") pin = 28;
      else if (device == "DEHU") pin = 48;
      else if (device == "OZON") pin = 38;
      else if (device == "WATR") pin = 36;
      else if (device == "LGT1") pin = 30;
      else if (device == "LGT2") pin = 32;
      else if (device == "LGT3") pin = 34;

      if (pin != -1) {
        digitalWrite(pin, !state);
        // Serial.print(device);
        // Serial.print(" is now ");
        // Serial.println(state ? "ON" : "OFF");
      }
    }
  }
}


float phLevel(){
  for(int i=0;i<10;i++)       //Get 10 sample value from the sensor for smooth the value
  { 
    pHbuf[i]=analogRead(phSensorPin);
    delay(10);
  }
  for(int i=0;i<9;i++)        //sort the analog from small to large
  {
    for(int j=i+1;j<10;j++)
    {
      if(pHbuf[i]>pHbuf[j])
      {
        pHtemp=pHbuf[i];
        pHbuf[i]=pHbuf[j];
        pHbuf[j]=pHtemp;
      }
    }
  }
  pHavgValue=0;
  for(int i=2;i<8;i++)                      //take the average value of 6 center sample
    pHavgValue+=pHbuf[i];
  float phValue=(float)pHavgValue*5.0/1024/6; //convert the analog into millivolt
  phValue=3.5*phValue;                      //convert the millivolt into pH value
  return (phValue);
}

void read_ec_value(){
  static unsigned long timepoint = millis();
    if(millis()-timepoint>1000U)  //time interval: 1s
    {
      timepoint = millis();
      ecvoltage = analogRead(ecSensorPin)/1024.0*5000;  // read the voltage
      // Serial.print("voltage:");
      // Serial.print(ecvoltage);
      //temperature = readTemperature();  // read your temperature sensor to execute temperature compensation
      ecValue =  ec.readEC(ecvoltage,ectemperature);  // convert voltage to EC with temperature compensation
      // Serial.print("  temperature:");
      // Serial.print(ectemperature,1);
      // Serial.print("^C  EC:");
      // Serial.print(ecValue,1);
      // Serial.println("ms/cm");
    }
    ec.calibration(ecvoltage,ectemperature);  // calibration process by Serail CMD
}

void read_orp_value(){
  static unsigned long orpTimer=millis();   //analog sampling interval
  static unsigned long printTime=millis();
  if(millis() >= orpTimer)
  {
    orpTimer=millis()+20;
    orpArray[orpArrayIndex++]=analogRead(orpPin);    //read an analog value every 20ms
    if (orpArrayIndex==ArrayLenth) {
      orpArrayIndex=0;
    }
    orpValue=((30*(double)VOLTAGE*1000)-(75*avergearray(orpArray, ArrayLenth)*VOLTAGE*1000/1024))/75-OFFSET;

    //convert the analog value to orp according the circuit
  }
  if(millis() >= printTime)   //Every 800 milliseconds, print a numerical, convert the state of the LED indicator
  {
    printTime=millis()+800;
    // Serial.print("ORP: ");
    // Serial.print((int)orpValue);
    //     Serial.println("mV");
    //     digitalWrite(LED,1-digitalRead(LED));

}
