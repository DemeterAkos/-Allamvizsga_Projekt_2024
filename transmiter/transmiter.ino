#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

// CE and CSN pins for the nRF24L01
const int CE_PIN = 8;
const int CSN_PIN = 7;

// Create a Radio object
RF24 radio(CE_PIN, CSN_PIN);

// Address of the radio pipe
const byte Write_address[6] = "00001";
const byte Read_address[6] = "00002";

//Initializing the xyz data
const int in_X = A0;
const int in_Y = A1;
const int in_Z = A2;

//Siren pin

const int SirenaPin = 9;
int distance;

struct SensorData {
  int x;
  int y;
  int z;
};

void setup() {
  Serial.begin(9600);

  //Initialize the ADXL sensor inputs
  pinMode(in_X, INPUT);
  pinMode(in_Y, INPUT);
  pinMode(in_Z, INPUT);

   // Initialize the radio
  radio.begin();
  radio.openWritingPipe(Write_address);
  radio.openReadingPipe(1, Read_address);
  radio.setPALevel(RF24_PA_MIN);
  radio.stopListening();

  //Sirena Pin declare
  pinMode(SirenaPin,OUTPUT);
  
}

void loop() {

  SensorData data;
  data.x = analogRead(in_X);
  data.y = analogRead(in_Y);
  data.z = analogRead(in_Z);

  radio.write(&data, sizeof(data));
  delay(5);
  radio.startListening();
  
  if(radio.available()){
    radio.read(&distance, sizeof(distance));
    Serial.print("Received Distance: ");
    Serial.println(distance);   
  
  }
  
  delay(5);
  radio.stopListening();
  
  if(distance <= 8 && data.y < 332){
    digitalWrite(SirenaPin,HIGH);
  }
  else{
    digitalWrite(SirenaPin,LOW);
  }
  Serial.print("X: ");
  Serial.print(data.x);
  Serial.print(" Y: ");
  Serial.print(data.y);
  Serial.println("");
 
  delay(200);
  

}
