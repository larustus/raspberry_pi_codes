import adafruit_dht
import board
import time
from w1thermsensor import W1ThermSensor

# Initialize the DHT22 sensor
dht_device = adafruit_dht.DHT22(board.D17)  # DHT22 on GPIO 17

# Initialize the DS18B20 sensor
ds18b20_sensor = W1ThermSensor()

try:
    while True:
        # Read data from the DHT22
        try:
            temperature_dht22 = dht_device.temperature
            humidity = dht_device.humidity
            print(f"DHT22 - Temperature: {temperature_dht22:.2f}°C, Humidity: {humidity:.2f}%")
        except RuntimeError as error:
            print(f"Error reading DHT22: {error}")

        # Read data from the DS18B20
        try:
            for sensor in W1ThermSensor.get_available_sensors():
                temperature_ds18b20 = sensor.get_temperature()
                print(f"DS18B20 - Temperature: {temperature_ds18b20:.2f}°C (Sensor ID: {sensor.id})")
        except Exception as error:
            print(f"Error reading DS18B20: {error}")

        print("-" * 40)  # Separator for readability
        time.sleep(2)  # Wait 2 seconds before the next reading

except KeyboardInterrupt:
    print("Program stopped.")
