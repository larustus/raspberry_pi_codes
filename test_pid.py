import time
from w1thermsensor import W1ThermSensor
import csv
from datetime import datetime

# Ścieżka do pliku CSV
output_file = "ds18b20_readings.csv"

# Funkcja zapisująca nagłówki do pliku (jeśli jeszcze nie istnieją)
def initialize_csv(file_path):
    try:
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Nagłówki kolumn
            writer.writerow(["Timestamp", "Temperature"])
        print(f"Plik {file_path} został zainicjalizowany.")
    except Exception as e:
        print(f"Błąd przy inicjalizacji pliku: {e}")

# Funkcja zapisująca odczyty do pliku
def save_reading_to_csv(file_path, timestamp, temperature):
    try:
        with open(file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, temperature])
        print(f"Zapisano: {timestamp}, {temperature:.2f}°C")
    except Exception as e:
        print(f"Błąd przy zapisie do pliku: {e}")

# Inicjalizacja pliku CSV
initialize_csv(output_file)

# Inicjalizacja sensora DS18B20
sensor = W1ThermSensor()

print("Rozpoczynamy odczyty z DS18B20...")
try:
    while True:
        try:
            # Pobranie temperatury
            temperature = sensor.get_temperature()
            # Aktualny czas
            timestamp = datetime.now().isoformat()
            # Zapis odczytu do pliku
            save_reading_to_csv(output_file, timestamp, temperature)
        except Exception as e:
            print(f"Błąd przy odczycie z sensora: {e}")
        
        # Odczekanie 2 sekund przed kolejnym odczytem
        time.sleep(2)

except KeyboardInterrupt:
    print("Zatrzymano odczytywanie temperatur.")

