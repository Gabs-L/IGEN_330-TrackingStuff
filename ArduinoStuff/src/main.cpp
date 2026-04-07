#include <Arduino.h>
#include <Servo.h>
 
Servo servoX;
Servo servoY;

const int SERVOX_PIN = 8;
const int SERVOY_PIN = 9;
const int SOLENOID_PIN = 10;
const int PUMP_PIN = 3;

const int NEUTRAL = 90;
const int focusWidth = 500; // 500
const int sprayRad = 250; // 250

const unsigned long SERIAL_TIMEOUT = 2000; // ms
unsigned long lastSerialTime = 0;
unsigned long solenoidOpened;
const int pumpDelay = 100; // ms
bool solenoidOpen = false;

const float xSpeed = 0.5; // (0-1)
float yAngle = 90.0;
const float ySpeed = 0.1; // (0-0.5)
const float autoPumpPower = 0.5; // (0-1)

void setup() {
  Serial.begin(9600);
  Serial.setTimeout(50); //may need to increase

  pinMode(LED_BUILTIN, OUTPUT);

  servoX.attach(SERVOX_PIN);
  servoY.attach(SERVOY_PIN);
  pinMode(SOLENOID_PIN,OUTPUT);
  pinMode(PUMP_PIN, OUTPUT);

  servoX.write(NEUTRAL);
  servoY.write((int)yAngle);
  digitalWrite(SOLENOID_PIN, LOW);
  analogWrite(PUMP_PIN, 0);
  // TCCR2B = (TCCR2B & 0xF8) | 0x01; //Sets uber high freq to pins 3 and 11
  lastSerialTime = millis();
}

void loop() {
  if (Serial.available() > 0){
    char buffer[64];
    int len = Serial.readBytesUntil('\n', buffer, sizeof(buffer)-1);
    buffer[len] = '\0';
    int mode, moveX, moveY, solenoid, pumpIn;
    int found  = sscanf(buffer, "%d,%d,%d,%d,%d", &mode, &moveX, &moveY, &solenoid, &pumpIn);
    if (found == 5) {
      lastSerialTime = millis();
      if (mode == 0) { // MANUAL
        // Explicitly map the 0-5 scale from Python to 0-255 for the Pump
        int pumpVal = map(pumpIn, 0, 5, 0, 255);
        digitalWrite(SOLENOID_PIN, (solenoid == 1) ? HIGH : LOW);
        analogWrite(PUMP_PIN, pumpVal);
        digitalWrite(LED_BUILTIN, pumpVal>0 ? HIGH : LOW); // Diagnostic LED
      }
      else if (mode == 1){ //auto
        bool inRange = abs(moveX) < sprayRad;
        if (inRange){
          if (!solenoidOpen){
            digitalWrite(SOLENOID_PIN, HIGH);
            solenoidOpened = millis();
            solenoidOpen = true;
          }
          if (millis() - solenoidOpened >= pumpDelay){
            analogWrite(PUMP_PIN, (int)(255*autoPumpPower));
            digitalWrite(LED_BUILTIN, HIGH);
          }
        } else{ // closes both solenoid and pump at the same time
          analogWrite(PUMP_PIN, 0);
          digitalWrite(SOLENOID_PIN, LOW);
          digitalWrite(LED_BUILTIN, LOW);
          solenoidOpen = false;
      }
    }
    int speedX = map(constrain(moveX, -focusWidth, focusWidth), -focusWidth, focusWidth, 0, 180.0);
    speedX = NEUTRAL + (int)((speedX - NEUTRAL) * xSpeed);
    yAngle = constrain(yAngle+(moveY * ySpeed), 0.0, 180.0);
    servoX.write(speedX);
    servoY.write((int)yAngle);
  }
}
  //return to neutral if no instruction
  if (millis() - lastSerialTime > SERIAL_TIMEOUT) {
    analogWrite(PUMP_PIN, 0);
    digitalWrite(SOLENOID_PIN, LOW);
    servoX.write(NEUTRAL);
    solenoidOpen = false;
  }
}