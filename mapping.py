"""
CONFIG FILE OF BACnet NETWORK AND
LOAD SHED ADJ SETPOINT

"""
# event duration in minutes
event_duration = 6

# adjust zone setpoints
setpoint_adj = 3.0

# applying overrides on BACnet priority
write_priority = 9

# if a zones rises above this temp
# release this zone even if the event isnt over
zone_hi_temp_release_setpoint = 75.0


nested_group_map = {"floor1_north" : {"VMA-1-1": {
                                        "address" :  "12345:2", 
                                        "points": {"zone_sensor" : "analogValue 806",
                                                   "zone_setpoint" : "analogValue 302",
                                                   "reheat_coil" : "analogValue 301"}},
                                        "VMA-1-2": {
                                        "address" :  "12345:2", 
                                        "points": {"zone_sensor" : "analogInput 3",
                                                   "zone_setpoint" : "analogValue 302",
                                                   "reheat_coil" : "analogValue 301"}},
                                        "VMA-1-3": {
                                        "address" :  "12345:2", 
                                        "points": {"zone_sensor" : "analogInput 2",
                                                   "zone_setpoint" : "analogValue 302",
                                                   "reheat_coil" : "analogValue 301"}},
                                        "VMA-1-4": {
                                        "address" :  "12345:2", 
                                        "points": {"zone_sensor" : "analogInput 3",
                                                   "zone_setpoint" : "analogValue 302",
                                                   "reheat_coil" : "analogValue 301"}},
                                        "VMA-1-5": {
                                        "address" :  "12345:2", 
                                        "points": {"zone_sensor" : "analogInput 2",
                                                   "zone_setpoint" : "analogValue 302",
                                                   "reheat_coil" : "analogValue 301"}},
                                        "VMA-1-7": {
                                        "address" :  "12345:2", 
                                        "points": {"zone_sensor" : "analogInput 3",
                                                   "zone_setpoint" : "analogValue 302",
                                                   "reheat_coil" : "analogValue 301"}},
                                        "VMA-1-10": {
                                        "address" :  "12345:2", 
                                        "points": {"zone_sensor" : "analogInput 3",
                                                   "zone_setpoint" : "analogValue 302",
                                                   "reheat_coil" : "analogValue 301"}},
                                        "VMA-1-11": {
                                        "address" :  "12345:2", 
                                        "points": {"zone_sensor" : "analogInput 3",
                                                   "zone_setpoint" : "analogValue 302",
                                                   "reheat_coil" : "analogValue 301"}},      
                    },

                    "floor1_south" : {"VMA-1-6": {
                                        "address" :  "12345:2", 
                                        "points": {"zone_sensor" : "analogValue 806",
                                                   "zone_setpoint" : "analogValue 302",
                                                   "reheat_coil" : "analogValue 301"}},
                                        "VMA-1-8": {
                                        "address" :  "12345:2", 
                                        "points": {"zone_sensor" : "analogInput 3",
                                                   "zone_setpoint" : "analogValue 302",
                                                   "reheat_coil" : "analogValue 301"}},
                                        "VMA-1-9": {
                                        "address" :  "12345:2", 
                                        "points": {"zone_sensor" : "analogInput 2",
                                                   "zone_setpoint" : "analogValue 302",
                                                   "reheat_coil" : "analogValue 301"}},
                                        "VMA-1-7": {
                                        "address" :  "12345:2", 
                                        "points": {"zone_sensor" : "analogInput 3",
                                                   "zone_setpoint" : "analogValue 302",
                                                   "reheat_coil" : "analogValue 301"}},
                                        "VMA-1-12": {
                                        "address" :  "12345:2", 
                                        "points": {"zone_sensor" : "analogInput 2",
                                                   "zone_setpoint" : "analogValue 302",
                                                   "reheat_coil" : "analogValue 301"}},
                                        "VMA-1-13": {
                                        "address" :  "12345:2", 
                                        "points": {"zone_sensor" : "analogInput 3",
                                                   "zone_setpoint" : "analogValue 302",
                                                   "reheat_coil" : "analogValue 301"}},
                                        "VMA-1-14": {
                                        "address" :  "12345:2", 
                                        "points": {"zone_sensor" : "analogInput 3",
                                                   "zone_setpoint" : "analogValue 302",
                                                   "reheat_coil" : "analogValue 301"}},
                                        "VMA-1-15": {
                                        "address" :  "12345:2", 
                                        "points": {"zone_sensor" : "analogInput 3",
                                                   "zone_setpoint" : "analogValue 302",
                                                   "reheat_coil" : "analogValue 301"}},
                                        "VMA-1-16": {
                                        "address" :  "12345:2", 
                                        "points": {"zone_sensor" : "analogInput 3",
                                                   "zone_setpoint" : "analogValue 302",
                                                   "reheat_coil" : "analogValue 301"}}, 
                    },

                    "floor2_north" : {"VMA-2-1": {
                                        "address" :  "12345:2", 
                                        "points": {"zone_sensor" : "analogValue 806",
                                                   "zone_setpoint" : "analogValue 302",
                                                   "reheat_coil" : "analogValue 301"}},
                                        "VMA-2-2": {
                                        "address" :  "12345:2", 
                                        "points": {"zone_sensor" : "analogInput 3",
                                                   "zone_setpoint" : "analogValue 302",
                                                   "reheat_coil" : "analogValue 301"}},
                                        "VMA-2-3": {
                                        "address" :  "12345:2", 
                                        "points": {"zone_sensor" : "analogInput 2",
                                                   "zone_setpoint" : "analogValue 302",
                                                   "reheat_coil" : "analogValue 301"}},
                                        "VMA-2-4": {
                                        "address" :  "12345:2", 
                                        "points": {"zone_sensor" : "analogInput 3",
                                                   "zone_setpoint" : "analogValue 302",
                                                   "reheat_coil" : "analogValue 301"}},
                                        "VMA-2-5": {
                                        "address" :  "12345:2", 
                                        "points": {"zone_sensor" : "analogInput 2",
                                                   "zone_setpoint" : "analogValue 302",
                                                   "reheat_coil" : "analogValue 301"}},
                                        "VMA-2-6": {
                                        "address" :  "12345:2", 
                                        "points": {"zone_sensor" : "analogInput 3",
                                                   "zone_setpoint" : "analogValue 302",
                                                   "reheat_coil" : "analogValue 301"}},
                                        "VMA-2-12": {
                                        "address" :  "12345:2", 
                                        "points": {"zone_sensor" : "analogInput 3",
                                                   "zone_setpoint" : "analogValue 302",
                                                   "reheat_coil" : "analogValue 301"}},
                                        "VMA-2-7": {
                                        "address" :  "12345:2", 
                                        "points": {"zone_sensor" : "analogInput 3",
                                                   "zone_setpoint" : "analogValue 302",
                                                   "reheat_coil" : "analogValue 301"}},

                },

                    "floor2_south" : {"VMA-2-8": {
                                        "address" :  "12345:2", 
                                        "points": {"zone_sensor" : "analogValue 806",
                                                   "zone_setpoint" : "analogValue 302",
                                                   "reheat_coil" : "analogValue 301"}},
                                        "VMA-2-9": {
                                        "address" :  "12345:2", 
                                        "points": {"zone_sensor" : "analogInput 3",
                                                   "zone_setpoint" : "analogValue 302",
                                                   "reheat_coil" : "analogValue 301"}},
                                        "VMA-2-10": {
                                        "address" :  "12345:2", 
                                        "points": {"zone_sensor" : "analogInput 2",
                                                   "zone_setpoint" : "analogValue 302",
                                                   "reheat_coil" : "analogValue 301"}},
                                        "VMA-2-11": {
                                        "address" :  "12345:2", 
                                        "points": {"zone_sensor" : "analogInput 3",
                                                   "zone_setpoint" : "analogValue 302",
                                                   "reheat_coil" : "analogValue 301"}},
                                        "VMA-2-13": {
                                        "address" :  "12345:2", 
                                        "points": {"zone_sensor" : "analogInput 2",
                                                   "zone_setpoint" : "analogValue 302",
                                                   "reheat_coil" : "analogValue 301"}},
                                        "VMA-2-14": {
                                        "address" :  "12345:2", 
                                        "points": {"zone_sensor" : "analogInput 3",
                                                   "zone_setpoint" : "analogValue 302",
                                                   "reheat_coil" : "analogValue 301"}},
                },

}