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
   Load relays
*/
// Relay 0-3
#include <SparkFun_Qwiic_Relay.h>
#define RELAY_ADDR 0x6D // Alternate address 0x6C
Qwiic_Relay quadRelay(RELAY_ADDR);

// Solid state relays for 110VAC
#define RELAY_SOLIDSTATE 0x0A
Qwiic_Relay solidStateRelay(RELAY_SOLIDSTATE);

// Relay 4-7
// Remember this is NOT a standard I2C add - it was coded to the quad relay.
#define RELAY_ADDR2 0x6C // 0x09
Qwiic_Relay quadRelay2(RELAY_ADDR2);


void setup() {
  Serial.begin(115200);
  Wire.begin();
  Wire.setClock(100000);

  /*
     Setup relays
  */
  if (!quadRelay.begin()) {
    Serial.println("Check connections to Qwiic Relay1.");
  }
  if (!solidStateRelay.begin()) {
    Serial.println("Check connections to solid state relay.");
  }
  if (!quadRelay2.begin()) {
    Serial.println("Check connections to Qwiic Relay2.");
  }

}

void loop() {
  // Updating the sensor values
  delay(2000);

  quadRelay.turnRelayOn(1);
  delay(2000);
  quadRelay.turnRelayOff(1);
  quadRelay.turnRelayOn(2);
  delay(2000);
  quadRelay.turnRelayOff(2);
  quadRelay.turnRelayOn(3);
  delay(2000);
  quadRelay.turnRelayOff(3);
  quadRelay.turnRelayOn(4);
  delay(2000);
  quadRelay.turnRelayOff(4);
//
//  quadRelay2.turnRelayOn(1);
//  delay(2000);
//  quadRelay2.turnRelayOff(1);
//  quadRelay2.turnRelayOn(2);
//  delay(2000);
//  quadRelay2.turnRelayOff(2);
//  quadRelay2.turnRelayOn(3);
//  delay(2000);
//  quadRelay2.turnRelayOff(3);
//  quadRelay2.turnRelayOn(4);
//  delay(2000);
//  quadRelay2.turnRelayOff(4);


}
