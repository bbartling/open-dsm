import mapping
import time
from helpers import Helpers as f

# import config file of device address & setpoint adj
devices = mapping.nested_group_map
setpoint_adj = mapping.setpoint_adj


read_results = {}
for group,vavs in devices.items():

    for vav,address in vavs.items():
        if int(address) > 10000:
            # get BACnet read of temp setpoint
            read_result = f.read_trane_zone_setpoints(address)
        else:
            read_result = f.read_jci_zone_setpoints(address)

        # create new dict keys,values
        read_results[address] = read_result

# Compile BACnet Read Results in new dict
print("read_results ",read_results)


# Modify current setpoints with adj values
for address,setpoint in read_results.items():
    if not isinstance(setpoint, str): # string is error
        if int(address) > 10000:
            f.write_trane_zone_setpoints(address,
                                         setpoint+setpoint_adj)
        else:
            f.write_jci_zone_setpoints(address,
                                       setpoint+setpoint_adj)
    else:
        print(f"passing BACnet write on {address} because of READ 'error'")


time.sleep(5)
f.kill_switch()
