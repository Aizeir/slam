#include <AFMotor.h>  
#include <Servo.h>

// Ports de sortie/entrée
const int trigPin = A0; //par là où on émet le signal
const int echoPin = A1; //par lmà où on recoit le signal

// Variables
long duration; int distance;

// MOTEURS (avec la carte Adafruit)
AF_DCMotor moteur1(1, MOTOR12_4KHZ);
AF_DCMotor moteur2(2, MOTOR12_4KHZ);
AF_DCMotor moteur3(3, MOTOR34_4KHZ);
AF_DCMotor moteur4(4, MOTOR34_4KHZ);

enum Direction { AVANT=1, ARRIERE=2, STATIQUE=0, DROITE=3, GAUCHE=4};
Direction direction = STATIQUE;

void setup() {
  // Initialiser la communication série
  Serial.begin(9600);
  
  // Définir les pins
  pinMode(trigPin, OUTPUT);pinMode(echoPin, INPUT);
  
  // MOTEURS
  moteur1.setSpeed(150);moteur2.setSpeed(150);
  moteur3.setSpeed(150);moteur4.setSpeed(150);
}

// FONCTIONS MOTEURS
void marche(int moteur12, int moteur34) {
   moteur1.run(moteur12); moteur2.run(moteur12);
   moteur3.run(moteur34); moteur4.run(moteur34);
}
void avant(){ marche(FORWARD,FORWARD); direction = AVANT; }
void arriere(){ marche(BACKWARD,BACKWARD); direction = ARRIERE; }
void tourner_droite(){ marche(FORWARD,BACKWARD); direction = DROITE; }
void tourner_gauche(){ marche(BACKWARD,FORWARD); direction = GAUCHE; }
void stop(){ marche(RELEASE,RELEASE); direction = STATIQUE; }


void loop() {
  // trucs obligatoire
  delay(100);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  // Distance (ultrason)
  duration = pulseIn(echoPin, HIGH);
  distance = duration * 0.0344 / 2;
  
  // Commande moteur
  if (distance < 100) tourner_droite();
  else avant();
  Serial.println(direction);
}
