#include <SoftwareSerial.h>
#include "SD.h"
#include <Wire.h>
#include "RTClib.h"

// Define the Real Time Clock object
RTC_PCF8523 RTC;

#define RX 6 
#define TX 7 
SoftwareSerial linkSerial(RX, TX);  // RX, TX

// Logging file on SD card
File logfile;

// For the data logging shield, we are using digital pin 10 for the SD cs line
const int chipSelect = 10;

#define ECHO_TO_SERIAL   0          // echo data to serial port.

void setup() {

    // Initialize Serial port
    Serial.begin(9600);

    // Initialize the "link" serial port
    // Using the lowest possible data rate to reduce error ratio
    linkSerial.begin(9600);

    while (!Serial){
        continue;
    }
    
    initSDcard();                  // Initialize the SD card
    createFile();                  // Create the log file. File incremented every time to get a new file
    initRTC();                     // Initialize the RTC
  
   /*
      The data is in CSV (comma separated value) format and the headers are: "millis, datetime, temp" the first item millis is milliseconds since the Arduino started,
      stamp is the timestamp, datetime is the time and date from the RTC in human readable format, temp is the max temp received from Rpi.
    */
    logfile.println("millis, datetime, temp");
}

void loop() {

    if (linkSerial.available() > 0){

        // Get the new temperature on UART from RPi delimited by the '\n'
        String data = linkSerial.readStringUntil('\n');
        Serial.print("RX sent me: ");
        Serial.println(data);
        
        /*
           Starts logging data
           Logs milliseconds since start
        */
        uint32_t m = millis();
        
        // log the millisec
        logfile.print(m);           //-> Milliseconds since start

        // Fetches the time
        DateTime now = RTC.now();

        // Log the RTC time
        logfile.print(", ");
        logfile.print(now.year(), DEC);
        logfile.print("/");
        logfile.print(now.month(), DEC);
        logfile.print("/");
        logfile.print(now.day(), DEC);
        logfile.print(" ");
        logfile.print(now.hour(), DEC);
        logfile.print(":");
        logfile.print(now.minute(), DEC);
        logfile.print(":");
        logfile.print(now.second(), DEC);
        
        //Stores Temperature Data
        logfile.print(", ");
        logfile.println(data);
        logfile.flush();
    }
}

// Initialize the SD card
void initSDcard() {
  Serial.print("Initializing SD card:");
  pinMode(chipSelect, OUTPUT);

  if (!SD.begin(chipSelect)) {             //-> Checks if card is present and can be initialized
    Serial.println("");
    return;
  }
  Serial.println("");
}

/* 
   Create the log file.
   The file names are named as FLOGxy.CSV. xy increments for every time new log file is created
*/
void createFile() {

  //file name must be in 8.3 format (name length at most 8 characters, follwed by a '.' and then a three character extension.
  char filename[] = "FLOG00.CSV";

  for (uint8_t i = 0; i < 100; i++) {
    filename[4] = i / 10 + '0';
    filename[5] = i % 10 + '0';

    if (! SD.exists(filename)) {
      logfile = SD.open(filename, FILE_WRITE);
      break;
    }
  }
  if (! logfile) {
    error("NoFile");
  }
  Serial.print("Log to: ");
  Serial.println(filename);
}

/*
   If couldn't write data to SD card or open it
   Prints out the error to the Serial Monitor, and then sits in a while(1);
   Forever Loop also known as a halt
*/
void error(char const *str) {

    Serial.print("err:");
    Serial.println(str);
    while (1);
}

// Initialize the RTC
void initRTC() {

    Wire.begin();
    if (!RTC.begin())
    {
        logfile.println("RTC failed");
        #if ECHO_TO_SERIAL
            Serial.println("RTC failed");
        #endif                              //ECHO_TO_SERIAL
    }
}