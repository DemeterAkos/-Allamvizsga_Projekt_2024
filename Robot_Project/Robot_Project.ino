#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

//Ultrasonic sensor pins eclaration
const int trigPin = 3;
const int echoPin = 2;

//Motor Driver Ports Declaration
//Driver Port A
const int DriverPortA1A = 4;
const int DriverPortA1B = 10;

//Driver Port B
const int DriverPortB1A = 5;
const int DriverPortB1B = 6;

// CE and CSN pins for the nRF24L01
const int CE_PIN = 7;
const int CSN_PIN = 8;

// Create a Radio object
RF24 radio(CE_PIN, CSN_PIN);

// Addresses of the radio pipe
const byte Read_address[6] = "00001";
const byte Write_address[6] = "00002";



struct SensorData {
  int x;
  int y;
  int z;
};

//Variables for Ultrasonic Sensor

long duration;
int distance;
int btn_state = 0;

void setup() {

  //Ultrasonic Sensor Pins 
  pinMode(trigPin,OUTPUT);
  pinMode(echoPin,INPUT);

  //Motor Driver Ports pins
  pinMode(DriverPortA1A,OUTPUT);
  pinMode(DriverPortA1B,OUTPUT);
  pinMode(DriverPortB1A,OUTPUT);
  pinMode(DriverPortB1B,OUTPUT);

  // Initialize the radio
  radio.begin();
  radio.openReadingPipe(1, Read_address);
  radio.openWritingPipe(Write_address);
  radio.setPALevel(RF24_PA_MIN);
  radio.startListening();

  //Serial communication 9600 bps
  Serial.begin(9600);
}


void loop() {
  //Ultrasonic sensor function

  distance = UltrasonicSensor();

  Serial.print("Distance for the Object = ");
  Serial.print(distance);
  Serial.println(" cm");

  ControlUnit(distance);

  delay(100);

}


//Functions Inicialization and declaration 

int UltrasonicSensor(){
  //Clear the trigPin
  digitalWrite(trigPin,LOW);
  delayMicroseconds(2);

  //Set the trigPin on HIGH state 10 microseconds

  digitalWrite(trigPin,HIGH);
  delayMicroseconds(10);

  //Reads the echoPin, returns the sound wave travel time in microsecond

  duration = pulseIn(echoPin, HIGH);

  //Calculating the distance in cm

  distance = duration * 0.034/2;


  return distance;

}


void ControlUnit(int distance){
 
  //Driver Ports Activate and read the ADXL sensor values from the transmiter part
  
  if(radio.available()){
    SensorData data;
    radio.read(&data, sizeof(data));

    if(data.y < 332 && distance > 8){
      Go_Forward();
    }
    else if(data.y > 380){
      Go_Backward();
    }
     else if(data.x < 338 && data.y > 332 and data.y < 380){
      Turn_Right();
    }
     else if(data.x > 380 && data.y > 332 and data.y < 380){
      Turn_Left();
    }
    else{
      Stop_Moveing();
    }

    Serial.print("Received X: ");
    Serial.print(data.x);
    Serial.print(" Y: ");
    Serial.print(data.y);
    Serial.println("");

    // Activate Siren and send data to transmitter if distance <= 8 cm
    if (data.y < 332 && distance <= 8) {

      radio.stopListening();
      radio.write(&distance, sizeof(distance));
      radio.startListening();
  }
    
  }

}


void Stop_Moveing(){
  //Port A control
  digitalWrite(DriverPortA1A, LOW);
  digitalWrite(DriverPortA1B, LOW);

  //Port B control
  digitalWrite(DriverPortB1A, LOW);
  digitalWrite(DriverPortB1B, LOW);
}

void Go_Forward(){
  //Port A control
  digitalWrite(DriverPortA1A, HIGH);
  digitalWrite(DriverPortA1B, LOW);

  //Port B control
  digitalWrite(DriverPortB1A, HIGH);
  digitalWrite(DriverPortB1B, LOW);
}

void Go_Backward(){
   //Port A control
  digitalWrite(DriverPortA1A, LOW);
  digitalWrite(DriverPortA1B, HIGH);

  //Port B control
  digitalWrite(DriverPortB1A, LOW);
  digitalWrite(DriverPortB1B, HIGH);
}

void Turn_Left(){
   //Port A control
  digitalWrite(DriverPortA1A, LOW);
  digitalWrite(DriverPortA1B, LOW);

  //Port B control
  digitalWrite(DriverPortB1A, HIGH);
  digitalWrite(DriverPortB1B, LOW);
}

void Turn_Right(){
   //Port A control
  digitalWrite(DriverPortA1A, HIGH);
  digitalWrite(DriverPortA1B, LOW);

  //Port B control
  digitalWrite(DriverPortB1A, LOW);
  digitalWrite(DriverPortB1B, LOW);
}



