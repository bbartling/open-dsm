import BAC0
import time


#bacnet = BAC0.lite()
time.sleep(5) #warm up timer

#simulate BACnet read of setpoints
import random


class Helpers():

    # JCI BACNET WRITE ON PRIORITY 10
    # <address> <pointType> <pointAdress> presentValue <value> - <bacnetPriority>
    def write_jci_zone_setpoints(device,setpoint):
        try:
            jci_write = f'{device} anlogValue 22 presentValue {setpoint} - 10'
            print("Write Success VAV: ",jci_write)
            #bacnet.write(jci_write)
        except:
            print("Error: ",jci_write)

    # TRANE BACNET WRITE ON PRIORITY 10
    # <address> <pointType> <pointAdress> presentValue <value> - <bacnetPriority>
    def write_trane_zone_setpoints(device,setpoint):
        try:
            trane_write = f'{device} anlogValue 99 presentValue {setpoint} - 10'
            #bacnet.write(trane_write)
            print("Write Success VAV: ",trane_write)
        except:
            print("Error: ",trane_write)        

    # JCI BACNET READ
    def read_jci_zone_setpoints(device):
        try:
            #jci_read = f'{device} anlogValue 59 presentValue'
            #bacnet.read(jci_write)
            jci_read = random.randrange(65, 75)
            print(f"Read Success VAV: {device} is {jci_read} degrees F")
            return jci_read
        
        except:
            print("Error: ",jci_read)
            return "error"
        
    # TRANE BACNET READ            
    def read_trane_zone_setpoints(device):
        try:
            #trane_read = f'{device} anlogValue 59 presentValue'
            #bacnet.read(trane_write)
            trane_read = random.randrange(65, 75)
            print(f"Read Success VAV: {device} is {trane_read} degrees F")
            return trane_read
        except:
            print("Error: ",trane_read)
            return "error"


    # BACNET RELEASE PRIORITY 10
    # <address> <pointType> <pointAdress> presentValue <null> - <priority>
    def release_override(device):
        try:
            release = f'{device} anlogValue 99 presentValue null - 10'
            #bacnet.write(trane_write)
            print("Release Success VAV: ",release)
        except:
            print("Release Error: ",release)


    # Gracefully hit the kill switch
    def kill_switch():
        #bacnet.disconect()
        print("BACnet kill switch success")
