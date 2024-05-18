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
const byte buff_size = 40;
char input_buffer[buff_size];
const char start_marker = '<';
const char end_marker = '>';
byte bytes_rcvd = 0;
boolean read_in_progress = false;
boolean new_data_pc = false;
String message_from_pc;
int direction_in = 0;
int steps_in = 0;
int step_time_in = 0;
int m_num = 0;
float ultrasound_time_in;


/*
   Load temperature sensor
*/
#include <SparkFun_MCP9600.h>
MCP9600 tempSensor0;
float sample_temperature0;
float ambient_temperature0;
MCP9600 tempSensor1;
float sample_temperature1;
float ambient_temperature1;

/*
   Load LCD
*/

#include <SerLCD.h>
SerLCD lcd; // Initialize the library with default I2C address 0x72


/*
   Load relays
*/
// Relay 0-3
#include <SparkFun_Qwiic_Relay.h>
#define RELAY_ADDR 0x6D // Alternate address 0x6C
Qwiic_Relay quadRelay(RELAY_ADDR);

// Solid state relays relay 4-5 for 110VAC
#define RELAY_SOLIDSTATE 0x0A
Qwiic_Relay solidStateRelay(RELAY_SOLIDSTATE);

// Relay 6-9
// Remember this is NOT a standard I2C add - it was coded to the quad relay.
#define RELAY_ADDR2 0x09
Qwiic_Relay quadRelay2(RELAY_ADDR2);


/*
   Load PID control
*/
#include <AutoPID.h>
#define OUTPUT_MIN 0
#define OUTPUT_MAX 255
#define KP 1
#define KI 1
#define KD 1
double temperature, setPoint, outputVal;
AutoPID myPID(&temperature, &setPoint, &outputVal, OUTPUT_MIN, OUTPUT_MAX, KP, KI, KD);
unsigned long lastTempUpdate; //tracks clock time of last temp update
int dutyCycle0 = 0; //Tracks how much the relay is on at 1Hz. 120 = 100%.
int dutyCycle1 = 0; //Tracks how much the relay is on at 1Hz. 120 = 100%.

void setup() {
  Serial.begin(115200);
  Wire.begin();
  Wire.setClock(100000);


  /*
     Setup LCD
  */
  // Serial.println("Booting LCD");
  lcd.begin(Wire); //Set up the LCD for I2C communication
  lcd.setBacklight(255, 255, 255); //Set backlight to bright white
  lcd.setContrast(5); //Set contrast. Lower to 0 for higher contrast.
  lcd.clear(); //Clear the display - this moves the cursor to home position as well
  lcd.print("Booting!");


  /*
     Setup temperature sensor 0
  */
  // Serial.println("Booting temperature sensors");
  tempSensor0.begin(0x60); // Uses the default address (0x60) for SparkFun Thermocouple Amplifier
  tempSensor1.begin(0x67);

  // Check if temperature sensor is connected
  // Serial.println("Check if temperature sensor 0 is online");
  if (!tempSensor0.isConnected()) {
    lcd.setCursor(0, 0);
    lcd.print("Temp 0 not connected");
    Serial.println("Temperature sensor 0 not connected");
    delay(10000);
  }

  // Check if the temperature sensor address is correct
  // Serial.println("Check temperature sensor 0 address");
  if (!tempSensor0.checkDeviceID()) {
    lcd.setCursor(0, 0);
    lcd.print("Temp 0 addr. is wrong");
    Serial.println("Temperature sensor 0 address is wrong");
    delay(10000);
  }

  /*
     Setup temperature sensor 1
  */
  // Check if temperature sensor 1 is connected
  // Serial.println("Check if temperature sensor 1 is online");
  if (!tempSensor1.isConnected()) {
    lcd.setCursor(0, 0);
    lcd.print("Temp 1 not connected");
    Serial.println("Temperature sensor 1 not connected");
    delay(10000);
  }

  // Check if the temperature sensor address is correct
  // Serial.println("Check temperature sensor 1 address");
  if (!tempSensor1.checkDeviceID()) {
    lcd.setCursor(0, 0);
    lcd.print("Temp 1 addr. is wrong");
    Serial.println("Temperature sensor 1 address is wrong");
    delay(10000);
  }


  /*
     Setup relays
  */
  if (!quadRelay.begin()) {
    lcd.setCursor(0, 0);
    lcd.print("Quad relay not connected");
    Serial.println("Check connections to Qwiic Relay.");
  }
  if (!solidStateRelay.begin()) {
    lcd.setCursor(0, 0);
    lcd.print("SolStateRelay not connected");
    Serial.println("Check connections to solid state relay.");
  }
  if (!quadRelay2.begin()) {
    lcd.setCursor(0, 0);
    lcd.print("Quad relay not connected");
    Serial.println("Check connections to Qwiic Relay.");
  }

  /*
     Setup PID control
  */
  setPoint = 25;
  // if temperature is more than 4 degrees below or above setpoint, OUTPUT will be set to min or max respectively
  myPID.setBangBang(10);
  //set PID update interval to 2900ms
  myPID.setTimeStep(2900);
}

void loop() {
  // Updating the sensor values
  delay(500);
  sample_temperature0 = read_sample_temperature(0);
  delay(500);
  ambient_temperature0 = read_ambient_temperature(0);
  delay(500);
  sample_temperature1 = read_sample_temperature(1);
  delay(500);
  ambient_temperature1 = read_ambient_temperature(1);
  delay(500);

  // Update PID controller 0
  temperature = sample_temperature0;
  myPID.run();
  if (outputVal > 0)
  {
    dutyCycle0 = (outputVal / 255) * 120;
  }
  else
  {
    dutyCycle0 = 0;
  }
  solidStateRelay.setSlowPWM(1, dutyCycle0);
  //  Serial.print("OutputVal: ");
  //  Serial.print(outputVal);
  //  Serial.print(", Dutycycle: ");
  //  Serial.print(dutyCycle0);
  //  Serial.print(", P: ");
  //  Serial.print(KP);
  //  Serial.print(", I: ");
  //  Serial.print(KI);
  //  Serial.print(", D: ");
  //  Serial.println(KD);

  // Write the sensor values to the LCD
  write_to_lcd(sample_temperature0, sample_temperature1, dutyCycle0);

  // Check if there is instructions from the PC
  get_data_from_pc();
}

void get_data_from_pc()
{

  // receive data from PC and save it into input_buffer
  while (Serial.available())
  {
    char x = Serial.read();

    // the order of these IF clauses is significant

    if (x == end_marker)
    {
      read_in_progress = false;
      new_data_pc = true;
      input_buffer[bytes_rcvd] = 0;
      parse_data();
    }

    if (read_in_progress)
    {
      input_buffer[bytes_rcvd] = x;
      bytes_rcvd++;
      if (bytes_rcvd == buff_size)
      {
        bytes_rcvd = buff_size - 1;
      }
    }

    if (x == start_marker)
    {
      bytes_rcvd = 0;
      read_in_progress = true;
    }
  }
}

void parse_data()
{
  // split the data into its parts
  char *str_to_ind; // this is used by strtok() as an index

  str_to_ind = strtok(input_buffer, ","); // get the first part - the string
  message_from_pc = String(str_to_ind);

  if (message_from_pc == "set_relay_on_time")
  {
    str_to_ind = strtok(NULL, ","); // this continues where the previous call left off
    int relay_num = atoi(str_to_ind);       // convert this part to an integer

    str_to_ind = strtok(NULL, ",");
    int time_ms = atoi(str_to_ind);

    if (0 <= relay_num && relay_num <= 3)
    {
      quadRelay.turnRelayOn(relay_num);
      delay(time_ms);
      quadRelay.turnRelayOff(relay_num);
    }
    if (4 <= relay_num && relay_num <= 5)
    {
      if (relay_num == 4)
      {
        relay_num = 1;
      }
      if (relay_num == 5)
      {
        relay_num = 2;
      }
      solidStateRelay.turnRelayOn(relay_num);
      delay(time_ms);
      solidStateRelay.turnRelayOff(relay_num);
    }
    if (6 <= relay_num && relay_num <= 9)
    {
      quadRelay2.turnRelayOn(relay_num);
      delay(time_ms);
      quadRelay2.turnRelayOff(relay_num);
    }
    Serial.println("#"); // '#' indicates process is done
  }


  if (message_from_pc == "read_temp0")
  {
    Serial.println(sample_temperature0);
  }
  if (message_from_pc == "read_temp1")
  {
    Serial.println(sample_temperature1);
  }
  if (message_from_pc == "read_temp0_ambient")
  {
    Serial.println(ambient_temperature0);
  }
  if (message_from_pc == "read_temp1_ambient")
  {
    Serial.println(ambient_temperature1);
  }
  if (message_from_pc == "setpoint")
  {
    str_to_ind = strtok(NULL, ","); // this continues where the previous call left off
    double setPoint = atoi(str_to_ind);
  }
  //  if (message_from_pc == "set_relay_0_on")
  //  {
  //    quadRelay.turnRelayOn(1);
  //    Serial.println("#"); // '#' indicates process is done
  //  }
  //  if (message_from_pc == "set_relay_0_off")
  //  {
  //    quadRelay.turnRelayOff(1);
  //    Serial.println("#"); // '#' indicates process is done
  //  }
  //  if (message_from_pc == "set_relay_1_on")
  //  {
  //    quadRelay.turnRelayOn(2);
  //    Serial.println("#"); // '#' indicates process is done
  //  }
  //  if (message_from_pc == "set_relay_1_off")
  //  {
  //    quadRelay.turnRelayOff(2);
  //    Serial.println("#"); // '#' indicates process is done
  //  }
  //  if (message_from_pc == "set_relay_2_on")
  //  {
  //    quadRelay.turnRelayOn(3);
  //    Serial.println("#"); // '#' indicates process is done
  //  }
  //  if (message_from_pc == "set_relay_2_off")
  //  {
  //    quadRelay.turnRelayOff(3);
  //    Serial.println("#"); // '#' indicates process is done
  //  }
  //  if (message_from_pc == "set_relay_3_on")
  //  {
  //    quadRelay.turnRelayOn(4);
  //    Serial.println("#"); // '#' indicates process is done
  //  }
  //  if (message_from_pc == "set_relay_3_off")
  //  {
  //    quadRelay.turnRelayOff(4);
  //    Serial.println("#"); // '#' indicates process is done
  //  }
  //  if (message_from_pc == "set_relay_4_on")
  //  {
  //    solidStateRelay.turnRelayOn(1);
  //    Serial.println("#"); // '#' indicates process is done
  //  }
  //  if (message_from_pc == "set_relay_4_off")
  //  {
  //    solidStateRelay.turnRelayOff(1);
  //    Serial.println("#"); // '#' indicates process is done
  //  }
  //  if (message_from_pc == "set_relay_5_on")
  //  {
  //    solidStateRelay.turnRelayOn(2);
  //    Serial.println("#"); // '#' indicates process is done
  //  }
  //  if (message_from_pc == "set_relay_5_off")
  //  {
  //    solidStateRelay.turnRelayOff(2);
  //    Serial.println("#"); // '#' indicates process is done
  //  }
  if (message_from_pc == "get_relay_0_state")
  {
    int state = quadRelay.getState(1);
    Serial.println(state); // 0 = off, 1 = on
  }
  if (message_from_pc == "get_relay_1_state")
  {
    int state = quadRelay.getState(2);
    Serial.println(state); // 0 = off, 1 = on
  }
  if (message_from_pc == "get_relay_2_state")
  {
    int state = quadRelay.getState(3);
    Serial.println(state); // 0 = off, 1 = on
  }
  if (message_from_pc == "get_relay_3_state")
  {
    int state = quadRelay.getState(4);
    Serial.println(state); // 0 = off, 1 = on
  }
  if (message_from_pc == "get_relay_4_state")
  {
    int state = solidStateRelay.getState(1);
    Serial.println(state); // 0 = off, 1 = on
  }
  if (message_from_pc == "get_relay_5_state")
  {
    int state = solidStateRelay.getState(2);
    Serial.println(state); // 0 = off, 1 = on
  }
  if (message_from_pc == "get_relay_6_state")
  {
    int state = quadRelay2.getState(1);
    Serial.println(state); // 0 = off, 1 = on
  }
  if (message_from_pc == "get_relay_7_state")
  {
    int state = quadRelay2.getState(2);
    Serial.println(state); // 0 = off, 1 = on
  }
  if (message_from_pc == "get_relay_8_state")
  {
    int state = quadRelay2.getState(3);
    Serial.println(state); // 0 = off, 1 = on
  }
  if (message_from_pc == "get_relay_9_state")
  {
    int state = quadRelay2.getState(4);
    Serial.println(state); // 0 = off, 1 = on
  }

  else
  {
    Serial.println("Unknown command: " + message_from_pc);
  }

}

void ultrasound(float ultrasound_time)
{
  // flip relay on
  delay(ultrasound_time);
  // Flip relay off
  Serial.println("#"); // '#' indicates process is done
}

void drain(float drain_time)
{
  // Do something
  Serial.println("#"); // '#' indicates process is done
}

void transfer_liquid(float drain_time)
{
  // Do something
  Serial.println("#"); // '#' indicates process is done
}

float read_sample_temperature(int sensor)
{
  // There are two sensors on this system.
  // Read each of them dependen on the input
  float sample_temp = 999.99;
  if (sensor == 0) {
    if (tempSensor0.available()) {
      sample_temp = tempSensor0.getThermocoupleTemp();
    }
  }
  if (sensor == 1) {
    if (tempSensor1.available()) {
      sample_temp = tempSensor1.getThermocoupleTemp();
    }
  }

  return sample_temp;
}

float read_ambient_temperature(int sensor)
{
  // There are two sensors on this system.
  // Read each of them dependen on the input
  float ambient_temp = 999.99;
  if (sensor == 0) {
    if (tempSensor0.available()) {
      ambient_temp = tempSensor0.getAmbientTemp();
    }
  }
  if (sensor == 1) {
    if (tempSensor1.available()) {
      ambient_temp = tempSensor1.getAmbientTemp();
    }
  }

  return ambient_temp;
}

void write_to_lcd(float sample_temp0, float sample_temp1, double PIDoutput)
{
  lcd.setCursor(0, 0);
  lcd.print("0:");
  lcd.print(sample_temp0);
  lcd.print(" ");
  lcd.setCursor(9, 0);
  lcd.print("1:");
  lcd.print(sample_temp1);
  lcd.setCursor(0, 1);
  lcd.print("P1:");
  lcd.print(round(PIDoutput));
}
