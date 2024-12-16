import time
import RPi.GPIO as GPIO
from w1thermsensor import W1ThermSensor
import csv
from datetime import datetime

class PIDController:
    def __init__(self, Kp, Ki, Kd):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.previous_error = 0
        self.integral = 0

    def compute(self, setpoint, current_temperature, dt):
        error = setpoint - current_temperature
        self.integral += error * dt
        derivative = (error - self.previous_error) / dt

        output = (self.Kp * error) + (self.Ki * self.integral) + (self.Kd * derivative)
        self.previous_error = error

        return max(0, min(100, output))

# Funkcja inicjalizująca plik CSV
def initialize_csv(file_path):
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Time (s)", "Temperature (°C)"])
    print(f"Plik {file_path} zainicjalizowany.")

# Funkcja zapisująca dane do pliku CSV
def save_to_csv(file_path, elapsed_time, temperature):
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([elapsed_time, temperature])
    print(f"Zapisano: Czas = {elapsed_time:.1f}s, Temperatura = {temperature:.2f}°C")

# Inicjalizacja GPIO
GPIO.setmode(GPIO.BCM)
HEAT_LAMP_PIN = 17  # GPIO pin for heat lamp
GPIO.setup(HEAT_LAMP_PIN, GPIO.OUT)

# Inicjalizacja PWM
pwm = GPIO.PWM(HEAT_LAMP_PIN, 100)  # 100 Hz frequency
pwm.start(100)

# Inicjalizacja DS18B20 Sensor
sensor = W1ThermSensor()

# Parametry PID
setpoint = 31.0  # Zadana temperatura
dt = 1.0  # Odstęp czasu w sekundach
Kp = 0.139
Ki = 0.1
Kd = 0.0

pid = PIDController(Kp=Kp, Ki=Ki, Kd=Kd)

# Plik CSV do zapisu danych
csv_file = "pid_temperature_data2.csv"
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
            # Oblicz wartość PID
            pid_output = pid.compute(setpoint, current_temperature, dt)

            # Odwrócona logika PWM
            inverted_pwm = 100 - pid_output  # Invert the duty cycle
            pwm.ChangeDutyCycle(inverted_pwm)

            # Obliczenie czasu
            elapsed_time = time.time() - start_time

            # Wyświetlenie danych
            print(f"Time: {elapsed_time:.1f}s, Temp: {current_temperature:.2f}°C, PID Output: {pid_output:.2f}%, PWM: {inverted_pwm:.2f}%")

            # Zapis do pliku CSV
            save_to_csv(csv_file, elapsed_time, current_temperature)

        time.sleep(dt)

except KeyboardInterrupt:
    print("\nStopping...")
finally:
    # Czyszczenie GPIO
    pwm.stop()
    GPIO.cleanup()
    print("GPIO cleaned up.")
