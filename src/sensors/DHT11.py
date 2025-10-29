import Adafruit_DHT

class DHT11Sensor:
    def __init__(self, car_pin, vent_pin):
        """
        Initialize the sensor pins and the sensor type.
        :param car_pin: GPIO pin for the car sensor.
        :param vent_pin: GPIO pin for the ventilation system sensor.
        """
        self.sensor = Adafruit_DHT.DHT11
        self.car_pin = car_pin
        self.vent_pin = vent_pin

    def read_sensor_data(self, pin):
        """
        Read temperature and humidity from a DHT11 sensor.
        :param pin: The GPIO pin to which the sensor is connected.
        :return: tuple (temperature, humidity) or (None, None) if failed.
        """
        humidity, temperature = Adafruit_DHT.read_retry(self.sensor, pin)
        if humidity is not None and temperature is not None:
            return temperature, humidity
        else:
            return None, None
