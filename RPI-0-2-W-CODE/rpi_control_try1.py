#!/usr/bin/env python3
import serial
import time
import threading
import queue
import datetime
import RPi.GPIO as GPIO

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

        self.encoder_position = 0

        # Rotary Encoder Setup
        self.encoder_a_pin = 5
        self.encoder_b_pin = 6

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.encoder_a_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.encoder_b_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Attach interrupts to detect rotary encoder movement
        GPIO.add_event_detect(self.encoder_a_pin, GPIO.BOTH, callback=self.encoder_callback)
        GPIO.add_event_detect(self.encoder_b_pin, GPIO.BOTH, callback=self.encoder_callback)

    def encoder_callback(self, channel):
        """Called when encoder position changes"""
        # Read current state of the encoder
        a = GPIO.input(self.encoder_a_pin)
        b = GPIO.input(self.encoder_b_pin)

        # Check the direction of rotation
        if a == b:
            self.encoder_position += 1  # Clockwise rotation
        else:
            self.encoder_position -= 1  # Counter-clockwise rotation

        # Send updated position to Arduino
        self._send_rotary_info()

    def _send_rotary_info(self):
        """Send the rotary encoder position to Arduino"""
        if self.ser.is_open:
            message = f"ROTARYV:{self.encoder_position}\n"
            self.ser.write(message.encode())
            print(f"Sent to Arduino: {message.strip()}")

        
    def start(self):
        # Start the reading thread
        self.read_thread = threading.Thread(target=self._read_serial)
        self.read_thread.daemon = True
        self.read_thread.start()
        
        # Start the command processing thread
        self.command_thread = threading.Thread(target=self._process_commands)
        self.command_thread.daemon = True
        self.command_thread.start()

        # Start the time synchronization thread
        self.time_thread = threading.Thread(target=self._sync_time)
        self.time_thread.daemon = True
        self.time_thread.start()
        
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

    def _sync_time(self):
        """Thread function to send time updates to Arduino"""
        while self.running:
            try:
                if self.ser.is_open:
                    now = datetime.datetime.now()
                    time_str = now.strftime("TIME:%H:%M:%S\n")  # Format: TIME:HH:MM:SS
                    self.ser.write(time_str.encode())
                time.sleep(1)  # Send time update every second
            except Exception as e:
                print(f"Error syncing time: {e}")
                time.sleep(5)

                
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
    controller = ArduinoController(port='/dev/ttyS0')
    
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