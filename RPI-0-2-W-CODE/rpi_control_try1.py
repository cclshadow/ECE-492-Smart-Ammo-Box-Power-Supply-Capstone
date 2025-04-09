#!/usr/bin/env python3
import serial
import time
import threading
import queue
import datetime
from gpiozero import RotaryEncoder

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

        # Rotary Encoder Setup
        self.encoder = RotaryEncoder(a=5, b=6, max_steps=127, wrap=False)
        self.encoder.steps = 64  # Start in middle of range
        self.encoder.when_rotated = self._rotary_moved

    def _rotary_moved(self):
        value = max(0, min(127, self.encoder.steps))
        if self.ser.is_open:
            message = f"ROTARYV:{value}\n"
            self.ser.write(message.encode())
            print(f"Sent to Arduino: {message.strip()}")

    def start(self):
        # Start the reading thread
        self.read_thread = threading.Thread(target=self._read_serial, daemon=True)
        self.read_thread.start()

        # Start the command processing thread
        self.command_thread = threading.Thread(target=self._process_commands, daemon=True)
        self.command_thread.start()

        # Start the time synchronization thread
        self.time_thread = threading.Thread(target=self._sync_time, daemon=True)
        self.time_thread.start()

    def stop(self):
        self.running = False
        if hasattr(self, 'ser'):
            self.ser.close()

    def reconnect(self):
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
        while self.running:
            try:
                if not self.ser.is_open and not self.reconnect():
                    time.sleep(5)
                    continue

                if self.ser.in_waiting:
                    line = self.ser.readline().decode('utf-8').strip()
                    if line:
                        self._process_reading(line)
            except Exception as e:
                print(f"Error reading serial: {e}")
                time.sleep(1)

    def _process_reading(self, line):
        now = datetime.datetime.now().strftime('%H:%M:%S')
        try:
            if line.startswith("Voltage:"):
                self.last_voltage = float(line.split(":")[1].strip().split(" ")[0])
            elif line.startswith("Current:"):
                self.last_current = float(line.split(":")[1].strip().split(" ")[0])
            elif line.startswith("Temperature:"):
                self.last_temperature = float(line.split(":")[1].strip().split(" ")[0])
            print(f"[{now}] {line}")
        except ValueError:
            print(f"[{now}] Error parsing line: {line}")

    def _process_commands(self):
        while self.running:
            try:
                if not self.command_queue.empty():
                    if not self.ser.is_open and not self.reconnect():
                        time.sleep(5)
                        continue

                    command = self.command_queue.get()
                    self.ser.write((command + '\n').encode())
                    time.sleep(0.1)
            except Exception as e:
                print(f"Error processing command: {e}")
                time.sleep(1)

    def _sync_time(self):
        while self.running:
            try:
                if self.ser.is_open:
                    now = datetime.datetime.now()
                    time_str = now.strftime("TIME:%H:%M:%S\n")
                    self.ser.write(time_str.encode())
                time.sleep(1)
            except Exception as e:
                print(f"Error syncing time: {e}")
                time.sleep(5)

    def send_command(self, command):
        self.command_queue.put(command)

    def get_sensor_data(self):
        return {
            'voltage': self.last_voltage,
            'current': self.last_current,
            'temperature': self.last_temperature
        }

def main():
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
