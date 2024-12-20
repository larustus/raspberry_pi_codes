import time
import csv
import RPi.GPIO as GPIO
from w1thermsensor import W1ThermSensor

# Ustawienia GPIO i PWM
HEAT_LAMP_PIN = 17  # GPIO pin dla lampy grzewczej
GPIO.setmode(GPIO.BCM)
GPIO.setup(HEAT_LAMP_PIN, GPIO.OUT)

# Inicjalizacja PWM
pwm = GPIO.PWM(HEAT_LAMP_PIN, 100)  # Częstotliwość 100 Hz
pwm.start(0)  # Startujemy z 0% mocy

# Ustawienie 100% mocy
pwm.ChangeDutyCycle(0)  # Odwrócona logika: 0 = 100% mocy

# Inicjalizacja DS18B20
sensor = W1ThermSensor()

# Ścieżka do pliku CSV
csv_file = "temperature_100_percent_power.csv"

# Inicjalizacja pliku CSV
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Time (s)", "Temperature (°C)"])
    print(f"Plik {csv_file} został utworzony.")

# Rozpoczęcie eksperymentu
start_time = time.time()
try:
    while True:
        # Odczyt temperatury
        try:
            temperature = sensor.get_temperature()
        except Exception as e:
            print(f"Error reading temperature: {e}")
            temperature = None

        # Odczyt czasu od początku eksperymentu
        elapsed_time = time.time() - start_time

        # Zapis do pliku CSV
        if temperature is not None:
            with open(csv_file, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([elapsed_time, temperature])
            print(f"Czas: {elapsed_time:.2f}s, Temperatura: {temperature:.2f}°C")

        # Czekamy 1 sekundę przed kolejnym odczytem
        time.sleep(1)

except KeyboardInterrupt:
    print("\nZatrzymano eksperyment.")

finally:
    # Czyszczenie GPIO
    pwm.stop()
    GPIO.cleanup()
    print("GPIO cleaned up.")
