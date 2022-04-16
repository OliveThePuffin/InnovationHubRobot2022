#include <LiquidCrystal.h>

const int rs = 12, en = 11, d4 = 5, d5 = 4, d6 = 3, d7 = 2;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

union byte_float {
  float flt;
  unsigned char bytes[4];
};

float serial_read_float() {
  union byte_float ret;
  for (int i = 3; i >= 0; i--) {
      ret.bytes[i] = Serial.read();
  }
  return ret.flt;
}

void setup()
{
  Serial.begin(9600);
  lcd.begin(16, 2);
  lcd.clear();
}

float distance, orientation;
void loop()
{
  if (Serial.available() >= 8) {    
    distance = serial_read_float();
    orientation = serial_read_float();

    //lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print(distance, 12);
    lcd.setCursor(0, 1);
    lcd.print(orientation, 12);
  }
  delay(10);
}
