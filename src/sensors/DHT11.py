try:
    import Adafruit_DHT
    ADAFRUIT_AVAILABLE = True
except ImportError:
    ADAFRUIT_AVAILABLE = False
    print("[Warning] Adafruit_DHT library not found — running in simulation mode.")


import random


class DHT11Sensor:
    def __init__(self, car_pin, vent_pin):
        """
        Initialize the DHT11 sensors and GPIO pins.
        :param car_pin: GPIO pin for the car sensor.
        :param vent_pin: GPIO pin for the ventilation system sensor.
        """
        self.car_pin = car_pin
        self.vent_pin = vent_pin

        if ADAFRUIT_AVAILABLE:
            self.sensor = Adafruit_DHT.DHT11
        else:
            self.sensor = None  # mock mode

        # For simulation if Adafruit_DHT is not available
        self._fake_car_temp = 22.0
        self._fake_car_hum = 45.0
        self._fake_vent_temp = 21.0
        self._fake_vent_hum = 47.0

    def read_sensor_data(self, pin):
        """
        Read temperature and humidity from a DHT11 sensor.
        :param pin: The GPIO pin to which the sensor is connected.
        :return: tuple (temperature, humidity) or (None, None) if failed.
        """
        if ADAFRUIT_AVAILABLE:
            humidity, temperature = Adafruit_DHT.read_retry(self.sensor, pin)
            if humidity is not None and temperature is not None:
                return temperature, humidity
            else:
                return None, None
        else:
            # Simulation mode (no Adafruit_DHT installed)
            return self._simulate_fake_data(pin)

    def _simulate_fake_data(self, pin):
        """Generate simulated data for development without hardware."""
        if pin == self.car_pin:
            self._fake_car_temp += random.uniform(-0.2, 0.2)
            self._fake_car_hum += random.uniform(-0.5, 0.5)
            self._fake_car_temp = max(18, min(28, self._fake_car_temp))
            self._fake_car_hum = max(30, min(70, self._fake_car_hum))
            return self._fake_car_temp, self._fake_car_hum
        else:
            self._fake_vent_temp += random.uniform(-0.2, 0.2)
            self._fake_vent_hum += random.uniform(-0.5, 0.5)
            self._fake_vent_temp = max(18, min(28, self._fake_vent_temp))
            self._fake_vent_hum = max(30, min(70, self._fake_vent_hum))
            return self._fake_vent_temp, self._fake_vent_hum
