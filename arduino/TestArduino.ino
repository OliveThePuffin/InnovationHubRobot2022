#include <math.h>

//Pin assignment for motors
int rightMotor = 9;
int leftMotor = 10;

float rightMotorV = 0; // initializing voltage to the motor to 0
float leftMotorV = 0;

int DIR1 = 7; //assigning direction pins to control which direction motors spin
int DIR2 = 8;

int enable = 4; //assigning enable pin to allow motor driver to work
int nSF = 12;

const int RDT = 3;               //R wheel channel inputs
const int RCLK = 5;

const int LDT = 2;                //L wheel channel inputs
const int LCLK = 11;

int RDTsensor = 0;
int RCLKsensor = 0;
long Rcount = 0;

int LDTsensor = 0;
int LCLKsensor = 0;
long Lcount = 0;

float r = 3.0;             // wheel radius in inches
float b = 11;              //wheelspan distance in inches

double velocityLeft = 0;  //velocity of left wheel
double velocityRight = 0; //velocity of right wheel

float currentPositionRight = 0.0;
float currentPositionLeft = 0.0;
float desiredPosition = 72.0;

float Kp = 20;
float Kd = .2;
float errorRight, errorLeft;
double prevErrorRight = 0;
double prevErrorLeft = 0;

float Vmax = 12;
float Vmin = -12;

unsigned long currTime = 0;
unsigned long prevTime = 0;
int Ts = 0;

double derivativeRight = 0.0;
double derivativeLeft = 0.0;

void setup() {
  Serial.begin(9600);           // open the serial port to print to serial monitor

  pinMode(RDT, INPUT_PULLUP);  // initialize pin 2 with an internal pull-up resistor
  pinMode(RCLK, INPUT_PULLUP);  // initialize pin 4 with an internal pull-up resistor
  pinMode(LDT, INPUT_PULLUP);  // initialize pin 2 with an internal pull-up resistor
  pinMode(LCLK, INPUT_PULLUP);  // initialize pin 4 with an internal pull-up resistor

  pinMode(rightMotor, OUTPUT);
  pinMode(leftMotor, OUTPUT);
  pinMode(DIR1, OUTPUT);
  pinMode(DIR2, OUTPUT);
  pinMode(enable, OUTPUT);

  digitalWrite(enable, HIGH);

  attachInterrupt(digitalPinToInterrupt(2), Rsensor, CHANGE); //  function for creating external interrupts on Pin 2 when a change is detected
  attachInterrupt(digitalPinToInterrupt(3), Lsensor, CHANGE); //  function for creating external interrupts on Pin 2 when a change is detected
}

void loop() {
  currTime = millis();

  currentPositionRight = float((Rcount / 3200.00) * 2.00 * M_PI * r);
  currentPositionLeft = float((-Lcount / 3200.00) * 2.00 * M_PI * r);

  //  Serial.print(Rcount);
  //  Serial.print('\t');
  //  Serial.println(Lcount);
  //
    Serial.print(currentPositionRight);
    Serial.print('\t');
    Serial.println(currentPositionLeft);

  errorRight = (desiredPosition - currentPositionRight) / desiredPosition;
  errorLeft = (desiredPosition - currentPositionLeft)  / desiredPosition;

  //  Serial.print(errorRight);
  //  Serial.print('\t');
  //  Serial.println(errorLeft);

  if (Ts > 0) {
    derivativeRight = (errorRight - prevErrorRight) / (currTime - prevTime);
    derivativeLeft = (errorLeft - prevErrorLeft) / (currTime - prevTime);
    prevErrorRight = errorRight;
    prevErrorLeft = errorLeft;
  }
  else {
    derivativeRight = 0;
    derivativeLeft = 0;
  }

  rightMotorV = Kp * errorRight + Kd * derivativeRight;
  leftMotorV = Kp * errorLeft + Kd * derivativeLeft;

  if (rightMotorV > Vmax) {
    rightMotorV = Vmax;
  }
  if (rightMotorV < Vmin) {
    rightMotorV = Vmin;
  }

  if (leftMotorV > Vmax) {
    leftMotorV = Vmax;
  }
  if (leftMotorV < Vmin) {
    leftMotorV = Vmin;
  }

  WriteRightMotorDriver(rightMotorV, Vmax);
  WriteLeftMotorDriver(leftMotorV, Vmax);

  Ts = millis() - currTime;
  delay(20 - Ts);
}

void WriteRightMotorDriver(float V, float Vmax) {
  int PWMval = int(100 * abs(V) / Vmax);
  if (PWMval > 100) {
    PWMval = 100;
  }
  if ( V < 0) {
    digitalWrite(DIR1, HIGH);
  }
  else if ( V > 0) {
    digitalWrite(DIR1, LOW);
  }
  else {
    digitalWrite(DIR1, LOW);
  }
  analogWrite(rightMotor, PWMval);
}

void WriteLeftMotorDriver(float V, float Vmax) {
  int PWMval = int(100 * abs(V) / Vmax);
  if (PWMval > 100) {
    PWMval = 100;
  }
  if ( V < 0) {
    digitalWrite(DIR2, LOW);
  }
  else if ( V > 0) {
    digitalWrite(DIR2, HIGH);
  }
  else {
    digitalWrite(DIR2, LOW);
  }
  analogWrite(leftMotor, PWMval);
}



void Rsensor() {
  RDTsensor = digitalRead(RDT);   // reads the state on pin 2 and assignes the value to a variable
  RCLKsensor = digitalRead(RCLK); // reads the state on pin 4 and assignes the value to a variable

  int posneg = 0;

  if (RDTsensor == RCLKsensor) {                    // if pin 2 and 4 states are the same the encoder is rotating CW
    Rcount += 2;
    posneg = 1;                                     // positive for CW
  }
  else if (RDTsensor != RCLKsensor) {               // if pin 2 and 4 states are different the encoder is rotating CCW
    Rcount -= 2;
    posneg  = -1;                                   // negative for CCW
  }
}

void Lsensor() {

  LDTsensor = digitalRead(LDT);   // reads the state on pin 3 and assignes the value to a variable
  LCLKsensor = digitalRead(LCLK); // reads the state on pin 5 and assignes the value to a variable

  int posneg = 0;
  // the delay is used to debounce the decoder by preventing the ISR from comparing too soon
  if (LDTsensor == LCLKsensor) {                    // if pin 2 and 4 states are the same the encoder is rotating CW
    Lcount += 2;
    posneg = -1;
  }
  else if (LDTsensor != LCLKsensor) {               // if pin 2 and 4 states are different the encoder is rotating CCW
    Lcount -= 2;
    posneg = +1;
  }
}
