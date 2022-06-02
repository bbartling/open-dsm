"""
CONFIG FILE OF BACnet NETWORK AND
LOAD SHED ADJ SETPOINT

"""


setpoint_adj = 0.03

nested_group_map = {
            'group_l1n' : {
            'VMA-1-1': '14',
            'VMA-1-2': '13',
            'VMA-1-3': '15',
            'VMA-1-4': '11',
            'VMA-1-5': '9',
            'VMA-1-7': '7',
            'VMA-1-10': '21',
            'VMA-1-11': '16'
            },
            'group_l1s' : {
            'VMA-1-6': '8',
            'VMA-1-8': '11002', # formerly JCI #8
            'VAV 1-9': '11007',
            'VMA-1-7': '10', # changed name to VAV 7
            'VMA-1-12': '19',
            'VMA-1-13': '20',
            'VMA-1-14': '37',
            'VMA-1-15': '38',
            'VMA-1-16': '39'
            },
            'group_l2n' : {
            'VAV-2-1': '12032',
            'VAV-2-2': '12033',
            'VMA-2-3': '31',
            'VMA-2-4': '29',
            'VAV-2-5': '12028',
            'VMA-2-6': '27',
            'VMA-2-12': '12026', # formerly JCI #26
            'VMA-2-7': '30'
            },
            'group_l2s' : {
            'VMA-2-8': '34',
            'VAV-2-9': '12035',
            'VMA-2-10': '36',
            'VMA-2-11': '25',
            'VMA-2-13': '12023',  # formerly JCI #23
            'VMA-2-14': '24',
            'VAV 2-12': '12026',
            }
        }



