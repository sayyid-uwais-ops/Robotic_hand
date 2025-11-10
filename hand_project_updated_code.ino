#include <Servo.h>

Servo fingerServos[5];  // Servos for 5 fingers
int angles[5] = {90, 90, 90, 90, 90}; // Default angles (all closed)

void setup() {
  Serial.begin(9600);

  // Attach each servo to corresponding pin
  fingerServos[0].attach(3);  // Thumb
  fingerServos[1].attach(5);  // Index
  fingerServos[2].attach(6);  // Middle
  fingerServos[3].attach(9);  // Ring
  fingerServos[4].attach(10); // Pinky

  // Initialize all fingers as closed (90°)
  for (int i = 0; i < 5; i++) {
    fingerServos[i].write(angles[i]);
  }
}

void loop() {
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();

    // Expecting format: F1:UP:R or F2:DOWN:L
    if (input.startsWith("F")) {
      int fingerIndex = input.substring(1, 2).toInt() - 1;

      if (fingerIndex >= 0 && fingerIndex < 5) {
        String state = input.substring(3, input.indexOf(':', 3)); // UP/DOWN
        String handType = input.substring(input.length() - 1);     // R or L

        if (fingerIndex == 0) {
          // Thumb behavior depends on hand
          if (handType == "R") {
            angles[fingerIndex] = (state == "UP") ? 90 : 0;
          } else if (handType == "L") {
            angles[fingerIndex] = (state == "UP") ? 0 : 90;
          }
        } else if (fingerIndex == 4) {
          // Pinky reversed
          angles[fingerIndex] = (state == "UP") ? 90 : 0;
        } else {
          // Other fingers normal
          angles[fingerIndex] = (state == "UP") ? 0 : 90;
        }

        // Move servo
        fingerServos[fingerIndex].write(angles[fingerIndex]);

        // Debug info
        Serial.print("Finger ");
        Serial.print(fingerIndex + 1);
        Serial.print(" -> ");
        Serial.println(angles[fingerIndex]);
      }
    }
  }
}
