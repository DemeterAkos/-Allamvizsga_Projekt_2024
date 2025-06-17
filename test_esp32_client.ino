#include <WiFi.h> 

// Wi-Fi AP adatok
const char* ssid = "ESP32-AccesPoint";
const char* password = "12345678";
const char* host = "192.168.4.1"; // Robot IP-address (AP)

// Inicializálás
const int comm_LED = 25; 
const int in_X = 34;
const int in_Y = 35;
const int in_Z = 32;

const int FILTER_SIZE = 3;  // Mozgó átlag szűrő mérete
int x_values[FILTER_SIZE] = {0};
int y_values[FILTER_SIZE] = {0};
int z_values[FILTER_SIZE] = {0};
int filter_index = 0;

struct SensorData {
  int x;
  int y;
  int z;
};

WiFiClient client;

void setup() {
  Serial.begin(115200);

  pinMode(in_X, INPUT);
  pinMode(in_Y, INPUT);
  pinMode(in_Z, INPUT);
  pinMode(comm_LED, OUTPUT);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    digitalWrite(comm_LED, LOW);
    delay(200);
    digitalWrite(comm_LED, HIGH);
    delay(200);
    Serial.println("Csatlakozás a Wi-Fi-hez...");
  }
  Serial.println("Csatlakozva!");

  if (client.connect(host, 80)) {
    Serial.println("Csatlakozva a robot szerverhez.");
    digitalWrite(comm_LED, HIGH);
  } else {
    Serial.println("Nem sikerült csatlakozni.");
    digitalWrite(comm_LED, LOW);
  }
}

int moving_average(int* values) {
  int sum = 0;
  for (int i = 0; i < FILTER_SIZE; i++) {
    sum += values[i];
  }
  return sum / FILTER_SIZE;
}

void loop() {
  SensorData data;
  data.x = analogRead(in_X);
  data.y = analogRead(in_Y);
  data.z = analogRead(in_Z);

  // Frissítjük a mozgó átlag szűrőt
  x_values[filter_index] = data.x;
  y_values[filter_index] = data.y;
  z_values[filter_index] = data.z;
  filter_index = (filter_index + 1) % FILTER_SIZE;

  // Szűrt értékek kiszámítása
  int filteredX = moving_average(x_values);
  int filteredY = moving_average(y_values);
  int filteredZ = moving_average(z_values);

  // Skálázás (0-4095 -> 0-50)
  int scaledX = map(filteredX, 0, 4095, 0, 100);
  int scaledY = map(filteredY, 0, 4095, 0, 100);
  int scaledZ = map(filteredZ, 0, 4095, 0, 100);

  // Küldés Wi-Fi-n keresztül
  if (client.connected()) {
    String data_to_send = String(scaledX) + "," + String(scaledY) + "," + String(scaledZ);
    client.println(data_to_send);
    Serial.println("Küldött adat: " + data_to_send);
  } else {
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
