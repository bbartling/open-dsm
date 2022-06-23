import BAC0
import time


# define BAC0 app
#STATIC_BACNET_IP = '192.168.0.103/24'
#bacnet = BAC0.lite(IP=STATIC_BACNET_IP)
bacnet = BAC0.lite()



class BacNetWorker():
    async def do_things(**kwargs):

        action = kwargs.get('action', None)
        dev_address = kwargs.get('dev_address', None)
        object_type_instance = kwargs.get('point_info', None)
        value = kwargs.get('value', None)
        priority = kwargs.get('priority', None)

        if action == "read":
            try:
                read_vals = f'{dev_address} {object_type_instance} presentValue'
                print("Excecuting BACnet read statement:", read_vals)
                read_result = bacnet.read(read_vals)
                if isinstance(read_result, str):
                    pass
                else:
                    read_result = round(read_result,2)
                return read_result
            except Exception as error:
                return f"error: {error}"
      

        elif action == "write":
            try:
                write_vals = f'{dev_address} {object_type_instance} presentValue {value} - {priority}'
                bacnet.write(write_vals)
                return "success"          
            except Exception as error:
                return f"error: {error}"


        elif action == "release":
            try:    
                release_vals = f'{dev_address} {object_type_instance} presentValue null - {priority}'
                print("Excecuting BACnet release statement:", release_vals)
                bacnet.write(release_vals)
                return "success" 
            except Exception as error:
                return f"error: {error}"
                

        elif action == "kill_switch":
            try:    
                bacnet.disconnect()
                return "success"
            except Exception as error:
                return f"error! - {error}"
                
        else:
            return "BACnet server error"


