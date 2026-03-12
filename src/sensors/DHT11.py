try:
    import adafruit_dht
    import board
    ADAFRUIT_AVAILABLE = True
except ImportError:
    ADAFRUIT_AVAILABLE = False

import random

class DHT11:

    def __init__(self, car_pin=None, vent_pin=None):
        self.car_pin = car_pin
        self.vent_pin = vent_pin
        self.sensors = {}
        self.test_mode = False

        if ADAFRUIT_AVAILABLE:
            
            if car_pin:
                self._release_gpio(car_pin)

            if vent_pin:
                self._release_gpio(vent_pin)
            
            if car_pin is not None:
                self.sensors['car'] = adafruit_dht.DHT11(board.D4, use_pulseio=False)
            if vent_pin is not None:
                self.sensors['vent'] = adafruit_dht.DHT11(board.D27, use_pulseio=False)
        else:
            self.sensors['car'] = None
            self.sensors['vent'] = None
            self.test_mode = True


        # For simulation
        self._fake_car_temp = 22.0
        self._fake_car_hum = 45.0
        self._fake_vent_temp = 21.0
        self._fake_vent_hum = 47.0

    def read_sensor_data(self, sensor_name):
        if sensor_name not in self.sensors:
            raise ValueError(f"Invalid sensor name: {sensor_name}. Must be 'car' or 'vent'.")

        if ADAFRUIT_AVAILABLE and self.sensors[sensor_name]:
            try:
                temperature = self.sensors[sensor_name].temperature - 2.0 # Value is slightly too high.
                humidity = self.sensors[sensor_name].humidity
                if temperature is not None and humidity is not None:
                    return temperature, humidity
                else:
                    return None, None
            except RuntimeError as err:
                print(f"[Warning] Sensor {sensor_name} read error: {err}")
                return None, None
        else:
            return self._simulate_fake_data(sensor_name)

    def _simulate_fake_data(self, sensor_name):
        if sensor_name == 'car':
            self._fake_car_temp += random.uniform(-0.2, 0.2)
            self._fake_car_hum += random.uniform(-0.5, 0.5)
            self._fake_car_temp = max(18, min(28, self._fake_car_temp))
            self._fake_car_hum = max(30, min(70, self._fake_car_hum))
            return self._fake_car_temp, self._fake_car_hum
        elif sensor_name == 'vent':
            self._fake_vent_temp += random.uniform(-0.2, 0.2)
            self._fake_vent_hum += random.uniform(-0.5, 0.5)
            self._fake_vent_temp = max(18, min(28, self._fake_vent_temp))
            self._fake_vent_hum = max(30, min(70, self._fake_vent_hum))
            return self._fake_vent_temp, self._fake_vent_hum
        else:
            return None, None
        
    def _release_gpio(self, pin):
        try:
            chip = gpiod.Chip("gpiochip0")
            line = chip.get_line(pin)

            # Request and immediately release
            line.request(consumer="dht_cleanup", type=gpiod.LINE_REQ_DIR_IN)
            line.release()

            print(f"[DHT11] Released GPIO{pin}")

        except Exception as e:
            print(f"[DHT11] Could not release GPIO{pin}: {e}")