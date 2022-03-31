#include <LiquidCrystal.h>

const int rs = 12, en = 11, d4 = 5, d5 = 4, d6 = 3, d7 = 2;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

float distance_from_pi;
float orientation_from_pi;

void setup() {
  lcd.begin(16, 2);
  Serial.begin(9600);
}

void read_from_serial() {    
  long tmp_distance_long;
  long tmp_orientation_long;

  byte data[8];
  for(int i = 0; i < 8; i++) {
    data[i] = Serial.read();
  }

  for(byte j = 0; j < 4; j++) tmp_distance_long = (long(data[j]) << ((j) << 3)) | tmp_distance_long;
  distance_from_pi = *((float *)&tmp_distance_long);

  for(byte j = 4; j < 8; j++) tmp_orientation_long = (long(data[j]) << ((j-4) << 3)) | tmp_orientation_long;
  orientation_from_pi = *((float *)&tmp_orientation_long);
}

void loop() {
  if (Serial.available() >= 8) {
    read_from_serial();

    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print(distance_from_pi);
    lcd.setCursor(0, 1);
    lcd.print(orientation_from_pi);
  }
  delay(10);
}
