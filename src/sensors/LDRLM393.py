import random

try:
    import RPi.GPIO as GPIO
    RPI_AVAILABLE = True
except ImportError:
    RPI_AVAILABLE = False
    print("[Warning] RPi.GPIO not found — running in simulation mode.")

class LDRLM393:
    def __init__(self, pin1=22, pin2=10):
        """
        Initializes the two light sensors.
        """
        self.pin1 = pin1
        self.pin2 = pin2

        if RPI_AVAILABLE:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin1, GPIO.IN)
            GPIO.setup(self.pin2, GPIO.IN)

    def read_light_intensity(self, pin):
        """
        Reads light intensity (0 or 1) from a given pin.
        """
        if RPI_AVAILABLE:
            return GPIO.input(pin)
        else:
            # Simulate smooth day/night transitions
            if pin == self.pin1:
                self._sim_light1 = 1 if random.random() > 0.4 else 0
                return self._sim_light1
            else:
                self._sim_light2 = 1 if random.random() > 0.4 else 0
                return self._sim_light2

    def initialize(self):
        """
        Initializes both sensors and checks if both give the same value.
        """
        val1 = self.read_light_intensity(self.pin1)
        val2 = self.read_light_intensity(self.pin2)
        if val1 == val2:
            print(f"[LightSensor] Initialized: both sensors read {val1}")
            return True
        else:
            print(f"[LightSensor] Init mismatch: {val1} vs {val2}")
            return False

    def cleanup(self):
        if RPI_AVAILABLE:
            GPIO.cleanup()