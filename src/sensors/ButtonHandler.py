import time
import random

class ButtonHandler:
    """
    Handles two physical buttons (GPIO) or simulates them if RPi.GPIO isn't available.
    - 'next' button: switches dashboard view
    - 'extra' button: reserved for future use
    """

    def __init__(self, pin_next=18, pin_extra=23):
        self.pins = {"next": pin_next, "extra": pin_extra}
        self.GPIO_AVAILABLE = False
        self.simulated_state = {"next": False, "extra": False}

        try:
            import RPi.GPIO as GPIO
            self.GPIO = GPIO
            self.GPIO.setmode(GPIO.BCM)

            # Set up buttons with pull-ups (active LOW)
            for name, pin in self.pins.items():
                self.GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

            self.GPIO_AVAILABLE = True
            print(f"[INFO] Buttons initialized on GPIO {pin_next} (next), {pin_extra} (extra)")
        except (ImportError, RuntimeError):
            print("[INFO] RPi.GPIO not found. Running in simulation mode.")

        # Debounce
        self.last_press_time = {"next": 0, "extra": 0}
        self.debounce_delay = 0.3  # seconds

    def is_pressed(self, name):
        """Check if the given button ('next' or 'extra') was pressed."""
        if name not in self.pins:
            raise ValueError("Invalid button name. Use 'next' or 'extra'.")

        now = time.time()
        if now - self.last_press_time[name] < self.debounce_delay:
            return False

        if self.GPIO_AVAILABLE:
            if self.GPIO.input(self.pins[name]) == self.GPIO.LOW:
                self.last_press_time[name] = now
                return True
        else:
            # Simulation mode: randomly trigger 'next' every few cycles
            if name == "next" and random.random() < 0.6:
                self.last_press_time[name] = now
                print("[SIM] 'next' button pressed")
                return True

        return False

    def cleanup(self):
        if self.GPIO_AVAILABLE:
            self.GPIO.cleanup()