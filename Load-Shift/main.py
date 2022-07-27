import BAC0, time, schedule
import logging
from datetime import datetime
import csv



priority = '8'
duration_minutes = 5

# override JCI reheat coils shut / Trane not writeable
jci_zntsp_object_type_instance = 'analogValue 1103'
trane_zntsp_object_type_instance = 'analogValue 27'
hot_water_sys_enable = 'binaryValue 7'


_zntsp_5AM = 68.0
_zntsp_10AM = 70.0
_zntsp_12PM = 72.0
_zntsp_2PM = 74.0


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



# turn off boiler to start with
turn_off_boiler = f'{address} {hot_water_sys_enable} presentValue \
    1 - {priority}'

print("Excecuting turn_off_boiler statement:", turn_off_boiler)
bacnet_requester("write",turn_off_boiler)

'''
SCHEDULER BELOW - Dan Bader creation
https://github.com/dbader/schedule

'''

schedule.every().day.at("5:00").do(write_new_zntsp_all, setpoint=_zntsp_5AM)
schedule.every().day.at("10:00").do(write_new_zntsp_all, setpoint=_zntsp_10AM)
schedule.every().day.at("12:00").do(write_new_zntsp_all, setpoint=_zntsp_12PM)
schedule.every().day.at("14:00").do(write_new_zntsp_all, setpoint=_zntsp_2PM)
schedule.every().day.at("18:00").do(release_all)

while True:
    schedule.run_pending()
    time.sleep(1)




# turn off boiler to start with
release_boiler = f'{address} {hot_water_sys_enable} presentValue \
    null - {priority}'
print("SCHEDULER DONE!! Releasing boiler back to control", release_boiler)
bacnet_requester("write",release_boiler)

print("ALL DIGITY DONE!!!")
bacnet.disconnect()


print("bad addresses found: ",bad_addresses)
print("clean up now... write bad addresses to CSV")
with open('bad_addresses.csv', 'w', newline='') as csv_1:
  csv_out = csv.writer(csv_1)
  csv_out.writerows([bad_addresses[index]] for index in range(0, len(bad_addresses)))

