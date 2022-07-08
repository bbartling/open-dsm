import BAC0, time


bacnet = BAC0.lite()

# Duct Pressure RTU Point
address = "10.200.200.27"
object_type = "analogValue"
object_instance = "3"
priority = 8
value = 0.5

# Event duration
event_duration_minutes = 10


read_vals = f"{address} {object_type} {object_instance} presentValue"
check = bacnet.read(read_vals)
print(f"Initial RTU duct pressure is: {check}")


# create write statement and run
write_vals = f"{address} {object_type} {object_instance} presentValue {value} - {priority}"
print("Excecuting BACnet write: ", write_vals)

write_result = bacnet.write(write_vals)
print(f"BACnet written to {address} device")

read_vals_two = f"{address} {object_type} {object_instance} presentValue"
check_two = bacnet.read(read_vals_two)
print("Checking the BACnet write to make sure it took: ", check_two)


"""
HALF TIME
"""
      
print("sleeping now... for in minutes: ",event_duration_minutes * 60)
time.sleep(event_duration_minutes * 60)

print("time to release!!!")
release_vals = f"{address} {object_type} {object_instance} presentValue null - {priority}"
print("Excecuting BACnet release: ", release_vals)

release_result = bacnet.write(release_vals)
print("BACnet release to {address} device")

release_check = f"{address} {object_type} {object_instance} presentValue"
check_= bacnet.read(release_check)
print("Checking the BACnet release was good: ", check_)

print("all done BAC0 rocks....!")
bacnet.disconnect()