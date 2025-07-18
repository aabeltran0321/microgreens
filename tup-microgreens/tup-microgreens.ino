#include "Parser.h"
Parser commandParse("CMD,",'\r',1);

#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include "DHT.h"
#define DHTPIN 2     // what digital pin we're connected to
// Uncomment whatever type you're using!
//#define DHTTYPE DHT11   // DHT 11
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

#include "DFRobot_EC10.h"
#include <EEPROM.h>
DFRobot_EC10 ec;

float temp, ph, orp, humid, ecVal, volt;
float tempUp, tempDwn, phLUp, phLDwn, orpUp, orpDwn, humidUp, humidDwn, ecUp, ecDwn;
int adcPH, adcORP, adcEC;
unsigned long tAdcORP, tAdcPH, tAdcEC;
int phInt, pumpFl, idx;
char sBuff[25] = "";
String dates, times;
int hrs, mn, sc;
char bRec[100], dummy = 0;
char *p, *n;



// LCD I2C setup
LiquidCrystal_I2C lcd(0x27, 20, 4); // Change to 0x3F if your LCD has a different address

const int relayPins1[] = {40, 42, 44, 46, 22, 24, 26, 28}; // Relay Module 1
const int relayPins2[] = {30, 32, 34, 36, 38, 48, 50};     // Relay Module 2

const int toggleSwitchPin = 6;
const int floatSwitchPin = 23;

bool toggleState = HIGH;
bool toggleState2 = HIGH;

unsigned long lastLCDUpdate = 0;

#define orpPin      A1    //orp meter output,connect to Arduino controller ADC pin
#define VOLTAGE     5.00  //system voltage
#define OFFSET      0     //zero drift voltage
#define ArrayLenth  40    //times of collection

double orpValue;
int orpArray[ArrayLenth];
int orpArrayIndex = 0;

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

  lcd.init();
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
    char srx = Serial.read()

    if(commandParse.DataReceived(srx)){
      String command =  commandParse.data;
      if (command == "GETDATA") {
        Serial.print("TUPM,");
        Serial.print(temp);
        Serial.print(",");
        Serial.print(humid);
        Serial.print(",");
        Serial.print(ecVal);
        Serial.print(",");
        Serial.print(ph);
        Serial.print(",");
        Serial.println(orp);
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

    
  }

  // Update LCD every 1 second
  if (millis() - lastLCDUpdate > 1000) {
    lastLCDUpdate = millis();

    getSensor();

    lcd.setCursor(0, 0);
    lcd.print("T:");
    lcd.print(temp, 1);
    lcd.print((char)223); // degree symbol
    lcd.print("C H:");
    lcd.print(humid, 0);
    lcd.print("%   ");

    lcd.setCursor(0, 1);
    lcd.print("EC:");
    lcd.print(ecVal, 2);
    lcd.print(" PH:");
    lcd.print(ph, 2);
    lcd.print("   ");

    lcd.setCursor(0, 2);
    lcd.print("ORP:");
    lcd.print(orp, 0);
    lcd.print("mV        ");

    lcd.setCursor(0, 3);
    lcd.print("Toggle:");
    lcd.print(toggleState ? "OFF" : "ON ");
    lcd.print(" Float:");
    lcd.print(toggleState2 ? "OFF" : "ON ");
  }
}
