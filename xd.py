import RPi.GPIO as GPIO
import time

# Pin configuration
GPIO_PIN = 17  # GPIO pin to control

# GPIO setup
GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
GPIO.setup(GPIO_PIN, GPIO.OUT)  # Set GPIO 4 as an output

try:
    # Set GPIO 4 to HIGH (3.3V)
    GPIO.output(GPIO_PIN, GPIO.HIGH)
    print("GPIO 4 is now outputting 3.3V")
    
    # Keep it HIGH indefinitely (or for testing purposes)
    input("Press Enter to exit...")

except KeyboardInterrupt:
    print("Exiting program.")

finally:
    # Clean up GPIO settings
    GPIO.cleanup()
