import RPi.GPIO as GPIO
import time

# Pin configuration
GPIO_PIN = 4  # GPIO pin connected to the pump

# GPIO setup
GPIO.setmode(GPIO.BCM)  # Use BCM numbering
GPIO.setup(GPIO_PIN, GPIO.OUT)  # Set the pin as an output

try:
    while True:
        # Set pin to LOW (turn pump ON)
        GPIO.output(GPIO_PIN, GPIO.LOW)
        print("Pump ON (LOW)")
        time.sleep(10)  # Wait for 10 seconds

        # Set pin to HIGH (turn pump OFF)
        GPIO.output(GPIO_PIN, GPIO.HIGH)
        print("Pump OFF (HIGH)")
        time.sleep(10)  # Wait for 10 seconds

except KeyboardInterrupt:
    print("Stopping script...")

finally:
    # Cleanup GPIO settings before exiting
    GPIO.cleanup()
