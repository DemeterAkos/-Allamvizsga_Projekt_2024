#include <WiFi.h>

// Wi-Fi AP settings
const char *ssid = "ESP32-AccesPoint";
const char *password = "12345678";

//Create Server port 
WiFiServer server(80);

//ADXL sensor data variables
int xVal = 0;
int yVal = 0;
int zVal = 0;

// LED pin
const int DPA = 18; 
const int DPB = 19;

//EmergencyLight and horn
const int Emergency_Light_and_Horn = 17;

//Distance beetwen robot car and object 
int distance = 25;

void setup() {
  // Serial communication 
  Serial.begin(115200);

  // LED pin for simulating driver triggers
  pinMode(DPA, OUTPUT);
  pinMode(DPB, OUTPUT);

  //Emergency Light and Horn Pin
  pinMode(Emergency_Light_and_Horn,OUTPUT);

  //Create Access Point 
  WiFi.softAP(ssid, password);
  
  // Print IP address
  IPAddress IP = WiFi.softAPIP();
  Serial.print("Access Point IP címe: ");
  Serial.println(IP);

  // Start server
  server.begin();
  Serial.println("Szerver fut...");
}

void loop() {
  // Client joint to server
  WiFiClient client = server.available();

  if (client) {
    Serial.println("Kliens csatlakozott.");
    
    // Waiting for the client
    while (client.connected()) {
      if (client.available()) {
        
        // Read sensor data from the client side
        String data = client.readStringUntil('\n');
        Serial.println("Kapott adat: " + data);
        
        int firstComma = data.indexOf(',');
        int secondComma = data.indexOf(',', firstComma + 1);

        if (firstComma != -1 && secondComma != -1) {
          // X value
          String xString = data.substring(0, firstComma);
          xVal = xString.toInt();

          // Y value
          String yString = data.substring(firstComma + 1, secondComma);
          yVal = yString.toInt();

          // Z value
          String zString = data.substring(secondComma + 1);
          zVal = zString.toInt();

          // print data to serial port
          Serial.print("X: ");
          Serial.println(xVal);
          Serial.print("Y: ");
          Serial.println(yVal);
          
        } else {
          Serial.println("Hibás adatformátum.");
        }
        
        //Process values and send trigger signal for motor driver

        if(yVal < 45 && distance > 8){
          digitalWrite(DPA,HIGH);
          digitalWrite(DPB,HIGH);
        }
        else if(yVal > 55){
          digitalWrite(DPA,HIGH);
          digitalWrite(DPB,HIGH);
        }
        else if(xVal < 45){
          digitalWrite(DPA,LOW);
          digitalWrite(DPB,HIGH);
          
        }
        else if(xVal > 55){
          digitalWrite(DPA,HIGH);
          digitalWrite(DPB,LOW);
        }
        else{
          digitalWrite(DPA,LOW);
          digitalWrite(DPB,LOW);
        }
        
      }
      
    }
   
    Serial.println("Kliens lecsatlakozott.");
  }
  
  
  
}
