#include <stdlib.h>
#include <Servo.h>

#define SERVO_PIN (11)
Servo servo;

int brightness[3];
int get_max_brightness_sensor_index(int arr[], int n) {
  int idx = 0, max_val = arr[0];
  for (int i = 1; i < n; ++i) {
    if (arr[i] > max_val) {
      max_val = arr[i];
      idx = i;
    }
  }
  return idx;
}

int angle = 0;
char buf[1024];

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(3, OUTPUT);
  pinMode(4, OUTPUT);

  servo.attach(SERVO_PIN);
}

void loop() {
  brightness[0] = analogRead(A0);
  brightness[1] = analogRead(A1);
  brightness[2] = analogRead(A2);

  servo.write(angle);
  Serial.print(angle);

  int min_index = get_max_brightness_sensor_index(brightness, 3);
  if (min_index == 0) {
    angle = 0;
  } else if (min_index == 1) {
    angle = 90;
  } else if (min_index == 2) {
    angle = 180;
  }
  Serial.println("[" + String(min_index) + "]");

  sprintf(buf,"\n%d %d %d\n", brightness[0], brightness[1], brightness[2]);
  Serial.print(buf);

  delay(1000);
}
