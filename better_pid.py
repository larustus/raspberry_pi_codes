import time
import RPi.GPIO as GPIO
from w1thermsensor import W1ThermSensor
import csv
from datetime import datetime

class PIController:
    def __init__(self, T, L):
        # Obliczanie parametrów według tabeli
        self.Kp = 0.9 * T / L
        self.Ti = L / 0.3
        self.integral = 0.0
        self.previous_time = None

    def compute(self, setpoint, measured_value):
        current_time = time.time()
        error = setpoint - measured_value

        # Obliczenie całki (integral) z uchybu
        if self.previous_time is not None:
            dt = current_time - self.previous_time
            self.integral += error * dt
        else:
            dt = 0

        # Składowe regulatora PI
        P = self.Kp * error
        I = (self.Kp / self.Ti) * self.integral
        output = P + I

        self.previous_time = current_time

        return max(0, min(100, output)), error, P, I

# Funkcja inicjalizująca plik CSV
def initialize_csv(file_path):
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Time (s)", "Temperature (°C)", "Error", "PI Output", "P Component", "I Component"])
    print(f"Plik {file_path} zainicjalizowany.")

# Funkcja zapisująca dane do pliku CSV
def save_to_csv(file_path, elapsed_time, temperature, error, pi_output, P, I):
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([elapsed_time, temperature, error, pi_output, P, I])
    print(f"Zapisano: Czas = {elapsed_time:.1f}s, Temp = {temperature:.2f}°C, Error = {error:.2f}, Output = {pi_output:.2f}%, P = {P:.2f}, I = {I:.2f}")

# Inicjalizacja GPIO
GPIO.setmode(GPIO.BCM)
HEAT_LAMP_PIN = 17  # GPIO pin for heat lamp
GPIO.setup(HEAT_LAMP_PIN, GPIO.OUT)

# Inicjalizacja PWM
pwm = GPIO.PWM(HEAT_LAMP_PIN, 100)  # 100 Hz frequency
pwm.start(100)

# Inicjalizacja DS18B20 Sensor
sensor = W1ThermSensor()

# Parametry systemu i regulatora
T = 900.0  # Stała czasowa procesu
L = 85.0  # Czas opóźnienia procesu
setpoint = 29.0  # Zadana temperatura

pi_controller = PIController(T, L)

# Plik CSV do zapisu danych
csv_file = "pi_temperature_log22_12_T900L85.csv"
initialize_csv(csv_file)

start_time = time.time()  # Czas początkowy programu

try:
    while True:
        # Odczyt temperatury z DS18B20
        try:
            current_temperature = sensor.get_temperature()
        except Exception as e:
            print(f"Error reading temperature: {e}")
            current_temperature = None

        if current_temperature is not None:
            # Oblicz wartość PI oraz dodatkowe informacje
            pi_output, error, P, I = pi_controller.compute(setpoint, current_temperature)

            # Odwrócona logika PWM
            inverted_pwm = 100 - pi_output  # Invert the duty cycle
            pwm.ChangeDutyCycle(inverted_pwm)

            # Obliczenie czasu
            elapsed_time = time.time() - start_time

            # Wyświetlenie danych
            print(f"Time: {elapsed_time:.1f}s, Temp: {current_temperature:.2f}°C, Error: {error:.2f}, "
                  f"PI Output: {pi_output:.2f}%, PWM: {inverted_pwm:.2f}%, P: {P:.2f}, I: {I:.2f}")

            # Zapis do pliku CSV
            save_to_csv(csv_file, elapsed_time, current_temperature, error, pi_output, P, I)

        time.sleep(5)  # Odstęp czasu między iteracjami

except KeyboardInterrupt:
    print("\nStopping...")
finally:
    # Czyszczenie GPIO
    pwm.stop()
    GPIO.cleanup()
    print("GPIO cleaned up.")
