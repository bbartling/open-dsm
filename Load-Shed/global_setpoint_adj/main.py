import BAC0, time
import logging
from datetime import datetime
import csv

priority = '8'
duration_minutes = 5

# override JCI reheat coils shut / Trane not writeable
jci_reheat_object_type_instance = 'analogOutput 2014'
jci_zntsp_object_type_instance = 'analogValue 1103'
_zntsp_adder = 2.0

trane_zntsp_adder = 2.0 * 5/9 # Trane BACnet data is Celcuis
trane_zntsp_object_type_instance = 'analogValue 27'


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


print("JCI ADDRESSES: ",jci_addresses)
for address in jci_addresses:
    try:
        if address not in bad_addresses:
            print("Doing DEVICE: ",address)
            logging.info(f"Doing DEVICE: {address}")

            read_jci_zntsp = f'{address} {jci_zntsp_object_type_instance} presentValue'

            zntsp = bacnet_requester("read",read_jci_zntsp)
            print("Zone Temp is: ",zntsp)

            write_jci_zntsp = f'{address} {jci_zntsp_object_type_instance} presentValue \
                {zntsp + _zntsp_adder} - {priority}'

            print("Excecuting write_jci_zntsp statement:", write_jci_zntsp)
            bacnet_requester("write",write_jci_zntsp)

            close_jci_reheat = f'{address} {jci_reheat_object_type_instance} presentValue 0 - {priority}'
            bacnet_requester("write",close_jci_reheat)
            print("write reheat valve and reheat coil success")
            print("******************************************")

            jci_addresses_written.append(address)

        else:
            print(f"Bad address {address} passing...")

    except Exception as error:
        print(f"OOF error on device {address}: {error}")
        bad_addresses.append(address)


print("TRANE ADDRESSES: ",trane_addresses)

for address in trane_addresses:
    try:
        if address not in bad_addresses:
            print("Doing DEVICE: ",address)
            logging.info(f"Doing DEVICE: {address}")

            read_trane_zntsp = f'{address} {trane_zntsp_object_type_instance} presentValue'
            zntsp = bacnet_requester("read",read_trane_zntsp)
            print("Trane Zone Temp is: ",zntsp)

            write_trane_zntsp = f'{address} {trane_zntsp_object_type_instance} presentValue \
                {zntsp + trane_zntsp_adder} - {priority}'

            print("Excecuting write_trane_zntsp statement:", write_trane_zntsp)
            bacnet_requester("write",write_trane_zntsp)

            print("******************************************")

            trane_addresses_written.append(address)

        else:
            print(f"Bad address {address} passing...")

    except Exception as error:
        print(f"OOF error on device {address}: {error}")
        logging.info(f"OOF error on device {address}: {error}")
        bad_addresses.append(address)


"""
HALF TIME START!
"""

print("sleeping now for minutes: ",duration_minutes)
logging.info(f"sleeping now for minutes: {duration_minutes}")
time.sleep(duration_minutes * 60)

"""
HALF TIME END!
"""

print("All Done Sleeping ready to release")
logging.info("All Done Sleeping ready to release")



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



print("ALL DIGITY DONE!!!")
bacnet.disconnect()


print("bad addresses found: ",bad_addresses)
print("clean up now... write bad addresses to CSV")
with open('bad_addresses.csv', 'w', newline='') as csv_1:
  csv_out = csv.writer(csv_1)
  csv_out.writerows([bad_addresses[index]] for index in range(0, len(bad_addresses)))

