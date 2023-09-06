

class PowerMeter:
    def read_current_power(self):
        return 0  # placeholder

class Chiller:
    def __init__(self):
        self.capacity_limit = 100  # in percentage, 100% being the maximum allowable capacity
        self.MIN_CAPACITY = 0  # minimum allowable capacity
        self.MAX_CAPACITY = 100  # maximum allowable capacity
        self.original_capacity = None

    def decrease_capacity(self):
        if self.original_capacity is None:
            self.original_capacity = self.capacity_limit
        self.capacity_limit = max(self.capacity_limit - 10, self.MIN_CAPACITY)  # reduce capacity by 10%

    def increase_capacity(self):
        self.capacity_limit = min(self.capacity_limit + 10, self.MAX_CAPACITY)

    def release_control_to_system(self):
        if self.original_capacity is not None and self.capacity_limit >= self.original_capacity:
            self.capacity_limit = self.original_capacity
            self.original_capacity = None

class LightingSystem:
    def __init__(self):
        self.brightness = 100  # in percentage, 100% being the brightest
        self.MIN_BRIGHTNESS = 10  # minimum allowable brightness
        self.MAX_BRIGHTNESS = 100  # maximum allowable brightness
        self.original_brightness = None 

    def decrease_brightness(self):
        if self.original_brightness is None:
            self.original_brightness = self.brightness
        self.brightness = max(self.brightness - 10, self.MIN_BRIGHTNESS)  # reduce brightness by 10%

    def increase_brightness(self):
        self.brightness = min(self.brightness + 10, self.MAX_BRIGHTNESS)

    def release_control_to_system(self):
        if self.original_brightness is not None and self.brightness >= self.original_brightness:
            self.brightness = self.original_brightness
            self.original_brightness = None

class WaterPumpingSystem:
    def __init__(self):
        self.setpoint = 10  # initial setpoint in PSI
        self.MIN_SETPOINT = 5  # minimum setpoint in PSI
        self.MAX_SETPOINT = 20  # maximum setpoint in PSI
        self.original_setpoint = None 

    def decrease_setpoint(self):
        if self.original_setpoint is None:
            self.original_setpoint = self.setpoint
        self.setpoint = max(self.setpoint - 0.5, self.MIN_SETPOINT)

    def increase_setpoint(self):
        self.setpoint = min(self.setpoint + 0.5, self.MAX_SETPOINT)

    def release_control_to_system(self):
        if self.original_setpoint is not None and self.setpoint >= self.original_setpoint:
            self.setpoint = self.original_setpoint
            self.original_setpoint = None

class AirHandlingSystem:
    def __init__(self):
        self.setpoint = 1.0  # initial setpoint in WC
        self.MIN_SETPOINT = 0.5  # minimum setpoint in WC
        self.MAX_SETPOINT = 2.0  # maximum setpoint in WC
        self.original_setpoint = None 

    def decrease_setpoint(self):
        if self.original_setpoint is None:
            self.original_setpoint = self.setpoint
        self.setpoint = max(self.setpoint - 0.1, self.MIN_SETPOINT)

    def increase_setpoint(self):
        self.setpoint = min(self.setpoint + 0.1, self.MAX_SETPOINT)

    def release_control_to_system(self):
        if self.original_setpoint is not None and self.setpoint >= self.original_setpoint:
            self.setpoint = self.original_setpoint
            self.original_setpoint = None