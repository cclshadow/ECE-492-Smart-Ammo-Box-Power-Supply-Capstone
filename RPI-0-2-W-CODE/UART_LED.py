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

def send_command(command):
    """Send a command to the Arduino and print the response"""
    ser.write((command + '\n').encode())
    print(f"Sent: {command}")
    
    # Wait for response
    time.sleep(0.1)  # Give Arduino time to process
    
    # Read response if available
    if ser.in_waiting > 0:
        response = ser.readline().decode('utf-8').strip()
        print(f"Received: {response}")

def main_menu():
    """Display the main menu and get user input"""
    print("\nELEGOO LED Control System")
    print("------------------------")
    print("0-9: Turn on specific LED")
    print("a: Turn all LEDs on")
    print("o: Turn all LEDs off")
    print("q: Quit")
    print("------------------------")
    return input("Enter command: ").strip().lower()

try:
    print("Connecting to Arduino Mega 2560...")
    time.sleep(2)  # Give Arduino time to initialize
    
    # Main program loop
    while True:
        command = main_menu()
        
        if command == 'q':
            print("Exiting program...")
            break
        elif command in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'o']:
            send_command(command)
        else:
            print("Invalid command. Please try again.")
        
        time.sleep(0.5)  # Small delay between commands

except KeyboardInterrupt:
    print("\nProgram terminated by user")
except Exception as e:
    print(f"Error: {e}")
finally:
    ser.close()
    print("Serial port closed")