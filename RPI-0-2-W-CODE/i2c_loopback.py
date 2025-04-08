import smbus
import time

# Initialize I2C bus
bus = smbus.SMBus(1)  # Use 1 for Raspberry Pi Zero 2 W
address = 0x00  # Loopback address0

# Send and receive data
try:
    print("Starting I2C loopback test...")
    print("Sending test data...")
    bus.write_byte(address, 0x01)  # Sending byte data
    time.sleep(1)
    data = bus.read_byte(address)  # Reading byte data
    print(f"Received data: {data}")
    
    # Test with different values
    test_values = [0x00, 0xFF, 0x55, 0xAA]
    for value in test_values:
        print(f"\nTesting with value: 0x{value:02X}")
        bus.write_byte(address, value)
        time.sleep(0.5)
        received = bus.read_byte(address)
        print(f"Sent: 0x{value:02X}, Received: 0x{received:02X}")
        
except Exception as e:
    print(f"Error: {e}")
