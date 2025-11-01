try:
    import RPi.GPIO as GPIO
except ImportError:
    RPI_AVAILABLE = False
    print("[Warning] RPI not found — running in simulation mode.")
import time

class LightSensor:
    def __init__(self, pin1=22, pin2=27):
        """
        Initializes the two light sensors.
        :param pin1: The GPIO pin where the first light sensor is connected (default is GPIO17).
        :param pin2: The GPIO pin where the second light sensor is connected (default is GPIO27).
        """
        self.pin1 = pin1
        self.pin2 = pin2
        GPIO.setmode(GPIO.BCM)  # Use Broadcom pin-numbering scheme
        GPIO.setup(self.pin1, GPIO.IN)  # Set GPIO pin1 as input
        GPIO.setup(self.pin2, GPIO.IN)  # Set GPIO pin2 as input
    
    def read_light_intensity(self, pin):
        """
        Reads the light intensity (0 or 1) from a given pin.
        :param pin: The GPIO pin to read the value from (either pin1 or pin2).
        :return: 0 (low light) or 1 (high light).
        """
        return GPIO.input(pin)
    
    def initialize(self):
        """
        Initializes both sensors and checks if both give the same value.
        :return: True if both sensors give the same value, False otherwise.
        """
        sensor1_value = self.read_light_intensity(self.pin1)
        sensor2_value = self.read_light_intensity(self.pin2)
        
        if sensor1_value == sensor2_value:
            print(f"Both sensors are initialized and give the same value: {sensor1_value}")
            return True
        else:
            print(f"Initialization error: Sensor 1 = {sensor1_value}, Sensor 2 = {sensor2_value}")
            return False
    
    def cleanup(self):
        """Cleans up the GPIO settings."""
        GPIO.cleanup()


# Example usage
if __name__ == "__main__":
    sensor = LightSensor(pin1=17, pin2=27)  # Assuming the light sensors are connected to GPIO17 and GPIO27

    # Initialize sensors and check if both sensors give the same value
    if sensor.initialize():
        try:
            while True:
                light_intensity_sensor1 = sensor.read_light_intensity(sensor.pin1)
                light_intensity_sensor2 = sensor.read_light_intensity(sensor.pin2)

                print(f"Sensor 1 Light Intensity: {'ABOVE' if light_intensity_sensor1 else 'BELOW'} threshold")
                print(f"Sensor 2 Light Intensity: {'ABOVE' if light_intensity_sensor2 else 'BELOW'} threshold")
                
                print("-----------------------------")
                time.sleep(1)  # Read every second
                
        except KeyboardInterrupt:
            print("Exiting Light Sensor Reader...")
        finally:
            sensor.cleanup()
    else:
        print("Sensors are not synchronized. Exiting.")
