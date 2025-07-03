#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <DHT.h>
#include "DFRobot_EC10.h"

// LCD I2C setup
LiquidCrystal_I2C lcd(0x27, 20, 4); // Change to 0x3F if your LCD has a different address

const int relayPins1[] = {40, 42, 44, 46, 22, 24, 26, 28}; // Relay Module 1
const int relayPins2[] = {30, 32, 34, 36, 38, 48, 50};     // Relay Module 2

const int toggleSwitchPin = 6;
const int floatSwitchPin = 23;
const int dht22Pin = 2;
const int ecSensorPin = A0;
const int phSensorPin = A1;
const int orpSensorPin = A2;

bool toggleState = HIGH;
bool toggleState2 = HIGH;

DHT dht(dht22Pin, DHT22);
DFRobot_EC10 ec;

unsigned long int pHavgValue;
float b;
int pHbuf[10], pHtemp;

float ecvoltage, ecValue, ectemperature = 25;

#define VOLTAGE 5.00
#define OFFSET 0
#define LED 13

double orpValue;
#define ArrayLenth  40
#define orpPin A2

int orpArray[ArrayLenth];
int orpArrayIndex = 0;

unsigned long lastLCDUpdate = 0;

double avergearray(int* arr, int number) {
  int i, max, min;
  double avg;
  long amount = 0;
  if (number <= 0) return 0;
  if (number < 5) {
    for (i = 0; i < number; i++) amount += arr[i];
    return (double)amount / number;
  } else {
    if (arr[0] < arr[1]) { min = arr[0]; max = arr[1]; }
    else { min = arr[1]; max = arr[0]; }

    for (i = 2; i < number; i++) {
      if (arr[i] < min) {
        amount += min;
        min = arr[i];
      } else if (arr[i] > max) {
        amount += max;
        max = arr[i];
      } else {
        amount += arr[i];
      }
    }
    avg = (double)amount / (number - 2);
    return avg;
  }
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
  ec.begin();

  lcd.begin();
  lcd.backlight();
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Microgreens Ready");
  delay(2000);
  lcd.clear();

  Serial.println("Microgreens");
}

void loop() {
  

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
    Serial.println(toggleState2 ? "OFF" : "ON");
  }

  if (Serial.available()) {
    String command = Serial.readStringUntil('?');
    command.trim();

    if (command == "GETDATA") {
      read_ec_value();
      read_orp_value();
      float temperature = dht.readTemperature();
      float humidity = dht.readHumidity();
      float phValue = phLevel();

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
      else if (device == "LGT4") pin = 50;

      if (pin != -1) {
        Serial.print(device);
        Serial.print(",");
        Serial.println(state);
        digitalWrite(pin, !state);
      }
    }
  }

  // Update LCD every 1 second
  if (millis() - lastLCDUpdate > 1000) {
    lastLCDUpdate = millis();

    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();
    float phValue = phLevel();

    lcd.setCursor(0, 0);
    lcd.print("T:");
    lcd.print(temperature, 1);
    lcd.print((char)223); // degree symbol
    lcd.print("C H:");
    lcd.print(humidity, 0);
    lcd.print("%   ");

    lcd.setCursor(0, 1);
    lcd.print("EC:");
    lcd.print(ecValue, 2);
    lcd.print(" PH:");
    lcd.print(phValue, 2);
    lcd.print("   ");

    lcd.setCursor(0, 2);
    lcd.print("ORP:");
    lcd.print(orpValue, 0);
    lcd.print("mV        ");

    lcd.setCursor(0, 3);
    lcd.print("Toggle:");
    lcd.print(toggleState ? "OFF" : "ON ");
    lcd.print(" Float:");
    lcd.print(toggleState2 ? "OFF" : "ON ");
  }
}

float phLevel() {
  for (int i = 0; i < 10; i++) {
    pHbuf[i] = analogRead(phSensorPin);
    delay(10);
  }

  for (int i = 0; i < 9; i++) {
    for (int j = i + 1; j < 10; j++) {
      if (pHbuf[i] > pHbuf[j]) {
        pHtemp = pHbuf[i];
        pHbuf[i] = pHbuf[j];
        pHbuf[j] = pHtemp;
      }
    }
  }

  pHavgValue = 0;
  for (int i = 2; i < 8; i++) pHavgValue += pHbuf[i];

  float phValue = (float)pHavgValue * 5.0 / 1024 / 6;
  phValue = 3.5 * phValue;
  return phValue;
}

void read_ec_value() {
  /*static unsigned long timepoint = millis();
  if (millis() - timepoint > 1000U) {
    timepoint = millis();
    ecvoltage = analogRead(ecSensorPin) / 1024.0 * 5000;
    ecValue = ec.readEC(ecvoltage, ectemperature);
    ec.calibration(ecvoltage, ectemperature);
  }*/
  ecvoltage = analogRead(ecSensorPin) / 1024.0 * 5000;
  ecValue = ec.readEC(ecvoltage, ectemperature);
  ec.calibration(ecvoltage, ectemperature);
  
}

void read_orp_value() {
  static unsigned long orpTimer = millis();
  if (millis() >= orpTimer) {
    orpTimer = millis() + 20;
    orpArray[orpArrayIndex++] = analogRead(orpPin);
    if (orpArrayIndex == ArrayLenth) {
      orpArrayIndex = 0;
    }
    orpValue = ((30 * VOLTAGE * 1000) - (75 * avergearray(orpArray, ArrayLenth) * VOLTAGE * 1000 / 1024)) / 75 - OFFSET;
  }
}
