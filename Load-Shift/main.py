import BAC0, time
import logging
from datetime import datetime
import csv


# BACnet write priority
priority = '8'

# override JCI reheat coils shut / Trane not writeable
jci_zntsp_object_type_instance = 'analogValue 1103'
trane_zntsp_object_type_instance = 'analogValue 27'
hot_water_sys_enable = 'binaryValue 7'

# zone setpoints to write at a time
_zntsp_5AM = 68.01
_zntsp_10AM = 70.0
_zntsp_12PM = 72.0
_zntsp_2PM = 74.0

# boolean objects to write once
five_am_done = False
ten_am_done = False
twelve_pm_done = False
two_pm_done = False
final_release_done = False

# datetime object containing current date and time
now = datetime.now()
dt_string = now.strftime("%m_%d_%Y %H:%M:%S")
logging.basicConfig(filename=f'log_{dt_string}.log', level=logging.INFO)
print(f"Running NOW date and time is {dt_string}")


try:
    print(f"Trying to see if any BAD BACnet addresses exist from previous runs!")
    with open('bad_addresses.csv', newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
    # flattens list of lists
    bad_addresses = sum(data, [])
    print("BAD ADDRESSES found that the program will skip over: ",bad_addresses)

except Exception as error:
    print(f"couldnt open up previous runs of BAD BACnet addresses!")
    bad_addresses = [] # errors out


# define bacnet app
bacnet = BAC0.lite()
time.sleep(2)

# generates all BACnet addresses some are not VAV boxes
devices = bacnet.whois(global_broadcast=True)
device_mapping = {}

jci_addresses = []
trane_addresses = []

jci_addresses_written = []
trane_addresses_written = []


for device in devices:
    if isinstance(device, tuple):
        device_mapping[device[1]] = device[0]
        print("Detected device %s with address %s" % (str(device[1]), str(device[0])))

print(device_mapping)
print((str(len(device_mapping)) + " devices discovered on network."))


 # Rooftop AHU is ID 1100, Trane Sup is 100, and boiler is 1102
 # there are some other random devices but most are VAV boxes
for bacnet_inst,address in device_mapping.items():
    if bacnet_inst < 100: #JCI boxes have inst ID less than 100 on this site
        jci_addresses.append(address)
print("jci_addresses is: ",jci_addresses)

for bacnet_inst,address in device_mapping.items():
    if bacnet_inst > 10000: #Trane boxes have inst ID less than 100 on this site
        trane_addresses.append(address)
print("trane_addresses is: ",trane_addresses)



# function to BACnet read and write
def bacnet_requester(action,req_str):
    if action == "read":
        result = bacnet.read(req_str)
        return result
    else:
        result = bacnet.write(req_str)
        print("Write success")


# write new setpoints function
def write_new_zntsp_all(setpoint):
    print("JCI ADDRESSES: ",jci_addresses)
    for address in jci_addresses:
        try:
            if address not in bad_addresses:
                print("Doing DEVICE: ",address)
                logging.info(f"Doing DEVICE: {address}")

                write_jci_zntsp = f'{address} {jci_zntsp_object_type_instance} presentValue \
                    {setpoint} - {priority}'

                print("Excecuting write_jci_zntsp statement:", write_jci_zntsp)
                bacnet_requester("write",write_jci_zntsp)

                print("******************************************")
                jci_addresses_written.append(address)

            else:
                print(f"Bad address {address} passing...")

        except Exception as error: # coult be a non-VAV box device
            print(f"OOF error on device {address}: {error}")
            bad_addresses.append(address)


    # (°F − 32) × 5/9
    trane_setpoint = (setpoint - 32) * 5/9
    print("TRANE ADDRESSES: ",trane_addresses)
    for address in trane_addresses:
        try:
            if address not in bad_addresses:
                print("Doing DEVICE: ",address)
                logging.info(f"Doing DEVICE: {address}")

                write_trane_zntsp = f'{address} {trane_zntsp_object_type_instance} presentValue \
                    {trane_setpoint} - {priority}'

                print("Excecuting write_trane_zntsp statement:", write_trane_zntsp)
                bacnet_requester("write",write_trane_zntsp)

                print("******************************************")
                trane_addresses_written.append(address)

            else:
                print(f"Bad address {address} passing...")

        except Exception as error: # coult be a non-VAV box device
            print(f"OOF error on device {address}: {error}")
            logging.info(f"OOF error on device {address}: {error}")
            bad_addresses.append(address)


# release all overrides function
def release_all():
    for address in jci_addresses_written:
        try:
            print("Releasing DEVICE: ",address)
            logging.info(f"Releasing DEVICE: {address}")
            release_jci_zntsp = f'{address} {jci_zntsp_object_type_instance} presentValue \
                null - {priority}'
            print("Excecuting release_jci_zntsp statement:", release_jci_zntsp)
            bacnet_requester("write",release_jci_zntsp)

            print("******************************************")

        except Exception as error:
            print(f"OOF error on device {address}: {error}")
            bad_addresses.append(address)

    for address in trane_addresses_written:
        try:
            print("Releasing DEVICE: ",address)
            logging.info(f"Releasing DEVICE: {address}")
            release_trane_zntsp = f'{address} {trane_zntsp_object_type_instance} presentValue \
                null - {priority}'

            print("Excecuting release_trane_zntsp statement:", release_trane_zntsp)
            bacnet_requester("write",release_trane_zntsp)
            print("******************************************")

        except Exception as error:
            print(f"OOF error on device {address}: {error}")
            logging.info(f"OOF error on device {address}: {error}")
            bad_addresses.append(address)


# turn off boiler function
def turn_off_hw_sys():
    # turn off boiler to start with
    turn_off_boiler = f'10.200.200.32 {hot_water_sys_enable} presentValue \
        inactive - {priority}'

    print("BOILER OFF! - ", turn_off_boiler)
    bacnet_requester("write",turn_off_boiler)


# release boiler function (turn back on)
def release_hw_sys():
    # release boiler when released all VAV boxes
    release_boiler = f'10.200.200.32 {hot_water_sys_enable} presentValue \
        null - {priority}'
    print("BOILER RELEASE! - ", release_boiler)
    bacnet_requester("write",release_boiler)


# check time every second called by the while loop
def time_checker(now):
    global five_am_done, ten_am_done, twelve_pm_done, two_pm_done, final_release_done

    if now.hour >= 5 and now.hour < 10:
        if not five_am_done:
            turn_off_hw_sys()
            write_new_zntsp_all(_zntsp_5AM)
            five_am_done = True

    elif now.hour >= 10 and now.hour < 12:
        if not ten_am_done:
            write_new_zntsp_all(_zntsp_10AM)
            ten_am_done = True

    elif now.hour >= 12 and now.hour < 14:
        if not twelve_pm_done:
            write_new_zntsp_all(_zntsp_12PM)
            twelve_pm_done = True

    elif now.hour >= 14 and now.hour < 16:
        if not two_pm_done:
            write_new_zntsp_all(_zntsp_2PM)
            two_pm_done = True

    else:
        if not final_release_done:
            release_hw_sys()
            release_all()
            final_release_done = True



while not final_release_done:

    # datetime object
    now_time = datetime.now()
    time_checker(now_time)
    time.sleep(1)



# gracefully exit BACnet app BAC0 if you can
print("ALL DIGITY DONE!!!")
bacnet.disconnect()

# collect bad addresses so we dont try them next go around
print("clean up now... write bad addresses to CSV")
print("bad addresses found: ",bad_addresses)
with open('bad_addresses.csv', 'w', newline='') as csv_1:
  csv_out = csv.writer(csv_1)
  csv_out.writerows([bad_addresses[index]] for index in range(0, len(bad_addresses)))



