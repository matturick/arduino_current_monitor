// Get this header from Emonlib repo
#include "EmonLib.h"

// globals
EnergyMonitor emon1;
char receivedChar;
boolean newData = false;

// Setup runs once at start
void setup()
{
  Serial.begin(9600);
  Serial.println("<Arduino is ready>");
  // Usage: current(input pin, calibration)
  // Hard-coded to use input pin 1
  // Calibration 12.6: 12.6 Amps current draw = 1 V over analog input
  // 12.6 is the max current we can measure
  // calibration = (input current / output current) / burden resistor,ohms
  // calibration = (100 / 0.05) / 160 = 12.5
  // Adjusted to 12.6 after some measurement comparisons with a clamp-on digital multimeter
  emon1.current(1, 12.60);    
}

// "loop" always runs repeatedly
// keeps checking for any input across the serial port interface
// if input is received, we perform a measurement
void loop() 
{
  recvOneChar();
  showNewData();
}


void recvOneChar() {
  // if anything comes across the serial interface, perform a measurement
  if (Serial.available() > 0) {
    receivedChar = Serial.read();
    newData = true;
  }
}

void showNewData() {
  if (newData == true) {
    do_measurement();
    newData = false;
  }
}

void do_measurement()
{
  // Irms = Apparent power (in Volt-Amps)
  // 1480 = number of current samples to average
  double Irms = emon1.calcIrms(1480);  

  // Current = Irms*120 Volts (USA residential 120VAC)
  Serial.print(Irms*120.0);     
  Serial.print(" ");
  Serial.println(Irms);
}
