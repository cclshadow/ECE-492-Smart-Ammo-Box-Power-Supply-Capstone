import smbus
import time

# Initialize I2C bus
bus = smbus.SMBus(1)  # Use 1 for Raspberry Pi Zero 2 W
ARDUINO_ADDRESS = 0x08

def set_led(number):
    if 0 <= number <= 9:
        bus.write_byte(ARDUINO_ADDRESS, number)
        print(f"Sent command to turn on LED {number}")
    else:
        print("Invalid LED number. Must be 0-9")

def request_data():
    try:
        # Request data from Arduino
        data = bus.read_i2c_block_data(ARDUINO_ADDRESS, 0, 20)  # Read up to 20 bytes
        # Convert bytes to string
        message = ''.join([chr(byte) for byte in data if byte != 0])
        print(f"Received from Arduino: {message}")
    except Exception as e:
        print(f"Error reading from Arduino: {e}")

if __name__ == "__main__":
    print("Starting I2C communication test...")
    
    # Example: Cycle through LEDs 0-9
    for led in range(10):
        set_led(led)
        time.sleep(0.5)  # Wait half a second between each LED
        
    # Request data from Arduino
    print("\nRequesting data from Arduino...")
    request_data()