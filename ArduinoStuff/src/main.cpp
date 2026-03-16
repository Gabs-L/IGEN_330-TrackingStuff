#include <Arduino.h>
#include <Servo.h>
 
Servo servoX;
Servo servoY;

const int SERVOX_PIN = 8;
const int SERVOY_PIN = 9;
const int NEUTRAL = 90;
const int focusWidth = 200;
const float speed = 0.1; //the "P" in "PID"
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

    //constrains focus width and maps to 0 to 180 for proportionally driven movement within that range
    int speedX = map(constrain(moveX, -focusWidth, focusWidth), -focusWidth, focusWidth, 0, 180);
    int speedY = map(constrain(moveY, -focusWidth, focusWidth), -focusWidth, focusWidth, 0, 180);
    
    servoX.write(speedX);
    servoY.write(speedY);

    lastSerialTime = millis();
  }

  //return to neutral if no instruction
  if (millis() - lastSerialTime > SERIAL_TIMEOUT) {
    servoX.write(NEUTRAL);
    servoY.write(NEUTRAL);
  }
}