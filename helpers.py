import BAC0
import time


bacnet = BAC0.lite()
time.sleep(5) #warm up timer

#simulate BACnet read of setpoints
#import random


class Helpers():

    # JCI BACNET WRITE ON PRIORITY 10
    # <address> <pointType> <pointAdress> presentValue <value> - <bacnetPriority>
    def write_jci_zone_setpoints(device,setpoint):
        try:
            jci_write = f'{device} anlogValue 1103 presentValue {setpoint} - 10'
            bacnet.write(jci_write)
            print("Write Success JCI VAV: ",jci_write)

        except:
            print("JCI Write Error: ",jci_write)


    # TRANE BACNET WRITE ON PRIORITY 10 anlogValue 27
    # <address> <pointType> <pointAdress> presentValue <value> - <bacnetPriority>
    def write_trane_zone_setpoints(device,setpoint):
        try:
            trane_write = f'{device} anlogValue 27 presentValue {setpoint} - 10'
            bacnet.write(trane_write)
            print("Write Success Trane VAV: ",trane_write)
        except:
            print("Trane Write Error: ",trane_write)        


    # JCI BACNET READ anlogValue 1103
    def read_jci_zone_setpoints(device):
        try:
            jci_read = f'{device} anlogValue 1103 presentValue'
            bacnet.read(jci_read)
            #jci_read = random.randrange(65, 75)
            print(f"Read Success JCI VAV: {device} is {jci_read} degrees F")
            return jci_read
        
        except:
            print("JCI Read Error: ",jci_read)
            return "error"
        

    # TRANE BACNET READ anlogValue 27            
    def read_trane_zone_setpoints(device):
        try:
            trane_read = f'{device} anlogValue 27 presentValue'
            bacnet.read(trane_read)
            #trane_read = random.randrange(65, 75)
            print(f"Read Success Trane VAV: {device} is {trane_read} degrees F")
            return trane_read

        except:
            print("Trane VAV Error: ",trane_read)
            return "error"


    # TRANE BACNET RELEASE PRIORITY 10 anlogValue 27
    # <address> <pointType> <pointAdress> presentValue <null> - <priority>
    def release_override_trane(device):
        try:
            release_trane = f'{device} anlogValue 27 presentValue null - 10'
            bacnet.write(release_trane)
            print("Release Success Trane VAV: ",release_trane)
        except:
            print("Trane VAV Release Error: ",release_trane)


    # JCI BACNET RELEASE PRIORITY 10 anlogValue 1103
    # <address> <pointType> <pointAdress> presentValue <null> - <priority>
    def release_override_jci(device):
        try:
            release_jci = f'{device} anlogValue 1103 presentValue null - 10'
            bacnet.write(release_jci)
            print("Release Success JCI VAV: ",release_jci)
        except:
            print("JCI VAV Release Error: ",release_jci)


    # Gracefully hit the kill switch via BAC0 recommendations
    def kill_switch():
        bacnet.disconect()
        print("BACnet kill switch success")
