#include <AFMotor.h>  
#include <NewPing.h>
#include <Servo.h>
 
#define TRIG_PIN A0 
#define ECHO_PIN A1 
#define MAX_DISTANCE 200 

NewPing sonar(TRIG_PIN, ECHO_PIN, MAX_DISTANCE); 
Servo myservo;   


int pos = 0;    // servo starting position int
float duration,distance;
 
void setup() {
  Serial.begin(115200);
  Serial.println("Radar Start");
  myservo.attach(10); // start servo control
}
 
void loop() {
  for (pos = 0; pos <= 180; pos += 1) { // goes from 0 degrees to 180 degrees
    // in steps of 1 degree
    myservo.write(pos);              // tell servo to go to position in variable 'pos'
    dist_calc(pos);
  }
 
  for (pos = 180; pos >= 0; pos -= 1) { // goes from 180 degrees to 0 degrees
    myservo.write(pos);              // tell servo to go to position in variable 'pos'
    dist_calc(pos);
  }
}
 
float dist_calc(int pos){
  distance = readPing();
  Serial.print(pos); // position of servo motor
  Serial.print(","); // comma separate variables
  Serial.println(distance); // print distance in cm
 
}

int readPing() { 
  delay(100); //50
  int cm = sonar.ping_cm();
  if(cm==0)
  {
    cm = 250;
  }
  return cm;
}