void checkSerial()
{
  int ctr = 0;
  while (1) {
    if (Serial3.available()) {
      char rxByte = Serial3.read();
      if (rxByte == 'P') {
        phLUp = Serial3.parseFloat();   phLDwn = Serial3.parseFloat();
        orpUp = Serial3.parseFloat();   orpDwn = Serial3.parseFloat();
        tempUp = Serial3.parseFloat();  tempDwn = Serial3.parseFloat();
        humidUp = Serial3.parseFloat(); humidDwn = Serial3.parseFloat();
        ecUp = Serial3.parseFloat();   ecDwn = Serial3.parseFloat();

//        phLUp = Serial.parseFloat();   phLDwn = Serial.parseFloat();
//        orpUp = Serial.parseFloat();   orpDwn = Serial.parseFloat();
//        tempUp = Serial.parseFloat();  tempDwn = Serial.parseFloat();
//        humidUp = Serial.parseFloat(); humidDwn = Serial.parseFloat();
//        ecUp = Serial.parseFloat();   ecDwn = Serial.parseFloat();

        Serial.print(phLUp); Serial.print(" "); Serial.println(phLDwn);
        Serial.print(orpUp); Serial.print(" "); Serial.println(orpDwn);
        Serial.print(tempUp); Serial.print(" "); Serial.println(tempDwn);
        Serial.print(humidUp); Serial.print(" "); Serial.println(humidDwn);
        Serial.print(ecUp); Serial.print(" "); Serial.println(ecDwn);
        break;
      }
    }
    ctr++;delay(1);
    if(ctr > 3000){
      break;
    }
  }
end_here: {}
}
void readADC()
{
  int times = 100;
  tAdcORP = 0; tAdcPH = 0; tAdcEC = 0;
  for (int x = 1; x <= times; x++)
  {
    adcPH = analogRead(A0); tAdcPH += adcPH; delayMicroseconds(50);
    adcEC = analogRead(A2); tAdcEC += adcEC; delayMicroseconds(50);
    //    adcORP = analogRead(A1); tAdcORP += adcORP; delayMicroseconds(50);
  }
  adcEC = tAdcEC / times;
  adcPH = tAdcPH / times;
  //  adcORP = tAdcORP / times;
}
void getSensor()
{
  readADC();
  readORP();
  phInt = map(adcPH, 245, 428, 918, 400);
  ph = float(phInt) / 100;
  //  orp = float(adcORP) / 1022.0 * 5000;

  humid = dht.readHumidity();
  temp = dht.readTemperature();
  readEc();
  //   Serial.print(adcPH);Serial.print("  ");  Serial.println(phInt);
  //  Serial.print(adcORP); Serial.print("  ");  Serial.println(orp, 1);
}
void readORP()
{
  while (1) {
    orpArray[orpArrayIndex++] = analogRead(orpPin);
    if (orpArrayIndex == ArrayLenth)
    {
      orpArrayIndex = 0; break;
    }
    delay(5);
  }
  orp = ((30 * (double)VOLTAGE * 1000) - (75 * avergearray(orpArray, ArrayLenth) * VOLTAGE * 1000 / 1024)) / 75 - OFFSET;
}
double avergearray(int* arr, int number)
{
  int i; int max, min;
  double avg; long amount = 0;
  if (number <= 0) {
    printf("Error number for the array to avraging!/n");
    return 0;
  }
  if (number < 5) { //less than 5, calculated directly statistics
    for (i = 0; i < number; i++) {
      amount += arr[i];
    }
    avg = amount / number;
    return avg;
  }
  else {
    if (arr[0] < arr[1]) {
      min = arr[0]; max = arr[1];
    }
    else {
      min = arr[1]; max = arr[0];
    }
    for (i = 2; i < number; i++) {
      if (arr[i] < min) {
        amount += min; min = arr[i]; //arr<min
      }
      else {
        if (arr[i] > max) {
          amount += max; max = arr[i]; //arr>max
        } else {
          amount += arr[i]; //min<=arr<=max
        }
      }
    }
    avg = (double)amount / (number - 2);
  }
  return avg;
}
void readEc()
{
  volt = float(adcEC) / 1024.0 * 5000; // read the voltage
  //  Serial.print("voltage:"); Serial.print(volt);
  float temperature = 25.0;  // read your temperature sensor to execute temperature compensation
  ecVal =  ec.readEC(volt, temperature); // convert voltage to EC with temperature compensation
  ecVal = ecVal / 9.1;
  Serial.print("  temp:");  Serial.print(temp, 1);
  Serial.print("^C  EC:"); Serial.print(ecVal, 1);  Serial.print("ms/cm");
  Serial.print("  Humid:");  Serial.print(humid, 1);
  Serial.print("  PH:");  Serial.print(ph, 1);
  Serial.print("  Orp:");  Serial.println(orp, 1);

  ec.calibration(volt, temp); // calibration process by Serail CMD
}
