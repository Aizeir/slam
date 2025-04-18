
// Modules
#include <AFMotor.h>  
#include <NewPing.h>
#include <Servo.h> 

// Constantes
#define TRIG_PIN A0 
#define ECHO_PIN A1 
#define MAX_DISTANCE 200 // Distance maximum considérée (défaut: MAX_SENSOR_DISTANCE)
#define MAX_SPEED 130 // Vitesse du moteur

// Composants
AF_DCMotor motor1(1, MOTOR12_1KHZ); 
AF_DCMotor motor2(2, MOTOR12_1KHZ);
AF_DCMotor motor3(3, MOTOR34_1KHZ);
AF_DCMotor motor4(4, MOTOR34_1KHZ);
NewPing sonar(TRIG_PIN, ECHO_PIN, MAX_DISTANCE); 
Servo myservo;   

// Variables
bool goesForward = false;
int distance = 100; // mesure de l'ultrason
int radar_step = 4; // 1 mesure radar tous les 4 degrés

// Position / Orientation du robot initial
float x = 0; float y = 0; // position (en cm)
float angle = 0;          // angle robot (en deg)
float timer = millis();   // temps de la dernière mesure (en ms)

float real_speed = 37; // Vitesse robot (en cm/s)
float delai_mesure = 3000; // Temps max entre chaque mesure (en ms)


void setup() {
  myservo.attach(10);  
  myservo.write(115); 
  delay(2000);
  Serial.println("Radar Start");
  // il y avait 4 readPing conséicutifs inutilisés que j'ai enlevé (cf code ARDUINO_OBSTACLE_...)
}

void loop() {
  // Mesurer la distance
  distance = readPing(); // il y avait un delay 40, mais y a deja un delay 50 dans readPing donc je l'ai enlevé

  // Mesures radar toutes les x secondes (utilise timer)
  if (millis() - timer > delai_mesure) {
    calculer_position();
    radar();
    timer = millis();
  }

  // Avancer
  if (distance > 15){
    moveForward();
  }
  // Obstacle
  else if (distance <= 15) {
    // S'arrêter
    moveStop();
    calculer_position();
    
    // Reculer
    delay(100);
    moveBackward();
    delay(300);
    moveStop(); // (il y avait un delay 200 après)
  
    // Réajuster la position avec la difference de distances mesurées
    float d2 = readPing();
    x = x - (d2 - distance) * cos(angle * 3.14 / 180.);
    y = y - (d2 - distance) * sin(angle * 3.14 / 180.);
  
    // Mesures radar
    radar();

    // Mesures a droite et a gauche
    int distanceR = lookRight(); delay(200);
    int distanceL = lookLeft();  delay(200);

    // Décision droite ou gauche
    if (distanceR>=distanceL) {
      turnRight();
      moveStop();
    }
    else {
      turnLeft();
      moveStop();
    }

    // Mettre a jour timer pour qu'il soit le dernier temps de mesure
    timer = millis();
  }
}

int readPing() { 
  delay(50);
  int cm = sonar.ping_cm();
  if (cm==0) cm = 250;
  return cm;
}

void calculer_position() {
  float delai = millis() - timer;
  float distance_parcourue = delai * real_speed;

  // déplacement en x et en y
  x = x + distance_parcourue * cos(angle * 3.14 / 180.);
  y = y + distance_parcourue * sin(angle * 3.14 / 180.);
}

void radar(){
  // il faut adapter le code python !
  for (int pos = 0; pos <= 180; pos += radar_step) { // dans le sens antihoraire
    myservo.write(pos);
    Serial.print(x);   Serial.print(",");
    Serial.print(y);   Serial.print(",");
    Serial.print(pos); Serial.print(",");
    Serial.println(readPing());
  }
}

int lookRight() {
  myservo.write(50); 
  delay(500);
  int distance = readPing();
  delay(100);
  myservo.write(115); 
  return distance;
}
int lookLeft() {
    myservo.write(170); 
    delay(500);
    int distance = readPing();
    delay(100);
    myservo.write(115); 
    return distance;
}

// FONCTIONS MOTEURS
void marche(int moteur12, int moteur34) {
  moteur1.run(moteur12); moteur2.run(moteur12);
  moteur3.run(moteur34); moteur4.run(moteur34);
}
void rampe_vitesse() {
  // eviter de dépenser trop vite les batteries
  for (int speedSet = 0; speedSet < MAX_SPEED; speedSet +=2) {
    motor1.setSpeed(speedSet)
    motor2.setSpeed(speedSet);
    motor3.setSpeed(speedSet)
    motor4.setSpeed(speedSet);
    delay(5);
  }
}

void moveStop()
  marche(RELEASE,RELEASE);

void moveForward() {
  if (goesForward) return;
  goesForward = true;
  marche(FORWARD,FORWARD);
  rampe_vitesse();
}

void moveBackward() {
  goesForward = false;
  marche(BACKWARD,BACKWARD);
  rampe_vitesse();
}  

void turnRight() {    
  marche(BACKWARD,FORWARD);  
  delay(500);
  marche(FORWARD,FORWARD);  
} 

void turnLeft() {
  marche(FORWARD,BACKWARD);  
  delay(500);
  marche(FORWARD,FORWARD);
}  

/*
TOUS LES DELAYS:

- Mesure distance: 50 + ping

Arrêt:
- Stop: 0
- Reculer: 100 + 325 (sans compter les 300ms utiles)
- Réajuster la position: 50 + ping
- Radar: 45 * (50+ping) ~ 3s
- Mesure droite/gauche: 2 * (200 + 500 + 100 + 50 + ping) = 1.7s ?!
- Tourner: 500
- Réavancer: 65 * 5 = 325

3 secondes sans arrêt:
- Calculer la position: 0
- Radar: 3s

ping vaut 1 donc c'est assez peu
*/