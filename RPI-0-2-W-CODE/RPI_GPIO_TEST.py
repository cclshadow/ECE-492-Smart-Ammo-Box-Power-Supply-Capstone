import RPi.GPIO as GPIO
import time

# List of all general-purpose GPIO pins on the Raspberry Pi Zero 2 W
gpio_pins = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27]

def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    for pin in gpio_pins:
        GPIO.setup(pin, GPIO.OUT)

def cleanup_gpio():
    GPIO.cleanup()

def toggle_pins():
    try:
        while True:
            for pin in gpio_pins:
                GPIO.output(pin, GPIO.HIGH)
                print(f"Pin {pin} set HIGH - Press Enter to turn it off")
                input()  # Wait for user input
                
                GPIO.output(pin, GPIO.LOW)
                print(f"Pin {pin} set LOW")
                time.sleep(0.5)  # Small delay before next pin
    except KeyboardInterrupt:
        print("Exiting program")

def main():
    setup_gpio()
    try:
        toggle_pins()
    finally:
        cleanup_gpio()
        print("Cleaned up GPIO settings")

if __name__ == '__main__':
    main()
