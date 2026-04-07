#include <Arduino.h>
#include <Servo.h>
#include <math.h>

Servo servoX;
Servo servoY;

const int SERVOX_PIN = 9;
const int SERVOY_PIN = 8;
const int SOLENOID_PIN = 7;
const int PUMP_PIN = 3;

const int NEUTRAL = 90; // 0-180
const int XfocusWidth = 250; // 500
const int YfocusWidth = 150; // 300
const int sprayRad = 100; // 250 is big

const unsigned long SERIAL_TIMEOUT = 2000; // ms
unsigned long lastSerialTime = 0;
unsigned long solenoidOpened;
const int pumpDelay = 100; // ms
bool solenoidOpen = false;

const float xSpeed = 0.50; // (0-1)
// const float ySpeed = 0.15; // (0-1)
float yAngle = 0;
const float ySpeed = 0.03; // (0-0.5)
const float autoPumpPower = 1; // (0-1)

void setup() {
  Serial.begin(9600);
  Serial.setTimeout(50); //may need to increase

  pinMode(LED_BUILTIN, OUTPUT);

  servoX.attach(SERVOX_PIN);
  servoY.attach(SERVOY_PIN);
  
  pinMode(SOLENOID_PIN,OUTPUT);
  pinMode(PUMP_PIN, OUTPUT);

  servoX.write(NEUTRAL);
  // servoY.write(NEUTRAL);
  servoY.write((int)yAngle);
  digitalWrite(SOLENOID_PIN, LOW);
  analogWrite(PUMP_PIN, 0);
  TCCR2B = (TCCR2B & 0xF8) | 0x01; //Sets uber high freq to pins 3 and 11. MUST BE PUT AFTER SERVO STUFF SINCE THOSE OVERWRITE THIS
  lastSerialTime = millis();
}

void loop() {
  if (Serial.available() > 0){
    char buffer[64];
    int len = Serial.readBytesUntil('\n', buffer, sizeof(buffer)-1);
    buffer[len] = '\0';
    int mode, moveX, moveY, solenoid, pumpIn, detection;
    int received  = sscanf(buffer, "%d,%d,%d,%d,%d,%d", &mode, &moveX, &moveY, &solenoid, &pumpIn, &detection);
    if (received == 6) {
      lastSerialTime = millis();
      if (mode == 0) { // MANUAL
        // Explicitly map the 0-5 scale from Python to 0-255 for the Pump
        int pumpVal = map(pumpIn, 0, 5, 0, 255);
        bool solState = (solenoid == 1);
        analogWrite(PUMP_PIN, pumpVal);
        digitalWrite(SOLENOID_PIN, solState ? HIGH : LOW);
        solenoidOpen = solState;
        digitalWrite(LED_BUILTIN, pumpVal>0 ? HIGH : LOW); // Diagnostic LED
      }
      else if (mode == 1){ //auto
        if (!detection) {
          analogWrite(PUMP_PIN, 0);
          digitalWrite(SOLENOID_PIN, LOW);
          digitalWrite(LED_BUILTIN, LOW);
          solenoidOpen = false;
        } else {
          float dist = sqrt((long)moveX*moveX+(long)moveY*moveY);
          bool inRange = dist < sprayRad;
          if (inRange){
            if (!solenoidOpen){
              digitalWrite(SOLENOID_PIN, HIGH);
              solenoidOpen = true;
            }
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
      // int speedY = map(constrain(moveY, -YfocusWidth, YfocusWidth), -YfocusWidth, YfocusWidth, 0, 180.0);
      speedX = NEUTRAL + (int)((speedX-NEUTRAL) * xSpeed);
      // speedY = NEUTRAL + (int)((NEUTRAL-speedY) * ySpeed);
      yAngle = constrain(yAngle+(moveY * ySpeed), 0.0, 150.0); //max defl. = 150
      servoX.write(speedX);
      // servoY.write(speedY);
      servoY.write((int)yAngle);
    }
  }
  //return to neutral if no instruction
  if (millis() - lastSerialTime > SERIAL_TIMEOUT) {
    analogWrite(PUMP_PIN, 0);
    digitalWrite(SOLENOID_PIN, LOW);
    servoX.write(NEUTRAL);
    // servoY.write(NEUTRAL);
    solenoidOpen = false;
  }
}