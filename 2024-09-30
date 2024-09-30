#include <stdlib.h>

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(3, OUTPUT);
  pinMode(4, OUTPUT);
}

int get_min_index(int arr[]) {
  int idx = 0, max_val = arr[0];
  for (int i = 1; i < 6; ++i) {
    if (arr[i] < max_val) {
      max_val = arr[i];
      idx = i;
    }
  }
  return idx;
}

int val[5];

void loop() {
  val[0] = analogRead(A0);
  val[1] = analogRead(A1);
  val[2] = analogRead(A2);
  val[3] = analogRead(A3);
  val[4] = analogRead(A4);
  val[5] = analogRead(A5);

  int min_index = get_min_index(val);
  if (min_index == 1 || min_index == 2 || min_index == 3) {
    Serial.print("Turn Right");
    digitalWrite(3, HIGH);
    digitalWrite(4, LOW);
  } else if (min_index == 4 || min_index == 5) {
    Serial.print("Turn Left");
    digitalWrite(4, HIGH);
    digitalWrite(3, LOW);
  } else if (min_index == 0) {
    Serial.print("Stop");
  }
  Serial.println("["+String(min_index) +"]");

  char buffer[1024];
  sprintf(buffer, "%d, %d, %d, %d, %d, %d", analogRead(A0), analogRead(A1), analogRead(A2), analogRead(A3), analogRead(A4), analogRead(A5));

}
