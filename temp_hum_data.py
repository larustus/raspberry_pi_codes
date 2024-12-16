import adafruit_dht
import board
import time
from w1thermsensor import W1ThermSensor
import requests
from datetime import datetime

# Initialize the sensors
dht_device = adafruit_dht.DHT22(board.D17)  # DHT22 on GPIO 17
ds18b20_sensor = W1ThermSensor()

# Terrarium ID
TERRARIUM_ID = 1

# API endpoint
API_URL = "http://212.47.71.180:8080/readings"
print("XD")
try:
    while True:
        # Read data from DHT22
        try:
            temperature_1 = dht_device.temperature
            humidity = dht_device.humidity
            print(f"DHT22 - Temperature: {temperature_1:.2f}°C, Humidity: {humidity:.2f}%")
        except RuntimeError as error:
            print(f"Error reading DHT22: {error}")
            temperature_1 = None
            humidity = None

        # Read data from DS18B20
        try:
            temperature_2 = ds18b20_sensor.get_temperature()
            print(f"DS18B20 - Temperature: {temperature_2:.2f}°C")
        except Exception as error:
            print(f"Error reading DS18B20: {error}")
            temperature_2 = None

        # Get the current timestamp
        current_timestamp = datetime.now().isoformat()

        # Prepare the data payload
        data = {
            "date": current_timestamp,
            "temperature_1": temperature_1,
            "temperature_2": temperature_2,
            "humidity": humidity,
            "terrarium_id": TERRARIUM_ID
        }

        # Send the data to the API
        try:
            response = requests.post(API_URL, json=data)
            if response.status_code == 200 or response.status_code == 201:
                print("Data sent successfully!")
            else:
                print(f"Failed to send data. Status code: {response.status_code}, Response: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error sending data: {e}")

        # Wait 2 seconds before the next reading
        time.sleep(2)

except KeyboardInterrupt:
    print("Program stopped.")
