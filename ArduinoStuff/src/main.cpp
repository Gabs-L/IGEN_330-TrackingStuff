#include <Arduino.h>
#include <Servo.h>
 
Servo servoX;
Servo servoY;

const int SERVOX_PIN = 8;
const int SERVOY_PIN = 9;
const int CW = 180;
const int NEUTRAL = 90;
const int CCW = 0;
const unsigned long SERIAL_TIMEOUT = 500; // ms
unsigned long lastSerialTime = 0;

void setup() {
  Serial.begin(9600);
  servoX.attach(SERVOX_PIN);
  servoY.attach(SERVOY_PIN);
  servoX.write(NEUTRAL);
  servoY.write(NEUTRAL);
  lastSerialTime = millis();
}

void loop() {
  if (Serial.available() > 0){
    int moveX = Serial.parseInt();
    int moveY = Serial.parseInt();

    //move x dir
    if (moveX > 0)       servoX.write(CW);
    else if (moveX < 0)  servoX.write(CCW);
    else                 servoX.write(NEUTRAL);
    
    //move y dir
    if (moveY > 0)       servoY.write(CW);
    else if (moveY < 0)  servoY.write(CCW);
    else   

    lastSerialTime = millis();
  }

  //return to neutral if no instruction
  if (millis() - lastSerialTime > SERIAL_TIMEOUT) {
    servoX.write(NEUTRAL);
    servoY.write(NEUTRAL);
  }
}