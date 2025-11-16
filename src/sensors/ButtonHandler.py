import time
import random
import os

class ButtonHandler:
    """
    Handles two physical buttons (GPIO) or simulates them if RPi.GPIO isn't available.
    - 'next' button: switches dashboard view
    - 'extra' button: reserved for future use
    - Shutdown is triggered if **both buttons are held for 3 seconds simultaneously**.
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
        self.press_start_time = {"next": 0, "extra": 0}  # Track press start times
        self.debounce_delay = 0.3  # seconds
        self.shutdown_threshold = 3  # seconds to hold both buttons

    def is_pressed(self, name):
        """Check if the given button ('next' or 'extra') is pressed."""
        if name not in self.pins:
            raise ValueError("Invalid button name. Use 'next' or 'extra'.")

        now = time.time()
        if now - self.last_press_time[name] < self.debounce_delay:
            return False

        pressed = False
        if self.GPIO_AVAILABLE:
            if self.GPIO.input(self.pins[name]) == self.GPIO.LOW:
                pressed = True
        else:
            # Simulation mode: randomly trigger buttons
            if random.random() < 0.3:
                pressed = True
                print(f"[SIM] {name} button pressed")

        if pressed:
            self.last_press_time[name] = now
            if self.press_start_time[name] == 0:
                self.press_start_time[name] = now  # mark the start of the press
        else:
            self.press_start_time[name] = 0  # reset if released

        return pressed

    def check_for_shutdown(self):
        """
        Trigger shutdown if **both buttons are pressed simultaneously** for at least shutdown_threshold seconds.
        """
        now = time.time()
        next_pressed = self.is_pressed("next")
        extra_pressed = self.is_pressed("extra")

        # Both buttons pressed → track earliest press start
        if next_pressed and extra_pressed:
            start_times = [t for t in self.press_start_time.values() if t != 0]
            if start_times and now - min(start_times) >= self.shutdown_threshold:
                print(f"[INFO] Both buttons held for {self.shutdown_threshold} seconds. Shutting down...")
                self.cleanup()
                os.system("sudo shutdown now")
                return True
        else:
            # Reset if any button released
            for name in self.press_start_time:
                if not self.is_pressed(name):
                    self.press_start_time[name] = 0

        return False

    def cleanup(self):
        if self.GPIO_AVAILABLE:
            self.GPIO.cleanup()
