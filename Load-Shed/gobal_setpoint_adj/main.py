import BAC0, time, random


bacnet = BAC0.lite()
time.sleep(2)


devices = bacnet.whois(global_broadcast=True)
device_mapping = {}
addresses = []
for device in devices:
    if isinstance(device, tuple):
        device_mapping[device[1]] = device[0]
        print("Detected device %s with address %s" % (str(device[1]), str(device[0])))
print(device_mapping)
print((str(len(device_mapping)) + " devices discovered on network."))

for bacnet_inst,address in device_mapping.items():
    if bacnet_inst < 100: #JCI boxes have inst ID less than 100 on this site
        addresses.append(address)

print("addresses is: ",addresses)


'''

addresses = [

        "11:2","11:4","11:5","12:22","11:7",
        "12:23","11:8","11:9","12:24","11:10",
        "12:25","11:11","12:26","12:27","11:12",
        "12:28","12:29","11:13","12:30","11:14",
        "12:31","11:15","12:32","11:16","12:33",
        "11:17","12:34","12:35","11:18","11:39",
        "11:19","12:36","11:20","12:40",
        "11:21","12:41","11:37","11:38",
        
        ]
'''

# change VAV box space setpoint MIN MAX VALUES
object_type = 'analogValue'
object_instance = '1103'
priority = 'default'
min_value = 55.0
max_value = 85.0


for address in addresses:

    try:
        print("Doing DEVICE: ",address)

        read_minPresValue = f'{address} {object_type} {object_instance} minPresValue'
        check_min = bacnet.read(read_minPresValue)
        print("check_min: ",check_min)

        if check_min != min_value:
            write_minPresValue = f'{address} {object_type} {object_instance} minPresValue {min_value} - {priority}'
            write_min = bacnet.write(write_minPresValue)
            print(write_min)

            read_minPresValue = f'{address} {object_type} {object_instance} minPresValue'
            check_min = bacnet.read(read_minPresValue)
            print("check_min: ",check_min)

        else:
            print("MINS are good on device: {address}")


        read_maxPresValue = f'{address} {object_type} {object_instance} maxPresValue'
        check_max = bacnet.read(read_maxPresValue)
        print("check_max: ",check_max)

        if check_max != max_value:
            write_maxPresValue = f'{address} {object_type} {object_instance} maxPresValue {max_value} - {priority}'
            write_max = bacnet.write(write_maxPresValue)
            print(write_max)

            read_maxPresValue = f'{address} {object_type} {object_instance} maxPresValue'
            check_max = bacnet.read(read_maxPresValue)
            print("check_max: ",check_max)

        else:
            print("MAX are good on device: {address}")
                  
        print("*********************************")

    except Exception as error:
        print(f"OOF error on device {address}: {error}")


print("ALL DIGITY DONE!!!")
bacnet.disconnect()



