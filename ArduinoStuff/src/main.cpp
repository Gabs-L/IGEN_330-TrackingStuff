#include <Arduino.h>
#include <Servo.h>
 
Servo servoX;
Servo servoY;

const int SERVOX_PIN = 8;
const int SERVOY_PIN = 9;
const int SOLENOID_PIN = 10;
const int PUMP_PIN = 11;

const int NEUTRAL = 90;
const int focusWidth = 500; // 500
const int sprayRad = 250; // 250

const unsigned long SERIAL_TIMEOUT = 500; // ms
unsigned long lastSerialTime = 0;
unsigned long solenoidOpened;
const int pumpDelay = 200; // ms
bool solenoidOpen = false;

const float xSpeed = 0.5; // (0-1)
float yAngle = 90.0;
const float ySpeed = 0.1; // (0-0.5)
const float autoPumpPower = 0.5; // (0-1)

void setup() {
  Serial.begin(9600);
  servoX.attach(SERVOX_PIN);
  servoY.attach(SERVOY_PIN);
  pinMode(SOLENOID_PIN,OUTPUT);
  pinMode(PUMP_PIN, OUTPUT);
  servoX.write(NEUTRAL);
  servoY.write((int)yAngle);
  digitalWrite(SOLENOID_PIN, LOW);
  analogWrite(PUMP_PIN, 0);
  lastSerialTime = millis();
}

void loop() {
  if (Serial.available() > 0){
    int mode = Serial.parseInt();
    int moveX = Serial.parseInt();
    int moveY = Serial.parseInt();

    if (mode == 0){ //manual
      int solenoid = Serial.parseInt();
      int pumpIn = Serial.parseInt();
      digitalWrite(SOLENOID_PIN, solenoid ? HIGH : LOW);
      analogWrite(PUMP_PIN, map(pumpIn, 0, 5, 0, 255));
    } else{ //auto
      bool inRange = abs(moveX) < sprayRad;
      if (inRange){
        if (!solenoidOpen){
          digitalWrite(SOLENOID_PIN, HIGH);
          solenoidOpened = millis();
          solenoidOpen = true;
        }
        if (millis() - solenoidOpened >= pumpDelay){
          analogWrite(PUMP_PIN, (int)(255*autoPumpPower));
        }
      } else{ // closes both solenoid and pump at the same time
          analogWrite(PUMP_PIN, 0);
          digitalWrite(SOLENOID_PIN, LOW);
          solenoidOpen = false;
      }
    }
      
    //x axis servo (CR) constrains focus width and maps to 0 to 180 for proportionally driven movement within that range
    int speedX = map(constrain(moveX, -focusWidth, focusWidth), -focusWidth, focusWidth, 0, 180);
    speedX = NEUTRAL + (int)((speedX - NEUTRAL) * xSpeed);
    
    //y axis servo (fixed range)
    yAngle += moveY * ySpeed;
    yAngle = constrain(yAngle, 0.0, 180.0);
    servoX.write(speedX);
    servoY.write((int)yAngle);

    lastSerialTime = millis();
  }

  //return to neutral if no instruction
  if (millis() - lastSerialTime > SERIAL_TIMEOUT) {
    servoX.write(NEUTRAL);
  }
}