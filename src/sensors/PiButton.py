class Button:
    def __init__(self, pin=18):
        """Initialize a button on the given GPIO pin (BCM numbering)."""
        self.pin = pin
        self.GPIO_AVAILABLE = False
        self.simulated_state = False

        try:
            import RPi.GPIO as GPIO
            self.GPIO = GPIO
            self.GPIO.setmode(GPIO.BCM)
            self.GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            self.GPIO_AVAILABLE = True
            print(f"[INFO] Button initialized on GPIO {self.pin}")
        except (ImportError, RuntimeError):
            print("[INFO] RPi.GPIO not found. Running in simulation mode.")

    def is_pressed(self):
        """Return True if the button is pressed."""
        if self.GPIO_AVAILABLE:
            return self.GPIO.input(self.pin) == self.GPIO.LOW
        else:
            # Simulation: randomly return True occasionally
            import random
            self.simulated_state = random.random() < 0.5 
            return self.simulated_state

    def cleanup(self):
        if self.GPIO_AVAILABLE:
            self.GPIO.cleanup()