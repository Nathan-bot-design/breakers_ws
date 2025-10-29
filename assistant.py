import serial
import time
import os

# --- Serial setup (Arduino connection) ---
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)  # Change port if different
time.sleep(2)  # Give Arduino time to reset

print("Assistant is running... waiting for sound triggers")

# --- Main loop ---
while True:
    if ser.in_waiting > 0:
        data = ser.readline().decode('utf-8').strip()
        print(f"Received: {data}")

        if data == "hello_detected":
            print("Trigger recognized! Playing response audio...")
            os.system("aplay /home/limitbreakers/breakers_ws/hello_response_loud.wav")
