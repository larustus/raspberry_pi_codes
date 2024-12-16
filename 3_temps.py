import requests
import board
import adafruit_dht
from w1thermsensor import W1ThermSensor
import time
from datetime import datetime

# Klasa TerrariumLamp
class TerrariumLamp:
    def __init__(self, terrarium_id, dht22_t1=None, dht11_t2=None, ds18b20=None):
        self.terrarium_id = terrarium_id
        self.dht22_t1 = dht22_t1
        self.dht11_t2 = dht11_t2
        self.ds18b20 = ds18b20
        self.hourly_data = []  # Lista przechowująca dane do statystyk

    def get_dht22_readings(self):
        if self.dht22_t1:
            try:
                temp = self.dht22_t1.temperature
                humidity = self.dht22_t1.humidity
                return temp, humidity
            except Exception as e:
                print(f"Error reading from DHT22: {e}")
        return None, None

    def get_dht11_readings(self):
        if self.dht11_t2:
            try:
                temp = self.dht11_t2.temperature
                humidity = self.dht11_t2.humidity
                return temp, humidity
            except Exception as e:
                print(f"Error reading from DHT11: {e}")
        return None, None

    def get_ds18b20_temperature(self):
        if self.ds18b20:
            try:
                temp = self.ds18b20.get_temperature()
                return temp
            except Exception as e:
                print(f"Error reading from DS18B20: {e}")
        return None

    def record_hourly_reading(self, dht22_temp, dht11_temp, dht11_humidity):
        """Zapisuje odczyty do listy przechowującej dane do statystyk."""
        self.hourly_data.append({
            "dht22_temp": dht22_temp,
            "dht11_temp": dht11_temp,
            "humidity": dht11_humidity
        })

    def calculate_and_send_hourly_stats(self, stats_api_url):
        """Oblicza średnie dane z hourly_data i wysyła je na API."""
        if not self.hourly_data:
            print(f"No data to calculate for Terrarium ID {self.terrarium_id}")
            return

        # Obliczenie średnich wartości
        dht22_temps = [data["dht22_temp"] for data in self.hourly_data if data["dht22_temp"] is not None]
        dht11_temps = [data["dht11_temp"] for data in self.hourly_data if data["dht11_temp"] is not None]
        humidities = [data["humidity"] for data in self.hourly_data if data["humidity"] is not None]

        avg_dht22_temp = sum(dht22_temps) / len(dht22_temps) if dht22_temps else 0
        avg_dht11_temp = sum(dht11_temps) / len(dht11_temps) if dht11_temps else 0
        avg_humidity = sum(humidities) / len(humidities) if humidities else 0

        # Przygotowanie danych do wysyłki
        data = {
            "date": datetime.now().date().isoformat(),
            "temperature_1": avg_dht22_temp,
            "temperature_2": avg_dht11_temp,
            "humidity": avg_humidity,
            "terrarium_id": self.terrarium_id,
            "hour": datetime.now().hour
        }

        # Wysłanie danych na API
        try:
            response = requests.post(stats_api_url, json=data)
            if response.status_code == 201:
                print(f"Hourly stats sent successfully for Terrarium ID {self.terrarium_id}.")
            else:
                print(f"Failed to send stats for Terrarium ID {self.terrarium_id}. Status code: {response.status_code}")
                print(f"Response: {response.text}")
        except requests.RequestException as e:
            print(f"Error sending stats for Terrarium ID {self.terrarium_id}: {e}")

        # Wyczyszczenie danych po wysłaniu
        self.hourly_data.clear()

    def send_readings(self, api_url_base):
        """Wysyła aktualne odczyty do API w celu zaktualizowania bieżących wartości."""
        dht22_temp, dht22_humidity = self.get_dht22_readings()
        dht11_temp, dht11_humidity = self.get_dht11_readings()

        params = {
            "current_temperature1": dht22_temp if dht22_temp is not None else 0,
            "current_temperature2": dht11_temp if dht11_temp is not None else 0,
            "current_hum": dht11_humidity if dht11_humidity is not None else 0
        }

        api_url = f"{api_url_base}/update/{self.terrarium_id}"
        try:
            response = requests.put(api_url, params=params)
            if response.status_code == 200:
                print(f"Current readings updated for Terrarium ID {self.terrarium_id}.")
            else:
                print(f"Failed to update readings for Terrarium ID {self.terrarium_id}.")
        except requests.RequestException as e:
            print(f"Error sending current readings for Terrarium ID {self.terrarium_id}: {e}")

# Funkcje pobierania danych
def fetch_terrariums(user_id):
    url = f"http://212.47.71.180:8080/terrariums/user/id/{user_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching terrariums: {e}")
        return []

def fetch_pins(user_id):
    url = f"http://212.47.71.180:8080/pins/pins/{user_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching pins: {e}")
        return []

def lamp_pin_setup(terrarium_id):
    pins = fetch_pins(user_id=1)
    dht22_sensor = None
    dht11_sensor = None
    ds18b20_sensor = None

    for pin in pins:
        if pin["terrarium_id"] == terrarium_id:
            function = pin["function"]
            if function == "t1":
                try:
                    gpio_pin = getattr(board, f"D{pin['id']}")
                    dht22_sensor = adafruit_dht.DHT22(gpio_pin)
                except Exception as e:
                    print(f"Error initializing DHT22: {e}")
            elif function == "t2":
                try:
                    gpio_pin = getattr(board, f"D{pin['id']}")
                    dht11_sensor = adafruit_dht.DHT11(gpio_pin)
                except Exception as e:
                    print(f"Error initializing DHT11: {e}")
            elif function == "3ce1d4433914":
                try:
                    ds18b20_sensor = W1ThermSensor(sensor_id=function)
                except Exception as e:
                    print(f"Error initializing DS18B20: {e}")

    return TerrariumLamp(
        terrarium_id=terrarium_id,
        dht22_t1=dht22_sensor,
        dht11_t2=dht11_sensor,
        ds18b20=ds18b20_sensor
    )

# Główna funkcja
if __name__ == "__main__":
    user_id = 1
    lamp_terrariums = []
    terrariums = fetch_terrariums(user_id)
    stats_api_url = "http://212.47.71.180:8080/readings"
    current_hour = datetime.now().hour

    for terrarium in terrariums:
        if terrarium["name"].lower() == "lampa":
            lamp_terrariums.append(lamp_pin_setup(terrarium["id"]))

    try:
        while True:
            for lamp in lamp_terrariums:
                dht22_temp, dht22_humidity = lamp.get_dht22_readings()
                dht11_temp, dht11_humidity = lamp.get_dht11_readings()
                lamp.record_hourly_reading(dht22_temp, dht11_temp, dht11_humidity)
                lamp.send_readings(api_url_base="http://212.47.71.180:8080/terrariums")

            new_hour = datetime.now().hour
            if new_hour != current_hour:
                for lamp in lamp_terrariums:
                    lamp.calculate_and_send_hourly_stats(stats_api_url)
                current_hour = new_hour

            time.sleep(30)
    except KeyboardInterrupt:
        print("Program zatrzymany.")
