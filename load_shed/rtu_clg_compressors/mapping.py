"""
CONFIG FILE OF BACnet NETWORK AND
RTU Cooling Compressor Points
This Script Only Adjusts Cooling Compressos

"""
# event duration in minutes
event_duration = 2


# applying overrides on BACnet priority
write_priority = 8




nested_group_map = {"air_side_systems" : {"rtu_1": {
                                        "address" : "10.200.200.27", 
                                        "points": {"cooling_stage_1" : "binaryOutput 3",
                                                   "cooling_stage_2" : "binaryOutput 4",
                                                   "cooling_stage_3" : "binaryOutput 5",
                                                   "cooling_stage_4" : "binaryOutput 6"}},

                },

}