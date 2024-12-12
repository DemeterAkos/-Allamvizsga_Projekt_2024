#include <WiFi.h>

// Wi-Fi AP adatok
const char* ssid = "ESP32-AccesPoint";
const char* password = "12345678";
const char* host = "192.168.4.1"; // Robot IP-address (AP)

//Initializing the WI-FI connection LED
const int comm_LED = 25; 
//Initializing the xyz data for ADXL sensor
const int in_X = 34;
const int in_Y = 35;
const int in_Z = 32;

struct SensorData {
  int x;
  int y;
  int z;
};

WiFiClient client;


void setup() {
  //Serial communication
  Serial.begin(115200);

  //Initialize the ADXL sensor inputs
  pinMode(in_X, INPUT);
  pinMode(in_Y, INPUT);
  pinMode(in_Z, INPUT);

  //Initialize the WI-FI Communication LED
  pinMode(comm_LED, OUTPUT);

  // Connecting to the robot IP addres
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    digitalWrite(comm_LED,LOW);
    delay(200);
    digitalWrite(comm_LED,HIGH);
    delay(200);
    Serial.println("Csatlakozás a Wi-Fi-hez...");
  }
  Serial.println("Csatlakozva!");

  // If client is Conected to the robot host 
  
  if (client.connect(host, 80)) {
    Serial.println("Csatlakozva a robot szerverhez.");
    digitalWrite(comm_LED,HIGH);
    
  } else {
    Serial.println("Nem sikerült csatlakozni.");
    digitalWrite(comm_LED,LOW);
  }
}

void loop() {
  //Read Data from ADXL sensor
  SensorData data;
  data.x = analogRead(in_X);
  data.y = analogRead(in_Y);
  data.z = analogRead(in_Z);

  // Scale the sensor data from 0-4095 to 0-20
  int scaledX = map(data.x, 0, 4095, 0, 50);
  int scaledY = map(data.y, 0, 4095, 0, 50);
  int scaledZ = map(data.z, 0, 4095, 0, 50);


  // If connection is alive send data to host
  if (client.connected()) {
    String data_to_send = String(scaledX) + "," + String(scaledY) + "," + String(scaledZ);
    client.println(data_to_send);
    Serial.println("Küldött adat: " + data_to_send);
    
}else{
  // If connection is lost, reconect
    Serial.println("Kapcsolat megszakadt, újracsatlakozás...");
    if (client.connect(host, 80)) {
      Serial.println("Újracsatlakozva a szerverhez.");
      digitalWrite(comm_LED, HIGH);
    } else {
      digitalWrite(comm_LED, LOW);
    }
  }
  
  delay(100);
  
}
