#!/usr/bin/env python3
"""
Raspberry Pi Zero 2 W LED Control Program
This program communicates with an Arduino Mega via UART to control LEDs on pins 22-31.
"""

import serial
import time
import sys

# UART configuration
# Try different UART ports in case default is not available
SERIAL_PORTS = ['/dev/ttyAMA0', '/dev/ttyS0', '/dev/serial0']  # Common UART ports on Raspberry Pi
BAUD_RATE = 9600

# Function to find available serial port
def find_serial_port():
    for port in SERIAL_PORTS:
        try:
            ser = serial.Serial(port, BAUD_RATE)
            ser.close()
            return port
        except:
            continue
    return None

SERIAL_PORT = find_serial_port()
if not SERIAL_PORT:
    print("Error: No available UART ports found")
    print("Please check:")
    print("1. UART is enabled in raspi-config")
    print("2. User has permission to access serial ports") 
    print("3. No other program is using the serial port")
    sys.exit(1)

def setup_serial():
    """Initialize the serial connection to the Arduino."""
    try:
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUD_RATE,
            timeout=1
        )
        print(f"Connected to {SERIAL_PORT} at {BAUD_RATE} baud")
        return ser
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        sys.exit(1)

def send_command(ser, command):
    """Send a command to the Arduino and wait for a response."""
    try:
        # Send the command with a newline character
        ser.write(f"{command}\n".encode())
        
        # Wait for a response (with timeout)
        response = ""
        start_time = time.time()
        while time.time() - start_time < 2.0:  # 2 second timeout
            if ser.in_waiting:
                response += ser.read(ser.in_waiting).decode()
                if '\n' in response:
                    break
            time.sleep(0.01)
        
        # Print the response
        if response:
            print(f"Response: {response.strip()}")
        else:
            print("No response received")
            
    except Exception as e:
        print(f"Error sending command: {e}")

def print_menu():
    """Display the command menu."""
    print("\n===== LED Control Menu =====")
    print("0-9: Turn on specific LED (0-9)")
    print("a  : Turn all LEDs on")
    print("o  : Turn all LEDs off")
    print("q  : Quit")
    print("===========================")

def main():
    """Main program loop."""
    ser = setup_serial()
    
    # Wait for Arduino to initialize
    time.sleep(2)
    
    # Clear any existing data
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    
    print_menu()
    
    while True:
        command = input("Enter command: ").strip().lower()
        
        if command == 'q':
            print("Exiting program")
            break
        elif command in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'o']:
            send_command(ser, command)
        else:
            print("Invalid command. Please try again.")
            print_menu()
    
    ser.close()

if __name__ == "__main__":
    main()