#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>

String URL = "http://192.168.8.100/robot_data/test_data.php";


// Wi-Fi AP settings
const char *ssid = "ESP32-AccesPoint";
const char *password = "12345678";

//// Wi-Fi client settings (for external network connection)
const char *ssidClient = "HUAWEI-Levi";  
const char *passwordClient = "zizifido"; 

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
const int Switch_Front_Right = 32;
const int Switch_Front_Center = 34;
const int Switch_Front_Left = 35;

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
const int Emergency_Light_and_Horn = 19;

//Database server connection switch
const int DB_Server_connection_Switch = 18;


// Collision detection variables
bool collisionDetected = false;
bool collisionDetected_Switch_Front_Left = false;
bool collisionDetected_Switch_Front_Center = false;
bool collisionDetected_Switch_Front_Right = false;
bool collisionDetected_Switch_Back_Left = false;
bool collisionDetected_Switch_Back_Center = false;
bool collisionDetected_Switch_Back_Right = false;

String direction;
int collision_ON = 0;
String collision_switch = "None";

//upload time to database
unsigned long lastUploadTime = 0;
const long uploadInterval = 2000; // 2 sec

//timeout for sensor data
unsigned long lastSensorDataTime = 0;
const long timeoutInterval = 4000;
//Last Values from Client sensor
int lastXVal = 0;
int lastYVal = 0;
int lastZVal = 0;

// Function declarations (prototypes)
int UltrasonicSensor();
void MotorControlUnit(int distance, int xVal, int yVal);
void Stop_Moveing();
void Go_Forward(int pwm_speed);
void Go_Backward(int pwm_speed);
void Turn_Left(int pwm_speed);
void Turn_Right(int pwm_speed);
void Collision();
void uploadDataToServer(int x, int y, int distance, String direction, int collision);

void setup() {
  // Serial communication 
  Serial.begin(115200);

  WiFi.mode(WIFI_AP_STA);
  WiFi.setAutoReconnect(true);
  WiFi.persistent(true);

  

  //Ultrasonic Sensor Pins 
  pinMode(trigPin,OUTPUT);
  pinMode(echoPin,INPUT);

  //Motor Drivers pins initialization
  pinMode(DriverA_PortA1A,OUTPUT);
  pinMode(DriverA_PortA1B,OUTPUT);
  pinMode(DriverB_PortA1A,OUTPUT);
  pinMode(DriverB_PortA1B,OUTPUT);

  // PWM setup for motor drivers
  ledcAttach(DriverA_PortA1A, 5000, 8); // Channel 0, 5kHz, 8-bit resolution
  ledcAttach(DriverA_PortA1B, 5000, 8); // Channel 1
  ledcAttach(DriverB_PortA1A, 5000, 8); // Channel 2
  ledcAttach(DriverB_PortA1B, 5000, 8); // Channel 3


  //Switches initialization
  pinMode(Switch_Front_Right,INPUT);
  pinMode(Switch_Front_Left,INPUT);
  pinMode(Switch_Front_Center,INPUT);
  pinMode(Switch_Back_Right,INPUT);
  pinMode(Switch_Back_Left,INPUT);
  pinMode(Switch_Back_Center,INPUT);

  //Emergency Light and Horn Pin
  pinMode(Emergency_Light_and_Horn,OUTPUT);

  pinMode(DB_Server_connection_Switch, INPUT);

  //Create Access Point 
  WiFi.softAP(ssid, password, 6, 0, 8);
  
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

   //**Párhuzamos szálak (taskok) létrehozása**
  xTaskCreatePinnedToCore(Task_MotorControl, "MotorControlTask", 4096, NULL, 1, NULL, 0);
  xTaskCreatePinnedToCore(Task_UploadData, "UploadDataTask", 4096, NULL, 1, NULL, 1);
}

void loop() {

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Wi-Fi kapcsolat megszakadt! Újracsatlakozás...");
    WiFi.disconnect();
    WiFi.begin(ssidClient, passwordClient);
  }

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

          if (xVal != lastXVal || yVal != lastYVal || zVal != lastZVal) {
            lastSensorDataTime = millis();  
            lastXVal = xVal;
            lastYVal = yVal;
            lastZVal = zVal;
          }

          // print data to serial port
          Serial.print("X: ");
          Serial.println(xVal);
          Serial.print("Y: ");
          Serial.println(yVal);

          vTaskDelay(10);
          
        } else {
          Serial.println("Hibás adatformátum.");
        }
        
      }
      
    }
   
    Serial.println("Kliens lecsatlakozott.");
  }

  
}

//Motor Control Thread
void Task_MotorControl(void *pvParameters) {
  while (1) {
    //Robot Collision function
    Collision();
    
    MotorControlUnit(distance, xVal, yVal);
  
    if (millis() - lastSensorDataTime > timeoutInterval) {
      //Serial.println("Timeout From Data sensor");
      Stop_Moveing();
    }
    vTaskDelay(1);
  }
}

//Database data upload Thread

void Task_UploadData(void *pvParameters) {
  while (1) {
    int Db_switch = digitalRead(DB_Server_connection_Switch);
    Serial.println(Db_switch);
    if (Db_switch == HIGH && (millis() - lastUploadTime > uploadInterval)) {
      uploadDataToServer(xVal, yVal, distance, direction, collision_ON, collision_switch);
      lastUploadTime = millis();
    }
    delay(500); 
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
  if(yVal < 44 && xVal > 44 && xVal < 50 && distance > 30){

    int pwm_speed = map(yVal, 36, 44, 255, 0);  
    pwm_speed = constrain(pwm_speed, 0, 255);

    Go_Forward(pwm_speed);
    direction = "FORWARD";
  }
  else if(yVal > 50 && xVal > 44 && xVal < 50){

    int pwm_speed = map(yVal, 50, 54, 0, 255);  
    pwm_speed = constrain(pwm_speed, 0, 255);

    Go_Backward(pwm_speed);
    direction = "BACKWARD";
  }
  else if(xVal < 44 && yVal > 44 && yVal < 50){

    //int pwm_speed = 240;

    int pwm_speed = map(xVal, 36, 44, 240, 0);  
    pwm_speed = constrain(pwm_speed, 0, 240);

    Turn_Right(pwm_speed);  
    direction = "RIGHT";      
  }
  else if(xVal > 49 && yVal > 44 && yVal < 50){

    //int pwm_speed = 240;
    int pwm_speed = map(xVal, 49, 56, 0, 240);  
    pwm_speed = constrain(pwm_speed, 0, 240);

    Turn_Left(pwm_speed);
    direction = "LEFT";
  }
  else{
    Stop_Moveing();
    direction = "STOP";
  }

}


void Stop_Moveing(){
  // //Driver A control
  // digitalWrite(DriverA_PortA1A, LOW);
  // digitalWrite(DriverA_PortA1B, LOW);

  // //Driver B control
  // digitalWrite(DriverB_PortA1A, LOW);
  // digitalWrite(DriverB_PortA1B, LOW);

  ledcWrite(DriverA_PortA1A, 0);
  ledcWrite(DriverA_PortA1B, 0);
  ledcWrite(DriverB_PortA1A, 0);
  ledcWrite(DriverB_PortA1B, 0);
  
}

void Go_Forward(int pwm_speed){
  // //Driver A control
  // digitalWrite(DriverA_PortA1A, HIGH);
  // digitalWrite(DriverA_PortA1B, LOW);

  // //Driver B control
  // digitalWrite(DriverB_PortA1A, HIGH);
  // digitalWrite(DriverB_PortA1B, LOW);
  ledcWrite(DriverA_PortA1A, pwm_speed);
  ledcWrite(DriverA_PortA1B, 0);
  ledcWrite(DriverB_PortA1A, pwm_speed);
  ledcWrite(DriverB_PortA1B, 0);
}

void Go_Backward(int pwm_speed){
  //  //Driver A control
  // digitalWrite(DriverA_PortA1A, LOW);
  // digitalWrite(DriverA_PortA1B, HIGH);

  // //Driver B control
  // digitalWrite(DriverB_PortA1A, LOW);
  // digitalWrite(DriverB_PortA1B, HIGH);
  ledcWrite(DriverA_PortA1A, 0);
  ledcWrite(DriverA_PortA1B, pwm_speed);
  ledcWrite(DriverB_PortA1A, 0);
  ledcWrite(DriverB_PortA1B, pwm_speed);
}

void Turn_Left(int pwm_speed){
  //  //Driver A control
  // digitalWrite(DriverA_PortA1A, HIGH);
  // digitalWrite(DriverA_PortA1B, LOW);

  // //Driver B control
  // digitalWrite(DriverB_PortA1A, LOW);
  // digitalWrite(DriverB_PortA1B, LOW);
  ledcWrite(DriverA_PortA1A, pwm_speed);
  ledcWrite(DriverA_PortA1B, 0);
  ledcWrite(DriverB_PortA1A, 0);
  ledcWrite(DriverB_PortA1B, 0);
}

void Turn_Right(int pwm_speed){
  //  //Driver A control
  // digitalWrite(DriverA_PortA1A, LOW);
  // digitalWrite(DriverA_PortA1B, LOW);

  // //Driver B control
  // digitalWrite(DriverB_PortA1A, HIGH);
  // digitalWrite(DriverB_PortA1B, LOW);
  ledcWrite(DriverA_PortA1A, 0);
  ledcWrite(DriverA_PortA1B, 0);
  ledcWrite(DriverB_PortA1A, pwm_speed);
  ledcWrite(DriverB_PortA1B, 0);
}

void Collision() {
  collisionDetected_Switch_Front_Right = digitalRead(Switch_Front_Right);
  collisionDetected_Switch_Front_Left = digitalRead(Switch_Front_Left);
  collisionDetected_Switch_Front_Center = digitalRead(Switch_Front_Center);
  collisionDetected_Switch_Back_Right = digitalRead(Switch_Back_Right);
  collisionDetected_Switch_Back_Left = digitalRead(Switch_Back_Left);
  collisionDetected_Switch_Back_Center = digitalRead(Switch_Back_Center);
 
  if (collisionDetected_Switch_Front_Right || collisionDetected_Switch_Front_Left || collisionDetected_Switch_Front_Center ||
   collisionDetected_Switch_Back_Right || collisionDetected_Switch_Back_Left || collisionDetected_Switch_Back_Center) {

    // Stop the motors when a collision is detected
    //Stop_Moveing();

    //Set value to 1 if collision is detected
    collision_ON = 1;
    collisionDetected = true;

    if (collisionDetected_Switch_Front_Right) {
      collision_switch = "Front RIGHT Switch";
    }
    else if(collisionDetected_Switch_Front_Left){
      collision_switch = "Front LEFT Switch";
    }
    else if(collisionDetected_Switch_Front_Center){
      collision_switch = "Front CENTER Switch";
    }
    else if(collisionDetected_Switch_Back_Right){
      collision_switch = "Back RIGHT Switch";
    }
    else if(collisionDetected_Switch_Back_Left){
      collision_switch = "Back LEFT Switch";
    }
    else if(collisionDetected_Switch_Back_Center){
      collision_switch = "Back CENTER Switch";
    }
    else{
      collision_switch = "None";
    }

    // Activate the emergency light and horn
    digitalWrite(Emergency_Light_and_Horn, HIGH);
    delay(500);
    digitalWrite(Emergency_Light_and_Horn, LOW);
    delay(500);
  } else {
    // Turn off the alarm if there is no collision
    digitalWrite(Emergency_Light_and_Horn, LOW);
    collision_ON = 0;
    collisionDetected = false;
    collision_switch = "None";
  }
}

void uploadDataToServer(int x, int y,int distance, String robot_direction, int robot_collision, String collision_switch) {
  if (WiFi.status() == WL_CONNECTED) {
    String postData = "xValue=" + String(x) + "&yValue=" + String(y) + "&Obstacle_distance=" + String(distance) + "&Control_direction=" + String(robot_direction) + "&collision=" + String(robot_collision) + "&collision_switch=" + String(collision_switch);
   
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