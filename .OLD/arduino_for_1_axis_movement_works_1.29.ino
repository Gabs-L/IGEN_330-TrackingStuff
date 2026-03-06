#include <Servo.h>

Servo servo;

const int SERVO_PIN = 9;

void setup() {
  Serial.begin(115200);
  servo.attach(SERVO_PIN);

  servo.write(90);  // safe startup position (center / stop)
  Serial.println("Arduino ready. Send 0–180.");
}



void loop() {

  int stop =90;

  if (Serial.available()) {

    int value = Serial.parseInt();   // expects 0–180

    if (value >= 0 && value <= 180) {
      servo.write(value);

      Serial.print("Input value: ");
      Serial.println(value);
    }

    
  
  }
}
