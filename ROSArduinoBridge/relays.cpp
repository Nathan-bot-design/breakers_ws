#include "Arduino.h"
#include "commands.h"   // ✅ Required for RELAY_* constants
#include "relays.h"

void initRelays() {
  pinMode(RELAY_PUMP_PIN, OUTPUT);
  pinMode(RELAY_VAC_PIN, OUTPUT);
  digitalWrite(RELAY_PUMP_PIN, OFF);
  digitalWrite(RELAY_VAC_PIN, OFF);
}

void handleRelayCommand(char cmd) {
  switch (cmd) {
    case RELAY_PUMP_ON:
      digitalWrite(RELAY_PUMP_PIN, ON);
      Serial.println("Pump ON");
      break;

    case RELAY_PUMP_OFF:
      digitalWrite(RELAY_PUMP_PIN, OFF);
      Serial.println("Pump OFF");
      break;

    case RELAY_VAC_ON:
      digitalWrite(RELAY_VAC_PIN, ON);
      Serial.println("Vacuum ON");
      break;

    case RELAY_VAC_OFF:
      digitalWrite(RELAY_VAC_PIN, OFF);
      Serial.println("Vacuum OFF");
      break;

    default:
      Serial.println("Unknown Relay Command");
      break;
  }
}
