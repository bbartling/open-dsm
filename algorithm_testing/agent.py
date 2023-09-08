import logging
import sys
import time
import pandas as pd
from volttron.platform.vip.agent import Agent, Core
from functions import PowerMeter, Chiller, LightingSystem, WaterPumpingSystem, AirHandlingSystem
from sklearn.ensemble import RandomForestRegressor

_log = logging.getLogger(__name__)


class DemandSideManagementAgent(Agent):
    
    def __init__(self, config_path, **kwargs):
        super(DemandSideManagementAgent, self).__init__(**kwargs)
        # You can read configuration using the config_path if needed
        self.setup_variables()
        
    def setup_variables(self):
        self.data_cache = pd.DataFrame(columns=["ds", "y"])
        self.power_setpoint = 1000
        self.power_meter = PowerMeter()
        self.HIGH_RATE_OF_CHANGE_SETPOINT = 20
        self.data_cache = pd.DataFrame(columns=["ds", "y"])
        self.power_setpoint = 1000  
        self.power_values = []
        self.power_meter = PowerMeter()
        self.water_system_heat = WaterPumpingSystem()
        self.water_system_cool = WaterPumpingSystem()
        self.air_system = AirHandlingSystem()
        self.lighting_system = LightingSystem()
        self.chiller_system = Chiller()
        self.actual_values = []
        self.current_power_last_hour_avg_rate_of_change = 0
        self.current_power_lv_rate_of_change = 0
        self.data_cache = pd.DataFrame(columns=["ds", "y"])
        self.actual_values = []
        self.current_power_last_hour_avg_rate_of_change = 0
        self.current_power_lv_rate_of_change = 0

    def calc_power_rate_of_change(self, current_value):
        if len(self.actual_values) > 1:
            current_rate_of_change = current_value - self.actual_values[-2]
            # Exclude negative rate of change
            current_rate_of_change = max(0, current_rate_of_change)
        else:
            current_rate_of_change = 0

        if len(self.actual_values) > 60:
            last_hour_values = self.actual_values[-61:-1]
            avg_rate_of_change = (last_hour_values[-1] - last_hour_values[0]) / 60.0
            # Exclude negative average rate of change
            avg_rate_of_change = max(0, avg_rate_of_change)
        else:
            avg_rate_of_change = current_rate_of_change

        self.current_power_last_hour_avg_rate_of_change = avg_rate_of_change
        self.current_power_lv_rate_of_change = current_rate_of_change

    def fetch_and_store_data(self):
        timestamp, new_data = self.power_meter.get_timestamp_and_power()
        if timestamp is None:
            return False
        new_row = {"ds": timestamp, "y": new_data}
        self.data_cache = pd.concat([self.data_cache, pd.DataFrame([new_row])], ignore_index=True)
        if len(self.data_cache) > self.CACHE_LIMIT:
            self.data_cache = self.data_cache.iloc[-self.CACHE_LIMIT :]
        return True

    def create_dataset(self, dataset):
        dataX, dataY = [], []
        for i in range(len(dataset) - 61):
            a = dataset[i:(i + 60)]
            dataX.append(a)
            dataY.append(dataset[i + 60])
        return np.array(dataX), np.array(dataY)


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
        model = None
        last_train_time = None
        self.HIGH_RATE_OF_CHANGE_SETPOINT = 20  # Adjust this value as needed
        
        while True:
            current_power = self.power_meter.read_current_power()
            self.power_values.append(current_power)
            self.actual_values.append(current_power)

            if len(self.power_values) > 5:
                self.power_values.pop(0)

            count += 1
            if count == 5:
                self.adjust_power_consumption()
                count = 0

            # attempts to detect a spike, like equipment startup
            self.calc_power_rate_of_change(current_power)

            # fetch and store data
            data_available = self.fetch_and_store_data()
            if not data_available:
                continue
            
            current_time = self.data_cache["ds"].iloc[-1]
            y = self.data_cache["y"].values

            # Only train if there are more than 60+1 data points in data_cache
            if len(y) > 61 and (
                last_train_time is None or (current_time - last_train_time) >= pd.Timedelta(days=1)
            ):
                print("Fit Model Called!")
                X, Y = self.create_dataset(y)
                model = RandomForestRegressor(n_estimators=100, random_state=42)
                model.fit(X, Y.ravel())
                last_train_time = current_time

            forecasted_value_60 = None
            if model is not None:
                forecasted_value_60 = model.predict(y[-60:].reshape(1, -1))[0]
                print(f"Forecasted Value 60 minutes ahead: {forecasted_value_60}")
            
            # Decision-making logic for adjusting power consumption
            if forecasted_value_60:
                max_power = max(current_power, forecasted_value_60)
                if max_power > self.power_setpoint:
                    print("Increasing power consumption due to forecasted high demand.")
                    self.increase_power_consumption()
                elif max_power < self.power_setpoint:
                    print("Reducing power consumption due to forecasted low demand.")
                    self.reduce_power_consumption()

            if self.current_power_lv_rate_of_change > self.HIGH_RATE_OF_CHANGE_SETPOINT:
                print("Detected high rate of change in power. Reducing consumption.")
                self.reduce_power_consumption()


    @Core.receiver('onstart')
    def onstart(self, sender, **kwargs):
        # Actions to be done when agent starts
        self.core.schedule(periodic=60, callback=self.periodic_check)

def main():
    try:
        utils.vip_main(DemandSideManagementAgent)
    except Exception as e:
        _log.exception('unhandled exception')

if __name__ == '__main__':
    # Entry point for script
    sys.exit(main())
