from src.sensors.DHT11 import DHT11Sensor
import random

class SensorOverlay:
    def __init__(self, car_pin, vent_pin, clock, test_mode=False):
        """
        Overlay system combining a clock with two DHT11 sensors.
        :param car_pin: GPIO pin for the car DHT11 sensor.
        :param vent_pin: GPIO pin for the ventilation DHT11 sensor.
        :param clock: Clock display instance to overlay text on.
        :param test_mode: If True, generate simulated data (no hardware needed).
        """
        self.sensor_system = DHT11Sensor(car_pin, vent_pin)
        self.clock = clock
        self.test_mode = test_mode  # auto-enable simulation mode

        # Fake data baseline for pure test mode
        self.fake_car_temp = 22.0
        self.fake_car_hum = 45.0
        self.fake_vent_temp = 21.0
        self.fake_vent_hum = 48.0

    # ---------------------------------------------------------------------
    # Main loop
    # ---------------------------------------------------------------------
    def update_sensor_data(self):
        """Periodically read both sensors and update the overlay text on the clock."""
        if self.test_mode:
            car_temp, car_hum, vent_temp, vent_hum = self._generate_fake_data()
        else:
            car_temp, car_hum = self.sensor_system.read_sensor_data('car')
            vent_temp, vent_hum = self.sensor_system.read_sensor_data('vent')

        if (car_temp is not None and car_hum is not None and
                vent_temp is not None and vent_hum is not None):
            self.overlay_temperature_and_humidity(car_temp, car_hum, vent_temp, vent_hum)
        else:
            self.overlay_error("Sensor read failed")

        # Update every 1 second 
        delay = 1000
        self.clock.root.after(delay, self.update_sensor_data)

    # ---------------------------------------------------------------------
    # Overlay rendering
    # ---------------------------------------------------------------------
    def _get_canvas_center(self):
        """Return the current canvas center coordinates (x, y)."""
        canvas = self.clock.canvas
        canvas.update_idletasks()
        return canvas.winfo_width() // 2, canvas.winfo_height() // 2

    def overlay_temperature_and_humidity(self, car_temp, car_hum, vent_temp, vent_hum):
        """
        Overlay the temperature and humidity readings from both sensors
        on the clock display (left and right of the 'Quartz' text).
        """
        self.clock.canvas.delete("sensor_text")

        # Get the current canvas center and radius
        canvas = self.clock.canvas
        canvas.update_idletasks()
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        cx, cy = width // 2, height // 2
        radius = min(width, height) // 2 - 1

        # Determine where the "Quartz" text sits (roughly 40% down from center)
        quartz_y = cy + radius * 0.4

        # Car sensor (left of center)
        text_car = f"🚗 {car_temp:.1f}°C  {car_hum:.0f}%"
        canvas.create_text(
            cx - radius * 0.3, quartz_y,
            text=text_car, font=("Arial", int(radius / 20), "bold"),
            fill="white", anchor="e", tags="sensor_text"
        )

        # Vent sensor (right of center)
        text_vent = f"{vent_temp:.1f}°C  {vent_hum:.0f}% 💨"
        canvas.create_text(
            cx + radius * 0.3, quartz_y,
            text=text_vent, font=("Arial", int(radius / 20), "bold"),
            fill="white", anchor="w", tags="sensor_text"
        )

    def overlay_error(self, message):
        """Show a brief error message on the display."""
        self.clock.canvas.delete("sensor_text")
        cx, cy = self._get_canvas_center()
        self.clock.canvas.create_text(
            cx, cy + 240,
            text=message, font=("Arial", 18), fill="red", tags="sensor_text"
        )

    # ---------------------------------------------------------------------
    # Fake data generator
    # ---------------------------------------------------------------------
    def _generate_fake_data(self):
        """Simulate realistic temperature/humidity fluctuations for testing."""
        self.fake_car_temp += random.uniform(-0.2, 0.2)
        self.fake_car_hum += random.uniform(-0.5, 0.5)
        self.fake_vent_temp += random.uniform(-0.2, 0.2)
        self.fake_vent_hum += random.uniform(-0.5, 0.5)

        # Clamp values
        self.fake_car_temp = max(18, min(28, self.fake_car_temp))
        self.fake_car_hum = max(30, min(70, self.fake_car_hum))
        self.fake_vent_temp = max(18, min(28, self.fake_vent_temp))
        self.fake_vent_hum = max(30, min(70, self.fake_vent_hum))

        return (self.fake_car_temp, self.fake_car_hum,
                self.fake_vent_temp, self.fake_vent_hum)
