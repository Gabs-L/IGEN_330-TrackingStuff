#include <Servo.h>

Servo servo;

const int SERVO_PIN = 9;
const int SAFE_POS = 90;
const unsigned long SERIAL_TIMEOUT = 500; // ms

unsigned long lastSerialTime = 0;

void setup() {
  Serial.begin(115200);
  servo.attach(SERVO_PIN);

  servo.write(SAFE_POS);  // safe startup position
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
