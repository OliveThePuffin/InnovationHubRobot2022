/*
*/
#include "DualMC33926MotorShield.h"

DualMC33926MotorShield md;


float initialHeading = 90;
float initialSpeed = 100;
int MIN_HEADING = 0;
int MEDIAN_HEADING = 90;
int MAX_HEADING = 180;
int RATIO_MULTIPLIER = 1;

void setup() {
  md.init();
//  md.setSpeeds(100, -100);
  Serial.begin(9600); // activates the serial communication
  // Begin the robot speed once the tour is selected
//  initialRobotSpeed();

}

void loop() {
  // Read in current speed and heading
  if (Serial.available() >= 8) {    
    float currSpeed = serial_read_float();
    float currHeading = serial_read_float();
    // Convert speed and heading to motor outputs
    motorOutputs(currSpeed, currHeading);
  }
  
}

void initialRobotSpeed(){
  for(int i = 1; i < 5; i++){
    md.setSpeeds(i*25,i*25);
    delay(500);
  }
}
  

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

void motorOutputs(int currSpeed, int currHeading){
  int ratio = 1;
  boolean left = false;
  boolean right = false;
  int speedLeftMotor = 0;
  int speedRightMotor = 0;

  // Robot is trying to turn right
  if (currHeading > MEDIAN_HEADING){
    ratio = RATIO_MULTIPLIER*(currHeading / MEDIAN_HEADING);
    // Set right motor speed lower
    speedRightMotor = currSpeed / ratio;
  }
  // Robot is trying to turn left
  else{
    ratio = RATIO_MULTIPLIER*(MEDIAN_HEADING / currHeading);
    // Set right motor speed lower
    speedLeftMotor = currSpeed / ratio;
  }

  md.setSpeeds(speedLeftMotor, speedRightMotor);
  
}
