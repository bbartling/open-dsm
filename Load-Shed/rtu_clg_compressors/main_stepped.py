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

object_type_and_instance = [
                "binaryOutput 3", #stage 1
                "binaryOutput 4", #stage 2
                "binaryOutput 5", #stage 3
                "binaryOutput 6"  #stage 4
                ]


# Duct Pressure RTU Point
address = "10.200.200.27"
priority = 8


# compressor read values
on_value = "active"
off_value = "inactive"


# Event duration
event_1_duration = 1 # 2 hours highest stage off
event_2_duration = 1 # 1 hours stage 2 off
event_3_duration = 1 # 1 hours stage 1 off



# make requests to count clg stages
stages_running_data = []
for stage in object_type_and_instance:
    read_req = f"{address} {stage} presentValue"
    read_val = bacnet.read(read_req)
    print("stage ", object_type_and_instance, "is: ",read_val)
    stages_running_data.append(read_val)


# loop thru read request data and count stages
stages_running = 0
for stage in stages_running_data:    
    if stage == 'active':
        stages_running += 1


print(f"the stages running: {stages_running}")
logging.info(f"the stages running: {stages_running}")


'''
# testing purposes redefine a fake value
stages_running = 3
'''

# make some decisions based on how many stages running
if stages_running == 0:
    print(f"No compressors are running, passing....")
    logging.info("No compressors are running, passing....")


# stage 1, 2, 3 are ON and 4 is OFF
elif stages_running == 3 or stages_running == 2:
    print(f"3 stages of cooling are running, overriding stage 3 and 4 OFF....")
    logging.info("3 stages of cooling are running, overriding stage 3 and 4 OFF....")            

    # create write statement and run
    write_stage_3_off = f"{address} binaryOutput 5 presentValue {off_value} - {priority}"
    print("Excecuting BACnet write: ", write_stage_3_off)
    bacnet.write(write_stage_3_off)


    # create write statement and run
    write_stage_4_off = f"{address} binaryOutput 6 presentValue {off_value} - {priority}"
    print("Excecuting BACnet write: ", write_stage_4_off)
    bacnet.write(write_stage_4_off)


elif stages_running == 4:
    print(f"4 stages of cooling are running, overriding stage ONLY stage 4 OFF....")
    logging.info("4 stages of cooling are running, overriding stage ONLY stage 4 OFF....")   


    # create write statement and run
    write_stage_4_off = f"{address} binaryOutput 6 presentValue {off_value} - {priority}"
    print("Excecuting BACnet write: ", write_stage_4_off)
    bacnet.write(write_stage_4_off)


else:
    print(f"Not enough cooling running to override OFF")
    logging.info("Not enough cooling running to override OFF")   




print(f"sleeping now event_1_duration... for in minutes: {event_1_duration * 60}")
logging.info(f"sleeping now event_1_duration... for in minutes: {event_1_duration * 60}") 
time.sleep(event_1_duration * 60)



"""
event_1_duration done - killed highest stage
next kill stage 2
"""


# create write statement and run
write_stage_2_off = f"{address} binaryOutput 4 presentValue {off_value} - {priority}"
print("Excecuting BACnet write: ", write_stage_2_off)
bacnet.write(write_stage_2_off)

print(f"sleeping now event_2_duration... for in minutes: {event_2_duration * 60}")
logging.info(f"sleeping now event_2_duration... for in minutes: {event_2_duration * 60}") 
time.sleep(event_2_duration * 60)



"""
kill stage 2 done
next kill stage 1
"""


# create write statement and run
write_stage_1_off = f"{address} binaryOutput 3 presentValue {off_value} - {priority}"
print("Excecuting BACnet write: ", write_stage_1_off)
bacnet.write(write_stage_1_off)

print(f"sleeping now event_3_duration... for in minutes: {event_3_duration * 60}")
logging.info(f"sleeping now event_3_duration... for in minutes: {event_3_duration * 60}") 
time.sleep(event_3_duration * 60)


"""
ALL DONE! ALL Stages should be off
"""


print("time to release!!!")
logging.info("time to release!!!")


# release all stages
release_req_stag_1 = f"{address} binaryOutput 3 presentValue null - {priority}"
bacnet.write(release_req_stag_1)

release_req_stag_2 = f"{address} binaryOutput 4 presentValue null - {priority}"
bacnet.write(release_req_stag_2)

release_req_stag_3 = f"{address} binaryOutput 5 presentValue null - {priority}"
bacnet.write(release_req_stag_3)

release_req_stag_4 = f"{address} binaryOutput 6 presentValue null - {priority}"
bacnet.write(release_req_stag_4)


print("all done BAC0 rocks....!")
logging.info("all done BAC0 rocks....!")
bacnet.disconnect()