import BAC0, time, csv
from datetime import datetime


# datetime object containing current date and time
now = datetime.now()
dt_string = now.strftime("%m_%d_%Y %H_%M_%S")
print(f"Running NOW date and time is {dt_string}")


# define bacnet app
bacnet = BAC0.lite()
time.sleep(2)


# generates all BACnet addresses some are not VAV boxes
devices = bacnet.whois(global_broadcast=True)
device_mapping = {}
jci_addresses = []
trane_addresses = []



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



# save output for devices discovered
# troubleshoot this list if devices seem like they were skipped
with open('addresses_jci.csv', 'w', newline='') as jci:
  csv_out = csv.writer(jci)
  csv_out.writerows([jci_addresses[index]] for index in range(0, len(jci_addresses)))


with open('addresses_trane.csv', 'w', newline='') as trane:
  csv_out = csv.writer(trane)
  csv_out.writerows([trane_addresses[index]] for index in range(0, len(trane_addresses)))


  bacnet.disconnect()