import smbus
import time
import sys
import os

def check_i2c_setup():
    print("Checking I2C setup...")
    
    # Check if I2C device exists
    if not os.path.exists('/dev/i2c-1'):
        print("ERROR: /dev/i2c-1 device not found!")
        print("Please enable I2C in raspi-config")
        return False
        
    # Check permissions
    try:
        with open('/dev/i2c-1', 'r') as f:
            print("I2C device is readable")
    except PermissionError:
        print("ERROR: Permission denied accessing I2C device")
        print("Try running with sudo")
        return False
    except Exception as e:
        print(f"ERROR accessing I2C device: {e}")
        return False
        
    return True

def check_i2c_devices():
    try:
        # List all I2C devices
        import subprocess
        result = subprocess.run(['i2cdetect', '-y', '1'], capture_output=True, text=True)
        print("I2C Devices found:")
        print(result.stdout)
    except Exception as e:
        print(f"Error checking I2C devices: {e}")

# Main program
try:
    print("Starting I2C diagnostics...")
    
    # First check I2C setup
    if not check_i2c_setup():
        sys.exit(1)
    
    print("\nInitializing I2C bus...")
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
    print("5. Try rebooting the Raspberry Pi")
    print("6. Check if the I2C kernel module is loaded (lsmod | grep i2c)")
