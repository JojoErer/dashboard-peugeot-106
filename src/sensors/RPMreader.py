import time
import random

class RPMreader:
    """
    Reads RPM from a GPIO pin by counting rising edges for 1 second.
    Falls back to simulated RPM if GPIO is unavailable.
    """

    def __init__(self, pin=17, pulses_per_revolution=1, update_interval=1.0):
        self.pin = pin
        self.pulses_per_revolution = pulses_per_revolution
        self.update_interval = update_interval

        self._pulse_count = 0
        self._rpm = 0
        self.test_mode = False
        self._last_update = time.time()

        try:
            import RPi.GPIO as GPIO
            self.GPIO = GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            GPIO.add_event_detect(self.pin, GPIO.RISING, callback=self._pulse_callback)
            print("[RPM] GPIO initialized on pin", self.pin)
        except Exception as e:
            print(f"[RPM] GPIO unavailable, using simulation mode: {e}")
            self.GPIO = None
            self.test_mode = True

    def _pulse_callback(self, channel):
        self._pulse_count += 1

    def read_rpm(self):
        """
        Call this periodically (e.g. every 500ms).
        RPM updates once per update_interval.
        """
        now = time.time()
        elapsed = now - self._last_update

        if elapsed >= self.update_interval:
            pulses = self._pulse_count
            self._pulse_count = 0
            self._last_update = now

            if self.test_mode:
                self._rpm = self._simulate_rpm()
            else:
                self._rpm = int((pulses / self.pulses_per_revolution) * 60)

        return self._rpm

    def _simulate_rpm(self):
        """
        Simple smooth RPM simulation.
        """
        target = random.randint(800, 4000)
        return int(self._rpm + (target - self._rpm) * 0.2)

    def cleanup(self):
        if self.GPIO:
            self.GPIO.cleanup(self.pin)
