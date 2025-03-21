#include <WiFi.h>
#include <HTTPClient.h>

String URL = "http://192.168.100.26/robot_data/test_data.php";


// Wi-Fi AP settings
const char *ssid = "ESP32-AccesPoint";
const char *password = "12345678";

//// Wi-Fi client settings (for external network connection)
const char *ssidClient = "DIGI-YpsU";  
const char *passwordClient = "kTS4N8Jv"; 

//Create Server port 
WiFiServer server(80);

//Ultrasonic sensor pins eclaration
const int trigPin = 33;
const int echoPin = 26;

//Motor Drivers Declaration
//DriverA 
const int DriverA_PortA1A = 13;
const int DriverA_PortA1B = 15;

//DriverB
const int DriverB_PortA1A = 14;
const int DriverB_PortA1B = 12;

//Microswitch pins declaration
//Front switches
const int Switch_Front_Right = 2;
const int Switch_Front_Center = 4;
const int Switch_Front_Left = 16;

//Back switches 
const int Switch_Back_Right = 21;
const int Switch_Back_Center = 22;
const int Switch_Back_Left = 23;


//ADXL sensor data variables
int xVal = 0;
int yVal = 0;
int zVal = 0;

//Variables for Ultrasonic Sensor
long duration;
int distance;


//EmergencyLight and horn
const int Emergency_Light_and_Horn = 17;


// Collision detection
bool collisionDetected = false;
String direction;
int collision_ON = 0;

//upload time to database
unsigned long lastUploadTime = 0;
const long uploadInterval = 2000; // 2 sec

// Function declarations (prototypes)
int UltrasonicSensor();
void MotorControlUnit(int distance, int xVal, int yVal);
void Stop_Moveing();
void Go_Forward();
void Go_Backward();
void Turn_Left();
void Turn_Right();
void Collision();
void uploadDataToServer(int x, int y, int distance, String direction, int collision);

void setup() {
  // Serial communication 
  Serial.begin(115200);

  WiFi.mode(WIFI_AP_STA);

  //Ultrasonic Sensor Pins 
  pinMode(trigPin,OUTPUT);
  pinMode(echoPin,INPUT);

  //Motor Drivers pins initialization
  pinMode(DriverA_PortA1A,OUTPUT);
  pinMode(DriverA_PortA1B,OUTPUT);
  pinMode(DriverB_PortA1A,OUTPUT);
  pinMode(DriverB_PortA1B,OUTPUT);

  //Switches initialization
  pinMode(Switch_Front_Right,INPUT);
  pinMode(Switch_Front_Left,INPUT);
  pinMode(Switch_Front_Center,INPUT);
  pinMode(Switch_Back_Right,INPUT);
  pinMode(Switch_Back_Left,INPUT);
  pinMode(Switch_Back_Center,INPUT);

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

  // Connect to external Wi-Fi network for data upload
  WiFi.begin(ssidClient, passwordClient);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to Wi-Fi network");
}

void loop() {
  // Client joint to server
  WiFiClient client = server.available();

  if (client) {
    Serial.println("Kliens csatlakozott.");
    
    // Waiting for the client
    while (client.connected()) {
      if (client.available()) {

        //Ultrasonic sensor function

        distance = UltrasonicSensor();
        Serial.print("Distance for the Object = ");
        Serial.print(distance);
        Serial.println(" cm");
        
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

        //Robot Collision function
        Collision();
        
        //motor drivers
        if(!collisionDetected){
          MotorControlUnit(distance,xVal,yVal);
        }else{
          Stop_Moveing();
        }
        // Upload data to server
        if (millis() - lastUploadTime > uploadInterval) {
          uploadDataToServer(xVal, yVal, distance, direction, collision_ON);
          lastUploadTime = millis();
        }
        
      }
      
    }
   
    Serial.println("Kliens lecsatlakozott.");
  }
  
  
  
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

void MotorControlUnit(int distance,int xVal, int yVal){
 
  //Motor Drivers Activate
  if(yVal <= 21 && distance > 8){
    Go_Forward();
    direction = "FORWARD";
  }
  else if(yVal >= 28){
    Go_Backward();
    direction = "BACKWARD";
  }
  else if(xVal <= 21){
    Turn_Right();  
    direction = "RIGHT";      
  }
  else if(xVal >= 30){
    Turn_Left();
    direction = "LEFT";
  }
  else{
    Stop_Moveing();
    direction = "STOP";
  }

}


void Stop_Moveing(){
  //Driver A control
  digitalWrite(DriverA_PortA1A, LOW);
  digitalWrite(DriverA_PortA1B, LOW);

  //Driver B control
  digitalWrite(DriverB_PortA1A, LOW);
  digitalWrite(DriverB_PortA1B, LOW);
  
}

void Go_Forward(){
  //Driver A control
  digitalWrite(DriverA_PortA1A, HIGH);
  digitalWrite(DriverA_PortA1B, LOW);

  //Driver B control
  digitalWrite(DriverB_PortA1A, HIGH);
  digitalWrite(DriverB_PortA1B, LOW);
}

void Go_Backward(){
   //Driver A control
  digitalWrite(DriverA_PortA1A, LOW);
  digitalWrite(DriverA_PortA1B, HIGH);

  //Driver B control
  digitalWrite(DriverB_PortA1A, LOW);
  digitalWrite(DriverB_PortA1B, HIGH);
}

void Turn_Left(){
   //Driver A control
  digitalWrite(DriverA_PortA1A, HIGH);
  digitalWrite(DriverA_PortA1B, LOW);

  //Driver B control
  digitalWrite(DriverB_PortA1A, LOW);
  digitalWrite(DriverB_PortA1B, LOW);
}

void Turn_Right(){
   //Driver A control
  digitalWrite(DriverA_PortA1A, LOW);
  digitalWrite(DriverA_PortA1B, LOW);

  //Driver B control
  digitalWrite(DriverB_PortA1A, HIGH);
  digitalWrite(DriverB_PortA1B, LOW);
}

void Collision() {
  collisionDetected = 
      digitalRead(Switch_Front_Right) == HIGH || 
      digitalRead(Switch_Front_Left) == HIGH || 
      digitalRead(Switch_Front_Center) == HIGH || 
      digitalRead(Switch_Back_Right) == HIGH || 
      digitalRead(Switch_Back_Left) == HIGH || 
      digitalRead(Switch_Back_Center) == HIGH;

  if (collisionDetected) {
    // Stop the motors when a collision is detected
    Stop_Moveing();

    //Set value to 1 if collision is detected
    collision_ON = 1;

    // Activate the emergency light and horn
    digitalWrite(Emergency_Light_and_Horn, HIGH);
    delay(500);
    digitalWrite(Emergency_Light_and_Horn, LOW);
    delay(500);
  } else {
    // Turn off the alarm if there is no collision
    digitalWrite(Emergency_Light_and_Horn, LOW);
    collision_ON = 0;
  }
}

void uploadDataToServer(int x, int y,int distance, String robot_direction, int robot_collision) {
  if (WiFi.status() == WL_CONNECTED) {
    String postData = "xValue=" + String(x) + "&yValue=" + String(y) + "&Obstacle_distance=" + String(distance) + "&Control_direction=" + String(robot_direction) + "&collision=" + String(robot_collision);
   
    HTTPClient http;
    http.begin(URL);

    http.addHeader("Content-Type", "application/x-www-form-urlencoded");
  
  int httpCode = http.POST(postData);
  String payload = "";

  if(httpCode > 0) {
    // file found at server
    if(httpCode == HTTP_CODE_OK) {
      String payload = http.getString();
      Serial.println(payload);
    } else {
      // HTTP header has been send and Server response header has been handled
      Serial.printf("[HTTP] GET... code: %d\n", httpCode);
    }
  } else {
    Serial.printf("[HTTP] GET... failed, error: %s\n", http.errorToString(httpCode).c_str());
  }
  }
}


