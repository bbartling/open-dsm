import BAC0, time
import logging
from datetime import datetime




# datetime object containing current date and time
now = datetime.now()

dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
logging.basicConfig(filename=f'log_{dt_string}.log', level=logging.WARNING)


print("Running NOW date and time is", dt_string)
logging.info(f"Running NOW date and time is {dt_string}")


# define BACnet app
bacnet = BAC0.lite()


# Duct Pressure RTU Point
address = "10.200.200.27"
object_type = "analogValue"
object_instance = "3"
priority = 7 # BACnet priority to write
value = 0.5 # new duct pressure setpoint

# Event duration
event_duration_minutes = 10


read_vals = f"{address} {object_type} {object_instance} presentValue"
check = bacnet.read(read_vals)
print(f"Initial RTU duct pressure is: {check}")
logging.info(f"Initial RTU duct pressure is: {check}")



# create write statement and run
write_vals = f"{address} {object_type} {object_instance} presentValue {value} - {priority}"
print(f"Excecuting BACnet write: {write_vals}")
logging.info(f"Excecuting BACnet write: {write_vals}")



bacnet.write(write_vals)
print(f"BACnet written to {address} device")
logging.info(f"BACnet written to {address} device")



read_vals_two = f"{address} {object_type} {object_instance} presentValue"
check_two = bacnet.read(read_vals_two)
print(f"Checking the BACnet write to make sure it took: {check_two}")
logging.info(f"Checking the BACnet write to make sure it took: {check_two}")



"""
HALF TIME
"""



print(f"sleeping now... for in minutes: {event_duration_minutes * 60}")
logging.info(f"sleeping now... for in minutes: {event_duration_minutes * 60}")
time.sleep(event_duration_minutes * 60)



print(f"time to release!!!")
logging.info(f"time to release!!!")
release_vals = f"{address} {object_type} {object_instance} presentValue null - {priority}"
print(f"Excecuting BACnet release: {release_vals}")
logging.info(f"Excecuting BACnet release: {release_vals}")



bacnet.write(release_vals)
print(f"BACnet release to {address} device sucess")
logging.info(f"BACnet release to {address} device sucess")



release_check = f"{address} {object_type} {object_instance} presentValue"
check_= bacnet.read(release_check)
print(f"Checking the BACnet release was good: {check_}")
logging.info(f"Checking the BACnet release was good: {check_}")



print(f"all done BAC0 rocks....!")
logging.info(f"all done BAC0 rocks....!")

bacnet.disconnect()