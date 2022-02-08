/*
   The purpose of this code is to count the ouput pulses or
   the encoder outputs as you rotate the Motor shaft. You can run the
   same code on the Arduino Uno, Arduino Nano, Arduino Mega, etc.
*/
#define Encoder_output_A 2 // pin2 of the Arduino
#define Encoder_output_B 6 // pin 3 of the Arduino
#include "DualMC33926MotorShield.h"

DualMC33926MotorShield md;

// these two pins has the hardware interrupts as well.

int Count_pulses = 0;
float deg = 0.0;
float revolutions = 0.0;
float arcLength = 0.0;

float centerOfWheelToCenterOfRobotMM = 10.5 * 25.4; //in to mm
float wheelDiameter = 6 * 25.4; //in to mm
float wheelCircumference = PI * wheelDiameter; //mm
int gearRatio = 50;

void setup() {
  md.init();
  md.setSpeeds(100, -100);
  Serial.begin(9600); // activates the serial communication
  pinMode(Encoder_output_A, INPUT); // sets the Encoder_output_A pin as the input
  pinMode(Encoder_output_B, INPUT); // sets the Encoder_output_B pin as the input
  attachInterrupt(digitalPinToInterrupt(Encoder_output_A), DC_Motor_Encoder, RISING);
}

void loop() {
  Serial.println("Result: ");
  Serial.println(Count_pulses);
  revolutions = Count_pulses / 800.0;
  arcLength = wheelCircumference * revolutions;
  deg = (arcLength * 360) / (2 * PI * centerOfWheelToCenterOfRobotMM);
  if (deg >= 90) md.setSpeeds(0, 0);
}

void DC_Motor_Encoder() {
  int b = digitalRead(Encoder_output_B);
  if (b > 0) {
    Count_pulses++;
  }
  else {
    Count_pulses--;
  }
}
