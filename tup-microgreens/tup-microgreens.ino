#include <DHT.h>

const int relayPins1[] = {40, 42, 44, 46, 22, 24, 26, 28}; // Relay Module 1
const int relayPins2[] = {30, 32, 34, 36, 38, 48};          // Relay Module 2
const int toggleSwitchPin = 6;
const int dht22Pin = 2;
const int ecSensorPin = A0;
const int phSensorPin = A1;
const int orpSensorPin = A2;
bool toggleState = HIGH;

DHT dht(dht22Pin, DHT22);

void setup() {
  Serial.begin(9600);
  pinMode(toggleSwitchPin, INPUT_PULLUP);

  for (int pin : relayPins1) {
    pinMode(pin, OUTPUT);
    digitalWrite(pin, LOW);
  }
  for (int pin : relayPins2) {
    pinMode(pin, OUTPUT);
    digitalWrite(pin, LOW);
  }
  dht.begin();
  Serial.println("Microgreens");
}

void loop() {
  // Check toggle switch
  bool newToggleState = digitalRead(toggleSwitchPin);
  if (newToggleState != toggleState) {
    toggleState = newToggleState;
    Serial.print("Toggle Switch: ");
    Serial.println(toggleState ? "OFF" : "ON");
  }

  // Handle serial commands
  if (Serial.available()) {
    String command = Serial.readStringUntil('?');
    command.trim();
    
    if (command == "GETDATA") {
      float temperature = dht.readTemperature();
      float humidity = dht.readHumidity();
      int ecValue = analogRead(ecSensorPin);
      int phValue = analogRead(phSensorPin);
      int orpValue = analogRead(orpSensorPin);

      Serial.print("Temperature: "); Serial.println(temperature);
      Serial.print("Humidity: "); Serial.println(humidity);
      Serial.print("EC: "); Serial.println(ecValue);
      Serial.print("PH: "); Serial.println(phValue);
      Serial.print("ORP: "); Serial.println(orpValue);
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
      else if (device == "DEHU") pin = 30;
      else if (device == "OZON") pin = 32;
      else if (device == "WATR") pin = 34;
      else if (device == "LGT1") pin = 36;
      else if (device == "LGT2") pin = 38;
      else if (device == "LGT3") pin = 48;

      if (pin != -1) {
        digitalWrite(pin, !state);
        Serial.print(device);
        Serial.print(" is now ");
        Serial.println(state ? "ON" : "OFF");
      }
    }
  }
}
