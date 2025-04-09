#!/usr/bin/env python3
import serial
import time
import threading
import queue
import datetime

class ArduinoController:
    def __init__(self, port='/dev/ttyS0', baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.ser = serial.Serial(port, baudrate, timeout=1)
        self.command_queue = queue.Queue()
        self.running = True
        self.last_voltage = 0.0
        self.last_current = 0.0
        self.last_temperature = 0.0
        
    def start(self):
        # Start the reading thread
        self.read_thread = threading.Thread(target=self._read_serial)
        self.read_thread.daemon = True
        self.read_thread.start()
        
        # Start the command processing thread
        self.command_thread = threading.Thread(target=self._process_commands)
        self.command_thread.daemon = True
        self.command_thread.start()
        
    def stop(self):
        self.running = False
        if hasattr(self, 'ser'):
            self.ser.close()
            
    def reconnect(self):
        """Attempt to reconnect to the serial port"""
        try:
            if hasattr(self, 'ser'):
                self.ser.close()
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            print("Serial port reconnected")
            return True
        except Exception as e:
            print(f"Reconnection failed: {e}")
            return False
            
    def _read_serial(self):
        """Thread function to continuously read from serial port"""
        while self.running:
            try:
                if not self.ser.is_open:
                    print("Serial port is closed. Attempting to reconnect...")
                    if not self.reconnect():
                        time.sleep(5)  # Wait before retrying
                        continue
                        
                if self.ser.in_waiting:
                    line = self.ser.readline().decode('utf-8').strip()
                    if line:
                        self._process_reading(line)
            except Exception as e:
                print(f"Error reading serial: {e}")
                time.sleep(1)
                
    def _process_reading(self, line):
        """Process incoming serial data"""
        if line.startswith("Voltage:"):
            try:
                self.last_voltage = float(line.split(":")[1].strip().split(" ")[0])
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {line}")
            except ValueError:
                print(f"Error parsing voltage: {line}")
        elif line.startswith("Current:"):
            try:
                self.last_current = float(line.split(":")[1].strip().split(" ")[0])
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {line}")
            except ValueError:
                print(f"Error parsing current: {line}")
        elif line.startswith("Temperature:"):
            try:
                self.last_temperature = float(line.split(":")[1].strip().split(" ")[0])
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {line}")
            except ValueError:
                print(f"Error parsing temperature: {line}")
        else:
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {line}")
            
    def _process_commands(self):
        """Thread function to process command queue"""
        while self.running:
            try:
                if not self.command_queue.empty():
                    if not self.ser.is_open:
                        print("Serial port is closed. Attempting to reconnect...")
                        if not self.reconnect():
                            time.sleep(5)  # Wait before retrying
                            continue
                            
                    command = self.command_queue.get()
                    self.ser.write((command + '\n').encode())
                    time.sleep(0.1)  # Small delay between commands
            except Exception as e:
                print(f"Error processing command: {e}")
                time.sleep(1)
                
    def send_command(self, command):
        """Add a command to the queue"""
        self.command_queue.put(command)
        
    def get_sensor_data(self):
        """Get the latest sensor readings"""
        return {
            'voltage': self.last_voltage,
            'current': self.last_current,
            'temperature': self.last_temperature
        }

def main():
    # Initialize the controller
    controller = ArduinoController(port='/dev/serial0')
    
    try:
        controller.start()
        print("Arduino Controller Started")
        print("\nAvailable commands:")
        print("0-49: Turn on specific LED")
        print("a: Turn all LEDs on")
        print("o: Turn all LEDs off")
        print("v: Read voltage")
        print("c: Read current")
        print("t: Read temperature")
        print("q: Quit")
        
        while True:
            command = input("\nEnter command: ").strip()
            if command.lower() == 'q':
                break
                
            # Validate LED number command
            if command.isdigit():
                led_num = int(command)
                if led_num < 0 or led_num > 49:
                    print("Invalid LED number. Must be between 0 and 49.")
                    continue
                    
            controller.send_command(command)
            
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        controller.stop()

if __name__ == "__main__":
    main()