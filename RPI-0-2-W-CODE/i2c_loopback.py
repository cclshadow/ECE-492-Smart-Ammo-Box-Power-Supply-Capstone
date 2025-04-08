import smbus
import time

# Initialize I2C bus
bus = smbus.SMBus(1)  # Use 1 for Raspberry Pi Zero 2 W
address = 0x08  # Use a valid address or a loopback address

# Send and receive data
try:
    print("Sending data...")
    bus.write_byte(address, 0x01)  # Sending byte data
    time.sleep(1)
    data = bus.read_byte(address)  # Reading byte data
    print(f"Received data: {data}")
except Exception as e:
    print(f"Error: {e}")
