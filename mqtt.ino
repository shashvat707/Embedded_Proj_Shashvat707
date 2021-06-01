#include <ESP8266WiFi.h> 
#include "Adafruit_MQTT.h" 
#include "Adafruit_MQTT_Client.h" 
#include <BlynkSimpleEsp8266.h>

// Auth token provided by Blynk App
char AUTH[] = "A1QxmouYuLBmCoqac8o3S1Tp3yXrVTXU";

// Wi-Fi Access Point
#define WLAN_SSID       "Taurus" 
#define WLAN_PASS       "zxcvbnm123" 
#define MQTT_SERVER     "192.168.206.105" // Static ip address
#define MQTT_PORT         1883                    
#define MQTT_USERNAME    "" 
#define MQTT_PASSWORD         "" 

/*
 ***Global State*** 
 * Create an ESP8266 Wi-Fi Client class to connect to the MQTT server. 
*/
WiFiClient client; 

/* 
 * Setup the MQTT client class by passing in the WiFi client 
 * and MQTT server and login details. 
*/
Adafruit_MQTT_Client mqtt(&client, MQTT_SERVER, MQTT_PORT, MQTT_USERNAME, MQTT_PASSWORD); 

/* 
 ***Feeds*** 
 * Setup a feed called 'esp8266_temp' for subscribing to changes. 
*/
Adafruit_MQTT_Subscribe esp8266_temp = Adafruit_MQTT_Subscribe(&mqtt, MQTT_USERNAME "temperature"); 

void MQTT_connect();

void setup() {
  Serial.begin(115200); 
  Serial.print("Connecting to "); 
  Serial.println(WLAN_SSID); 

  // Register to Blynk server that uses the Wi-Fi
  Blynk.begin(AUTH, WLAN_SSID, WLAN_PASS);
  
  // Setup MQTT subscription for the "temperature" feed. 
  mqtt.subscribe(&esp8266_temp);  
}

void loop() {
  
  /* 
   * Ensure the connection to the MQTT server is alive (this will make the first 
   * connection and automatically reconnect when disconnected).
  */
  MQTT_connect(); 
  /* 
   * This is our 'wait for incoming subscription packets' busy subloop 
   * try to spend your time here 
   * Here its read the subscription 
  */
  Adafruit_MQTT_Subscribe *subscription; 
  while ((subscription = mqtt.readSubscription())){ 

    if (subscription == &esp8266_temp){ 
      char *message = (char *)esp8266_temp.lastread; 
      Serial.print(F("Got: ")); 
      Serial.println(message);
      Blynk.virtualWrite(V1, String(message).toFloat());
    }
  }
  Blynk.run();
}

// Function to connect and reconnect as necessary to the MQTT server. 
void MQTT_connect() 
{ 
  int8_t ret;

  // Stop if already connected. 
  if (mqtt.connected()){ 
    return; 
  } 
  Serial.print("Connecting to MQTT... "); 
  uint8_t retries = 3; 

  while ((ret = mqtt.connect()) != 0){ 
    
    // Connect will return 0 for connected 
    Serial.println(mqtt.connectErrorString(ret)); 
    Serial.println("Retrying MQTT connection in 5 seconds..."); 
    mqtt.disconnect(); 
    
    delay(5000);  // wait 5 seconds 
    retries--; 
    
    if (retries == 0) { 
      // basically die and wait for WDT to reset me 
      while (1); 
    }
  } 
  Serial.println("MQTT Connected!"); 
} 