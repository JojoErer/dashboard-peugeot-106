import time
import random
import os

class ButtonHandler:
    """
    Handles two physical buttons (GPIO) or simulates them if RPi.GPIO isn't available.
    - 'next' button: switches dashboard view
    - 'extra' button: reserved for future use
    - Either button ('next' or 'extra') can trigger shutdown if held for 3 seconds.
    """

    def __init__(self, pin_next=18, pin_extra=23):
        self.pins = {"next": pin_next, "extra": pin_extra}
        self.GPIO_AVAILABLE = False
        self.simulated_state = {"next": False, "extra": False}
        self.test_mode: bool = False

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
            self.test_mode = True
            print("[INFO] RPi.GPIO not found. Running in simulation mode.")

        # Debounce and long-press tracking
        self.last_press_time = {"next": 0, "extra": 0}
        self.press_start_time = {"next": 0, "extra": 0}  # To track long presses
        self.debounce_delay = 0.3  # seconds
        self.shutdown_threshold = 3  # seconds to hold for shutdown

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
                if self.press_start_time[name] == 0:
                    self.press_start_time[name] = now  # Mark the start of the press
                return True
        else:
            # Simulation mode: randomly trigger buttons every few cycles
            if random.random() < 0.3:
                self.last_press_time[name] = now
                self.press_start_time[name] = now  # Mark the start of the press
                print("[SIM] button pressed")
                return True

        return False

    def check_for_shutdown(self):
        """Check if either of the buttons has been held long enough to trigger shutdown."""
        for name in self.pins:
            if self.press_start_time[name] != 0:
                now = time.time()
                if now - self.press_start_time[name] >= self.shutdown_threshold:
                    print(f"[INFO] {name.capitalize()} button held for 3 seconds. Shutting down...")
                    self.cleanup()
                    os.system("sudo shutdown now")
                    return True
        return False

    def cleanup(self):
        if self.GPIO_AVAILABLE:
            self.GPIO.cleanup()
