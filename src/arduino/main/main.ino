/*
  Software written by
  Nis Fisker-Bødker
  nis.fisker@gmail.com
  2024 at University of Toronto

  Components used:
  Sparkfun Arduino Redboard with Qwiic
  2 x SparFun MCP9600 (for temperature measurements in liquids)
  1 x SparkFun Dual Solid State Relay (for heat control)
  1 x Sparkfun Quad Relay (for control of peristaltic pumps)
  1 x Sparkfun SerLCD

*/
#include <Wire.h>


/*
   Load temperature sensor
*/
#include <SparkFun_MCP9600.h>
MCP9600 tempSensor1;
MCP9600 tempSensor2;

/*
   Load LCD
*/

#include <SerLCD.h>
SerLCD lcd; // Initialize the library with default I2C address 0x72

void setup() {
  Serial.begin(115200);
  Wire.begin();
  Wire.setClock(100000);

  /*
     Setup LCD
  */
  lcd.begin(Wire); //Set up the LCD for I2C communication
  lcd.setBacklight(255, 255, 255); //Set backlight to bright white
  lcd.setContrast(5); //Set contrast. Lower to 0 for higher contrast.
  lcd.clear(); //Clear the display - this moves the cursor to home position as well
  lcd.print("Booting!");


  /*
     Setup temperature sensor
  */
  tempSensor1.begin(); // Uses the default address (0x60) for SparkFun Thermocouple Amplifier
  tempSensor1.begin(0x67);

  // Check if temperature sensor is connected
  if (tempSensor1.isConnected() & tempSensor2.isConnected()) {
  }
  else {
    lcd.setCursor(0, 1);
    lcd.print("Temp sensor not connected");
    Serial.println("One of the temperature sensors are not connected");
  }

  // Check if the temperature sensor add is correct
  if (tempSensor1.checkDeviceID() & tempSensor2.checkDeviceID()) {
  }
  else {
    lcd.setCursor(0, 1);
    lcd.print("Temp sensor addr. is wrong");
    Serial.println("Temp. sensor 1 addr. is wrong");
  }
}

void loop() {
  lcd.setCursor(0, 0);

  /*
     Temperature sensor readings
  */
  if (tempSensor1.available()) {
    Serial.print("Thermocouple: ");
    Serial.print(tempSensor1.getThermocoupleTemp());
    Serial.print(" °C   Ambient: ");
    Serial.print(tempSensor1.getAmbientTemp());
    Serial.print(" °C   Temperature Delta: ");
    Serial.print(tempSensor1.getTempDelta());
    Serial.print(" °C");
    Serial.println();


    lcd.print("T1:");
    lcd.print(tempSensor1.getThermocoupleTemp());
    lcd.print("°C");
  }
  if (tempSensor2.available()) {
    lcd.print("   ");
    lcd.print("T2:");
    lcd.print(tempSensor2.getThermocoupleTemp());
    lcd.print("°C");
  }
  delay(1000);
}++
