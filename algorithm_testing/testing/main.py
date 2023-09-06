import time
from functions import PowerMeter, Chiller, LightingSystem, WaterPumpingSystem, AirHandlingSystem


class DemandSideManagement:
    def __init__(self):
        self.power_setpoint = 1000  
        self.power_values = []
        self.power_meter = PowerMeter()
        self.water_system_heat = WaterPumpingSystem()
        self.water_system_cool = WaterPumpingSystem()
        self.air_system = AirHandlingSystem()
        self.lighting_system = LightingSystem()
        self.chiller_system = Chiller()


    def adjust_power_consumption(self):
        avg_power = sum(self.power_values) / len(self.power_values) if self.power_values else 0

        if avg_power > self.power_setpoint:
            self.reduce_power_consumption()
        elif avg_power < self.power_setpoint:
            self.increase_power_consumption()

            # Check if setpoints should be released back to the main control system
            self.water_system_heat.release_control_to_system()
            self.water_system_cool.release_control_to_system()
            self.air_system.release_control_to_system()
            
    def reduce_power_consumption(self):
        self.water_system_heat.decrease_setpoint()
        self.water_system_cool.decrease_setpoint()
        self.air_system.decrease_setpoint()
        self.lighting_system.decrease_brightness()
        self.chiller_system.decrease_capacity()

    def increase_power_consumption(self):
        self.water_system_heat.increase_setpoint()
        self.water_system_cool.increase_setpoint()
        self.air_system.increase_setpoint()
        self.lighting_system.increase_brightness()
        self.chiller_system.increase_capacity()

    def periodic_check(self):
        count = 0
        while True:
            current_power = self.power_meter.read_current_power()
            self.power_values.append(current_power)
            if len(self.power_values) > 5:
                self.power_values.pop(0)

            count += 1
            if count == 5:
                self.adjust_power_consumption()
                count = 0

            time.sleep(60)  # Check every minute


def main():
    dsm = DemandSideManagement()
    dsm.periodic_check()

if __name__ == "__main__":
    main()
