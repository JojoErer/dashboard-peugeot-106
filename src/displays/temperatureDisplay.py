from src.sensors.DHT11 import DHT11Sensor
from clockDisplay import Clock

class SensorOverlay:
    def __init__(self, car_pin, vent_pin, clock):
        # Initialize the sensor and clock
        self.sensor_system = DHT11Sensor(car_pin, vent_pin)
        self.clock = clock

    def update_sensor_data(self):
        """
        Read the sensor data from the car sensor and update the clock with the data.
        This will be called periodically to refresh the display.
        """
        # Read data from the car sensor
        car_temp, car_humidity = self.sensor_system.read_sensor_data(self.sensor_system.car_pin)
        
        if car_temp is not None and car_humidity is not None:
            # Overlay the temperature and humidity on the clock
            self.overlay_temperature_and_humidity(car_temp, car_humidity)
        
        # Schedule the next update in 60 seconds (60000 milliseconds)
        self.clock.root.after(60000, self.update_sensor_data)

    def overlay_temperature_and_humidity(self, temp, humidity):
        """
        Overlay the temperature and humidity on the clock display.
        """
        text = f"Temp: {temp}°C, Humidity: {humidity}%"
        # Overlay the text on the clock at a specific position
        self.clock.canvas.create_text(self.clock.origin_x, self.clock.origin_y + 250, 
                                      text=text, font=("Arial", 20), fill="white")
