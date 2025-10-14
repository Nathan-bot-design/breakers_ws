#ifndef RELAYS_H
#define RELAYS_H

#include "Arduino.h"

#define RELAY_PUMP_PIN 4
#define RELAY_VAC_PIN  8

#define ON HIGH
#define OFF LOW

void initRelays();
void handleRelayCommand(char cmd);

#endif
