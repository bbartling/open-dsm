import pandas as pd
import time

class ControlSystem:
    def __init__(self, initial_value, min_value, max_value, step):
        self.value = initial_value
        self.MIN_VALUE = min_value
        self.MAX_VALUE = max_value
        self.step = step
        self.original_value = None 

    def decrease_value(self):
        if self.original_value is None:
            self.original_value = self.value
        self.value = max(self.value - self.step, self.MIN_VALUE)

    def increase_value(self):
        self.value = min(self.value + self.step, self.MAX_VALUE)

    def release_control_to_system(self):
        if self.original_value is not None and self.value >= self.original_value:
            self.value = self.original_value
            self.original_value = None

class Chiller(ControlSystem):
    def __init__(self):
        super().__init__(100, 0, 100, 10)

class LightingSystem(ControlSystem):
    def __init__(self):
        super().__init__(100, 10, 100, 10)

class WaterPumpingSystem(ControlSystem):
    def __init__(self):
        super().__init__(10, 5, 20, 0.5)

class AirHandlingSystem(ControlSystem):
    def __init__(self):
        super().__init__(1.0, 0.5, 2.0, 0.1)


class PowerMeter:
    def read_current_power(self):
        # Placeholder function to simulate reading from a power meter
        return 1000  # Sample power reading, this can be changed accordingly.

    def get_timestamp_and_power(self):
        # Get the current timestamp and power reading
        timestamp = pd.Timestamp(time.time(), unit='s')
        power = self.read_current_power()
        return timestamp, power
