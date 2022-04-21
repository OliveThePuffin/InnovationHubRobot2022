#include "DualMC33926MotorShield.h"
#include <math.h>

//define parameters
#define TICKS_PER_ROTATION  800
#define DUTY_CYCLE          127
#define WHEEL_RADIUS        0.184
#define ROBOT_WIDTH         0.027

#define MINPWM		    0x20
#define MAXPWM		    0xFF

//Define functions
//#define min(a,b) ((a)<(b)?(a):(b))

DualMC33926MotorShield md;

//Pin assignments
const int ENCODER[]     = {5, 3, 11, 2};   //1A,B; 2A,B
const int ENCODER_ISR[] = {3, 2};           //1,2
const int MOTORDIR[]    = {7, 8};           //1,2
const int MOTORPWM[]    = {9, 10};          //1,2

//Global variables
int desiredRotation1 = 0;
int desiredRotation2 = 0;
int rotation1 = 0;
int rotation2 = 0;

int pwm = 0;

byte receiveData;
byte sendData;
char receiveStr[5] = {' ', ' ', ' ', ' ', '\0'};

bool moveCommand = false;
bool circleCommand = false;
bool rotateCommand = false;
int  arg;

int encoder1last = 0;
int encoder1current = 0;
int encoder2last = 0;
int encoder2current = 0;

unsigned int lastTime1 = 0;
unsigned int currentTime1 = 0;
unsigned int lastTime2 = 0;
unsigned int currentTime2 = 0;

float deltaT1 = 0;
float deltaT2 = 0;

double v1 = 0;
double v2 = 0;

double x = 0;
double y = 0;
double phi = 0;

void stopIfFault() {
    if (md.getFault()) {
        Serial.println("Motor Controller fault");
        while(true);
    }
}

void setup() {
    //Set up Serial communication
    Serial.begin(9600);

    //Encoder pins
    pinMode(ENCODER[0], INPUT);
    pinMode(ENCODER[1], INPUT);
    pinMode(ENCODER[2], INPUT);
    pinMode(ENCODER[3], INPUT);
    pinMode(ENCODER_ISR[0], INPUT);
    pinMode(ENCODER_ISR[1], INPUT);

    //Motor controller pins
    pinMode(MOTORDIR[0], OUTPUT);
    pinMode(MOTORDIR[1], OUTPUT);
    pinMode(MOTORPWM[0], OUTPUT);
    pinMode(MOTORPWM[1], OUTPUT);

    //Interrupts
    attachInterrupt(digitalPinToInterrupt(ENCODER_ISR[0]), turn, CHANGE);
    attachInterrupt(digitalPinToInterrupt(ENCODER_ISR[1]), turn, CHANGE);

    md.init();
}

void loop() {
    if (moveCommand) movebot(arg);
    if (rotateCommand) rotatebot(arg);
    if (circleCommand) circlebot(arg);

}


void serialEvent() {

    if (Serial.available() > 0) {
        byte receiveData = Serial.read();
        switch (receiveData) {

            //STOP
            case '~':
		Serial.println("STOP");
		moveCommand = false;
		rotateCommand = false;
		circleCommand = false;
	        analogWrite(MOTORPWM[0], pwm);
                analogWrite(MOTORPWM[1], pwm);
                break;

            //ROTATE
            case ',':
		Serial.println("ROTATE");
                receiveStr[0] = ' ';
                receiveStr[1] = ' ';
                receiveStr[2] = ' ';
                receiveStr[3] = ' ';
                while (true) {
                    if (Serial.available() > 0) {
                        receiveData = Serial.read();
                        if (receiveData == '!') break;
                        receiveStr[0] = receiveStr[1];
                        receiveStr[1] = receiveStr[2];
                        receiveStr[2] = receiveStr[3];
                        receiveStr[3] = receiveData;
                    }
                }
                rotateCommand = true;
                arg = atof(receiveStr);
                break;

            //MOVE
            case ':':
		Serial.println("MOVE");
                receiveStr[0] = ' ';
                receiveStr[1] = ' ';
                receiveStr[2] = ' ';
                receiveStr[3] = ' ';
                while (receiveData != '!') {
                    if (Serial.available() > 0) {
                        receiveData = Serial.read();
                        if (receiveData == '!') break;
                        receiveStr[0] = receiveStr[1];
                        receiveStr[1] = receiveStr[2];
                        receiveStr[2] = receiveStr[3];
                        receiveStr[3] = receiveData;
                    }
                }
		if (atof(receiveStr) == 0) {
		    digitalWrite(MOTORDIR[0], false);
                    digitalWrite(MOTORDIR[1], true);

		    analogWrite(MOTORPWM[0], 64);
                    analogWrite(MOTORPWM[1], 64);
		}
		else {
                    moveCommand = true;
                    arg = atof(receiveStr);
		}
                break;

            //CIRCLE
            case ';':
		Serial.println("CIRCLE");
                receiveStr[0] = ' ';
                receiveStr[1] = ' ';
                receiveStr[2] = ' ';
                receiveStr[3] = ' ';
                while (receiveData != '!') {
                    if (Serial.available() > 0) {
                        receiveData = Serial.read();
                        if (receiveData == '!') break;
                        receiveStr[0] = receiveStr[1];
                        receiveStr[1] = receiveStr[2];
                        receiveStr[2] = receiveStr[3];
                        receiveStr[3] = receiveData;
                    }
                }
                circleCommand = true;
                arg = atof(receiveStr);
                break;
        }
    }
}

void movebot(float distance) {
    distance /= 2;
    if(distance == 0) return;
    distance *= 0.3048;
    //Serial.println("distance: ");
    //Serial.println(distance);
    double startX = x;
    double startY = y;

    //forward
    if(distance > 0) {
        digitalWrite(MOTORDIR[0], false);
        digitalWrite(MOTORDIR[1], true);
    }
    //backward
    if(distance < 0) {
        digitalWrite(MOTORDIR[0], true);
        digitalWrite(MOTORDIR[1], false);
        distance = -distance;
    }

    float traveled = sqrt(pow((startX - x), 2) + pow((startY - y), 2));
    while(traveled < distance) {
        traveled = sqrt(pow((startX - x), 2) + pow((startY - y), 2));
        serialEvent();
        if (!moveCommand) break;

	//Update PWM
	int multiplier = 50;
	if (traveled <= distance/2) {
		pwm = min( multiplier * traveled + MINPWM, MAXPWM );
		}
	else if (traveled > distance/2 && traveled < distance) {
		pwm = min( multiplier * (distance - traveled) + MINPWM, MAXPWM );
		}
	else{
		pwm = 0;
	}

        analogWrite(MOTORPWM[0], pwm);
        analogWrite(MOTORPWM[1], pwm);
        Serial.print("");
    }

    //stop motors after movement
    moveCommand = false;
    analogWrite(MOTORPWM[0], false);
    analogWrite(MOTORPWM[1], false);
}

void rotatebot(float degrees) {
    float rads = degrees * 2*PI/360;

    //if (degrees == 360) {
    //    rads = 3*2*PI*1.05;
    //}
    //Serial.println("destination:");
    //Serial.println(rads);
    double startPhi = phi;

    //rotate right
    if (rads < 0) {
        digitalWrite(MOTORDIR[0], false);
        digitalWrite(MOTORDIR[1], false);
        rads = -rads;
    }
    //rotate left
    else {
        digitalWrite(MOTORDIR[0], true);
        digitalWrite(MOTORDIR[1], true);
    }
    while(abs(phi - startPhi) < rads) {
        serialEvent();
        if (!rotateCommand) break;

	//Update PWM
	int multiplier = 50;
	if (traveled <= rads/2) {
		pwm = min( multiplier * abs(phi-startPhi) + MINPWM, MAXPWM );
		}
	else if (traveled > rads/2 && traveled < rads) {
		pwm = min( multiplier * (rads - abs(phi-startPhi)) + MINPWM, MAXPWM );
		}
	else{
		pwm = 0;
	}

            analogWrite(MOTORPWM[0], pwm);
            analogWrite(MOTORPWM[1], pwm);
            Serial.print("");
    }

    //stop motors
    rotateCommand = false;
    analogWrite(MOTORPWM[0], 0);
    analogWrite(MOTORPWM[1], 0);
}

void circlebot(float radius) {
    if(radius == 0) {
        circleCommand = false;
        rotateCommand = true;
        arg = 360;
    }
    //find maximum pwms for each wheel based on radius
    float leftRadius = radius*0.3048 - ROBOT_WIDTH*5;
    float rightRadius = radius*0.3048 + ROBOT_WIDTH*5;
    int multiplier = 500/radius;
    int leftpwm = int(leftRadius * multiplier);
    int rightpwm = int(rightRadius * multiplier);

    double startPhi = phi;

    if(leftpwm > 0) digitalWrite(MOTORDIR[0], false);
    if(leftpwm < 0) digitalWrite(MOTORDIR[0], true);
    if(rightpwm > 0) digitalWrite(MOTORDIR[1], true);
    if(rightpwm < 0) digitalWrite(MOTORDIR[1], false);
    analogWrite(MOTORPWM[0], abs(leftpwm));
    analogWrite(MOTORPWM[1], abs(rightpwm));

    while(abs(phi-startPhi) < 2*PI) {
        serialEvent();
        if (!circleCommand) break;
        if(phi-startPhi < (2*PI)/24) {
            analogWrite(MOTORPWM[0], 0);
            analogWrite(MOTORPWM[1], abs(rightpwm));
        }
        else {
            analogWrite(MOTORPWM[0], abs(leftpwm));
            analogWrite(MOTORPWM[1], abs(rightpwm));
        }
        Serial.print("");
    }

    //stop motors
    circleCommand = false;
    analogWrite(MOTORPWM[0], 0);
    analogWrite(MOTORPWM[1], 0);
}

void turn() {
    //wheel 1
    encoder1last = encoder1current;
    encoder1current = digitalRead(ENCODER[0])*2 + digitalRead(ENCODER[1]);
    if (encoder1last == 3 && encoder1current == 2) {
        updateLocRot(0, -4);
    }
    else if (encoder1last == 2 && encoder1current == 3) {
        updateLocRot(0, 4);
    }

    //wheel 2
    encoder2last = encoder2current;
    encoder2current = digitalRead(ENCODER[2])*2 + digitalRead(ENCODER[3]);

    if (encoder2last == 3 && encoder2current == 2) {
        updateLocRot(1, 4);
    }
    else if (encoder2last == 2 && encoder2current == 3) {
        updateLocRot(1, -4);
    }
}

void movebotArc(float distanceToObject) {
  float degrees = 90.0
  rotatebot(degrees);
  
}

void updateLocRot(bool wheel, int dir) {
    //Left
    if(!wheel) {
        rotation1 += dir;
        lastTime1 = currentTime1;
        currentTime1 = micros();
        deltaT1 = currentTime1 - lastTime1;
        if (deltaT1 == 0) deltaT1 = 0.5;
        v1 = WHEEL_RADIUS*dir*(2*PI/TICKS_PER_ROTATION) / ((float)deltaT1);
        x = x + cos(phi)*(v1*deltaT1)/2;
        y = y + sin(phi)*(v1*deltaT1)/2;
        phi = phi + (WHEEL_RADIUS/ROBOT_WIDTH)*(v1*deltaT1);
    }

    //Right
    else {
        rotation2 += dir;
        lastTime2 = currentTime2;
        currentTime2 = micros();
        deltaT2 = currentTime2 - lastTime2;
        if (deltaT2 == 0) deltaT2 = 0.5;
        v2 = WHEEL_RADIUS*dir*(2*PI/TICKS_PER_ROTATION) / ((float)deltaT2);
        x = x + cos(phi)*(-v2*deltaT2)/2;
        y = y + sin(phi)*(-v2*deltaT2)/2;
        phi = phi - (WHEEL_RADIUS/ROBOT_WIDTH)*(-v2*deltaT2);
    }
}
