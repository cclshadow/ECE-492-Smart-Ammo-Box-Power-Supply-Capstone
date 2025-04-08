import smbus
import time
import sys

def check_i2c_devices():
    try:
        # List all I2C devices
        import subprocess
        result = subprocess.run(['i2cdetect', '-y', '1'], capture_output=True, text=True)
        print("I2C Devices found:")
        print(result.stdout)
    except Exception as e:
        print(f"Error checking I2C devices: {e}")

# Initialize I2C bus
try:
    print("Initializing I2C bus...")
    bus = smbus.SMBus(1)  # Use 1 for Raspberry Pi Zero 2 W
    address = 0x00  # Loopback address
    
    # Check for I2C devices first
    check_i2c_devices()
    
    print("\nStarting I2C loopback test...")
    print("Sending test data...")
    
    # Try a simple write first
    try:
        bus.write_byte(address, 0x01)
        print("Write successful")
    except Exception as e:
        print(f"Write failed: {e}")
        sys.exit(1)
    
    time.sleep(1)
    
    # Try to read
    try:
        data = bus.read_byte(address)
        print(f"Received data: {data}")
    except Exception as e:
        print(f"Read failed: {e}")
        sys.exit(1)
    
    # Test with different values
    test_values = [0x00, 0xFF, 0x55, 0xAA]
    for value in test_values:
        print(f"\nTesting with value: 0x{value:02X}")
        try:
            bus.write_byte(address, value)
            time.sleep(0.5)
            received = bus.read_byte(address)
            print(f"Sent: 0x{value:02X}, Received: 0x{received:02X}")
        except Exception as e:
            print(f"Error during test with value 0x{value:02X}: {e}")
            
except Exception as e:
    print(f"Critical error: {e}")
    print("\nTroubleshooting tips:")
    print("1. Make sure I2C is enabled (sudo raspi-config)")
    print("2. Check I2C connections")
    print("3. Verify you're running with sudo")
    print("4. Check if i2c-tools is installed (sudo apt-get install i2c-tools)")
