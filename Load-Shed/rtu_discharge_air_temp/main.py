import BAC0, time
import logging
from datetime import datetime


# datetime object containing current date and time
now = datetime.now()

dt_string = now.strftime("%m_%d_%Y %H:%M:%S")
logging.basicConfig(filename=f'log_{dt_string}.log', level=logging.INFO)

print(f"Running NOW date and time is {dt_string}")

# define bacnet app
bacnet = BAC0.lite()

# Discharge Air Temperature Setpoint Active RTU Point
address = "10.200.200.27"
object_type = "analogValue"
object_instance = "12"
priority = 7
disch_temp_adder = 5.0 # add to the rtu leav temp setpoint


# Event duration
event_duration_minutes = 30


initial_setpoint = f"{address} {object_type} {object_instance} presentValue"
initial_setpoint_val = bacnet.read(initial_setpoint)
print(f"Initial RTU discharge air setpoint is: {initial_setpoint_val}")

new_initial_setpoint_val = initial_setpoint_val + disch_temp_adder
print(f"The RTU discharge air setpoint +5 degrees F is: {new_initial_setpoint_val}")

# create write statement and run
write_vals = f"{address} {object_type} {object_instance} presentValue \
     {new_initial_setpoint_val} - {priority}"

print(f"Excecuting BACnet write: {write_vals}")
bacnet.write(write_vals)
print(f"BACnet written to {address} device")


read_check = f"{address} {object_type} {object_instance} presentValue"
check_two = bacnet.read(read_check)
print(f"Checking the BACnet write to make sure it took: {check_two}")



"""
HALF TIME
"""
      
print(f"sleeping now... for in seconds: {event_duration_minutes * 60}")
logging.info(f"sleeping now... for in seconds: {event_duration_minutes * 60}")
time.sleep(event_duration_minutes * 60)


print(f"time to release!!!")
logging.info("time to release!!!")
release_vals = f"{address} {object_type} {object_instance} presentValue null - {priority}"
print(f"Excecuting BACnet release: {release_vals}")

bacnet.write(release_vals)
print(f"BACnet release to {address} device")


release_check = f"{address} {object_type} {object_instance} presentValue"
check_= bacnet.read(release_check)



print(f"all done BAC0 rocks....!")
logging.info(f"all done BAC0 rocks....!")
bacnet.disconnect()