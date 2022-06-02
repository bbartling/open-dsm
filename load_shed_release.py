import mapping
from helpers import Helpers as f
import time



# import config file of device address & setpoint adj
devices = mapping.nested_group_map
setpoint_adj = mapping.setpoint_adj


for group,vavs in devices.items():
    for vav,address in vavs.items():
        f.release_override(address)


time.sleep(5)
f.kill_switch()
