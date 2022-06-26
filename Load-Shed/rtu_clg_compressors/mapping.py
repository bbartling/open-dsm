"""
CONFIG FILE OF BACnet NETWORK AND
RTU Cooling Compressor Points
This Script Only Adjusts Cooling Compressos

"""
# event duration in minutes
event_duration = 10


# applying overrides on BACnet priority
write_priority = 12



my_rtu_read = {
  "devices": {
    "cooling_stage_1": {
      "address": "10.200.200.27",
      "object_type": "binaryOutput",
      "object_instance": "3"
    },
    "cooling_stage_2": {
      "address": "10.200.200.27",
      "object_type": "binaryOutput",
      "object_instance": "4"
    },
    "cooling_stage_3": {
      "address": "10.200.200.27",
      "object_type": "binaryOutput",
      "object_instance": "5"
    },
    "cooling_stage_4": {
      "address": "10.200.200.27",
      "object_type": "binaryOutput",
      "object_instance": "6"
    }
  }
}


my_rtu_write = {
  "devices": {
    "cooling_stage_1": {
      "address": "10.200.200.27",
      "object_type": "binaryOutput",
      "object_instance": "3"
    },
    "cooling_stage_2": {
      "address": "10.200.200.27",
      "object_type": "binaryOutput",
      "object_instance": "4"
    },
    "cooling_stage_3": {
      "address": "10.200.200.27",
      "object_type": "binaryOutput",
      "object_instance": "5"
    },
    "cooling_stage_4": {
      "address": "10.200.200.27",
      "object_type": "binaryOutput",
      "object_instance": "6"
    }
  }
}