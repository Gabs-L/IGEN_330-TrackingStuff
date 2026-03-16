#include <Arduino.h>
#include <Servo.h>

Servo servoX;
const int SERVOX_PIN = 8;
const int NEUTRAL = 90;
const int CW = 0;
const int CCW = 180;

const unsigned long SERIAL_TIMEOUT = 500;
unsigned long lastSerialTime = 0;

void setup() {
  Serial.begin(9600);
  servoX.attach(SERVOX_PIN);
  servoX.write(NEUTRAL);
  lastSerialTime = millis();
}

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();

    if (cmd == 'D' || cmd == 'd') {
      servoX.write(CW);
      Serial.println("Moving CW");
      lastSerialTime = millis();
    } else if (cmd == 'A' || cmd == 'a') {
      servoX.write(CCW);
      Serial.println("Moving CCW");
      lastSerialTime = millis();
    } else if (cmd == 'S' || cmd == 's') {
      servoX.write(NEUTRAL);
      Serial.println("NEUTRAL");
      lastSerialTime = millis();
    }
  }

  if (millis() - lastSerialTime > SERIAL_TIMEOUT) {
    servoX.write(NEUTRAL);
  }
}