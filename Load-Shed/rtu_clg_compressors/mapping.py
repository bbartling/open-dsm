"""
CONFIG FILE OF BACnet NETWORK AND
RTU Cooling Compressor Points
This Script Only Adjusts Cooling Compressos

"""


read_url = 'http://localhost:5000/bacnet/read/multiple'
write_url = 'http://localhost:5000/bacnet/write/multiple'
release_url = 'http://localhost:5000/bacnet/write/multiple'


# applying overrides on BACnet priority
write_priority = 12


my_rtu_reads = {
    "read": 
      [    
        {
        "address": "10.200.200.27",
        "object_type": "binaryOutput",
        "object_instance": "3"
        },
        {
        "address": "10.200.200.27",
        "object_type": "binaryOutput",
        "object_instance": "4"
        },
        {
        "address": "10.200.200.27",
        "object_type": "binaryOutput",
        "object_instance": "5"
        },
        {
        "address": "10.200.200.27",
        "object_type": "binaryOutput",
        "object_instance": "6"
        }
      ]
}


three_and_four_off = {
    "write": 
      [    
        {
        "address": "10.200.200.27",
        "object_type": "binaryOutput",
        "object_instance": "5"
        },
        {
        "address": "10.200.200.27",
        "object_type": "binaryOutput",
        "object_instance": "6"
        }
      ]
}


four_off = {
    "write": 
      [    
        {
        "address": "10.200.200.27",
        "object_type": "binaryOutput",
        "object_instance": "6"
        }
      ]
}


three_and_four_relase = {
    "release": 
      [    
        {
        "address": "10.200.200.27",
        "object_type": "binaryOutput",
        "object_instance": "5"
        },
        {
        "address": "10.200.200.27",
        "object_type": "binaryOutput",
        "object_instance": "6"
        }
      ]
}


four_relase = {
    "release": 
      [    
        {
        "address": "10.200.200.27",
        "object_type": "binaryOutput",
        "object_instance": "6"
        }
      ]
}


release_all = {
    "release": 
      [    
        {
        "address": "10.200.200.27",
        "object_type": "binaryOutput",
        "object_instance": "3"
        },
        {
        "address": "10.200.200.27",
        "object_type": "binaryOutput",
        "object_instance": "4"
        },
        {
        "address": "10.200.200.27",
        "object_type": "binaryOutput",
        "object_instance": "5"
        },
        {
        "address": "10.200.200.27",
        "object_type": "binaryOutput",
        "object_instance": "6"
        }
      ]
}
