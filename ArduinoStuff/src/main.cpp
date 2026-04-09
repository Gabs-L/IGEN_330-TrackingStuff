#include <Arduino.h>
#include <Servo.h>
#include <math.h>

Servo servoX;
Servo servoY;

const int SERVOX_PIN = 10;
const int SERVOY_PIN = 11;
const int LIM_X_PIN = 6;
const int LIM_Y_PIN = 7;
const int SOLENOID_PIN = 12;
const int PUMP_PIN = 5;

const int NEUTRAL = 90; // 0-180
const int XfocusWidth = 160; // 160 (150+)
const int YfocusWidth = 85; // 85 (80-90)
const int sprayRad = 100; // 250 is big
float yAngle = 0;

const unsigned long SERIAL_TIMEOUT = 2000; // ms
unsigned long lastSerialTime = 0;
bool solenoidOpen = false;

const float xSpeed = 0.55; // 0.5 (the higher the more overshoot)
const float ySpeed = 0.02; // (0.01-0.5)
const float autoPumpPower = 1; // (0-1)

void setup() {
  Serial.begin(9600);
  Serial.setTimeout(50); //may need to increase

  pinMode(LED_BUILTIN, OUTPUT);

  servoX.attach(SERVOX_PIN);
  servoY.attach(SERVOY_PIN);
  
  pinMode(SOLENOID_PIN,OUTPUT);
  pinMode(PUMP_PIN, OUTPUT);
  pinMode(LIM_X_PIN, INPUT_PULLUP);
  pinMode(LIM_Y_PIN, INPUT_PULLUP);

  servoX.write(NEUTRAL);
  servoY.write((int)yAngle);
  digitalWrite(SOLENOID_PIN, LOW);
  analogWrite(PUMP_PIN, 0);
  lastSerialTime = millis();

  //TCCR2B = (TCCR2B & 0xF8) | 0x02;
}

void loop() {
  if (Serial.available() > 0){
    char buffer[64];
    int len = Serial.readBytesUntil('\n', buffer, sizeof(buffer)-1);
    buffer[len] = '\0';
    int mode, moveX, moveY, solenoid, pumpIn, detection;
    int received  = sscanf(buffer, "%d,%d,%d,%d,%d,%d", &mode, &moveX, &moveY, &solenoid, &pumpIn, &detection);
    int pumpVal = map(pumpIn, 0, 5, 0, 255);

    if (received == 6) {
      lastSerialTime = millis();

      bool xLimitTriggered = (digitalRead(LIM_X_PIN) == HIGH);
      bool yLimitTriggered = (digitalRead(LIM_Y_PIN) == HIGH);

      if (mode == 0) { // MANUAL
        analogWrite(PUMP_PIN, pumpVal);
        digitalWrite(SOLENOID_PIN, (solenoid == 1) ? HIGH : LOW);
        digitalWrite(LED_BUILTIN, pumpVal > 0 ? HIGH : LOW); // Diagnostic LED
      }
      else if (mode == 1){ //auto
        if (!detection) {
          analogWrite(PUMP_PIN, 0);
          digitalWrite(SOLENOID_PIN, LOW);
          digitalWrite(LED_BUILTIN, LOW);
          solenoidOpen = false;
        } else {
          float dist = sqrt((float)moveX*moveX+(float)moveY*moveY);
          bool inRange = dist < sprayRad;
          if (inRange){
            solenoidOpen = true; 
            digitalWrite(SOLENOID_PIN, HIGH);
            analogWrite(PUMP_PIN, (int)(255*autoPumpPower));
            digitalWrite(LED_BUILTIN, HIGH);
          } else { // closes both solenoid and pump at the same time
            analogWrite(PUMP_PIN, 0);
            digitalWrite(SOLENOID_PIN, LOW);
            digitalWrite(LED_BUILTIN, LOW);
            solenoidOpen = false;
          }
        }
      }

      int speedX = map(constrain(moveX, -XfocusWidth, XfocusWidth), -XfocusWidth, XfocusWidth, 0, 180.0);
      speedX = NEUTRAL - (int)((speedX - NEUTRAL) * xSpeed);
      
      if (xLimitTriggered && moveX > 0) {
          speedX = NEUTRAL; 
      }

      float yRange = constrain(moveY, -YfocusWidth, YfocusWidth);
      float deltaY = yRange * ySpeed;
      float nextAngle = yAngle - deltaY;

      if (yLimitTriggered) {
          bool movingToCenter = (nextAngle > yAngle && yAngle < 65) || (nextAngle < yAngle && yAngle > 65);
          
          if (movingToCenter) {
              yAngle = constrain(nextAngle, 0.0, 130.0);
          }
      } else {
          yAngle = constrain(nextAngle, 0.0, 130.0);
      }
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