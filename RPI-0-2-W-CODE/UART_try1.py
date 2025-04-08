#!/usr/bin/env python3
import serial
import time

# Configure the serial port
ser = serial.Serial(
    port='/dev/serial0',  # Default serial port on GPIO
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

try:
    while True:
        # Send a message
        message = "Hello Mega 2560!\n"
        ser.write(message.encode())
        print(f"Sent: {message.strip()}")
        
        # Read response
        if ser.in_waiting > 0:
            response = ser.readline().decode('utf-8').strip()
            print(f"Received: {response}")
        
        time.sleep(2)

except KeyboardInterrupt:
    print("Program terminated")
    ser.close()