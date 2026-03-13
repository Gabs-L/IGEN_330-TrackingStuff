#include <Arduino.h>
#include <Servo.h>
 
Servo servo;

const int SERVOX_PIN = 9;
const int SERVOY_PIN = 10;
const int NEUTRAL = 90;
const unsigned long SERIAL_TIMEOUT = 500; // ms

unsigned long lastSerialTime = 0;

void setup() {
  Serial.begin(9600);
  servo.attach(SERVOX_PIN);
  servo.write(NEUTRAL);  // safe startup position
  lastSerialTime = millis();

  Serial.println("Arduino ready. Send 0–180.");
}

void loop() {

  // Check for incoming serial data
  if (Serial.available() > 0) {
    int value = Serial.parseInt();   // expects 0–180

    if (value >= 0 && value <= 180) {
      servo.write(value);
      lastSerialTime = millis();   // reset watchdog

      Serial.print("Input value: ");
      Serial.println(value);
    }
  }

  // WATCHDOG: stop if serial goes silent
  if (millis() - lastSerialTime > SERIAL_TIMEOUT) {
    servo.write(SAFE_POS);   // stop / center
  }
}