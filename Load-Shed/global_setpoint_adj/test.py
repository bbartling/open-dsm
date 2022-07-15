

import BAC0, time
import logging
from datetime import datetime

priority = '8'
duration_minutes = 5

# override JCI reheat coils shut / Trane not writeable
jci_reheat_object_type_instance = 'analogOutput 2014'
jci_zntsp_object_type_instance = 'analogValue 1103'
_zntsp_adder = 2.0

trane_zntsp_adder = 2.0 * 5/9 # Trane BACnet data is Celcuis
trane_zntsp_object_type_instance = 'analogValue 1103'

address = "11:20"


# define bacnet app
bacnet = BAC0.lite()
time.sleep(2)

# function to BACnet read and write
def bacnet_requester(action,req_str):
    if action == "read":
        result = bacnet.read(req_str)
        return result
    else:
        result = bacnet.write(req_str)
        print("Write success")


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




