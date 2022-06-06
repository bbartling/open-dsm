# https://gist.github.com/bbartling/2c28d7a3087b9c7f9b8bb9d30c30e773

import asyncio
from datetime import datetime as dt
from datetime import timedelta as td

import mapping
from bacnet_actions import BacNetWorker
import logging



logging.basicConfig(
        filename="event.log",
        level=logging.INFO)


# import config file of device address & setpoint adj
HVAC = mapping.nested_group_map
SETPOINT_ADJ = mapping.setpoint_adj
PRIORITY = mapping.write_priority
HI_TEMP_SETPOINT = mapping.zone_hi_temp_release_setpoint
EVENT_DURATION_MINUTES = mapping.event_duration



class Program:
    def __init__(self):
        self.duration_in_seconds = EVENT_DURATION_MINUTES * 60
        self.program_start = dt.now()
        self.event_has_expired = False
        self.tasks_cancelled_success = False
        self.bacnet_service_started = False

        # store zone sensor readings
        # used for monitoring 
        self.zone_sensor_vals = {}
        self.zones_overridden = []

        

    async def on_start(self):

        print("On Start Event Start! Applying Overrides!!!")
        logging.info("On Start Event Start! Applying Overrides!!!")

        for group,devices in HVAC.items():
            for device,info in devices.items():
                dev_address = info["address"]
                sensor = info["points"]["zone_sensor"]

                read_result = await BacNetWorker.do_things(
                        action = "read",
                        dev_address = dev_address,
                        point_info = sensor
                        )

                print(f"{device} zone sensor BACnet read is: {read_result}")
                logging.info(f"{device} zone sensor BACnet read is: {read_result}")

                # store zone sensor readings
                self.zone_sensor_vals[device] = read_result


        self.bacnet_service_started = True
        print(self.zone_sensor_vals)
        logging.info(f"{self.zone_sensor_vals}")


        for group,devices in HVAC.items():
            for device,info in devices.items():
                dev_address = info["address"]
                setpoint = info["points"]["zone_setpoint"]
                write_value = self.zone_sensor_vals[device] + SETPOINT_ADJ

                write_result = await BacNetWorker.do_things(
                        action = "write",
                        dev_address = dev_address,
                        point_info = setpoint,
                        value = write_value,
                        priority = PRIORITY
                        )

                print(f"{device} zone setpoint BACnet write is: {write_result} with {write_value}")
                logging.info(f"{device} zone setpoint BACnet write is: {write_result} with {write_value}")

                self.zones_overridden.append(device)



    async def get_sensor_readings(self):
        print("Getting sensor readings!!!")

        for group,devices in HVAC.items():
            for device,info in devices.items():
                dev_address = info["address"]
                sensor = info["points"]["zone_sensor"]

                read_result = await BacNetWorker.do_things(
                        action = "read",
                        dev_address = dev_address,
                        point_info = sensor
                        )

                print(f"{device} zone sensor BACnet read is: {read_result}")
                logging.info(f"{device} zone sensor BACnet read is: {read_result}")

                # store zone sensor readings
                self.zone_sensor_vals[device] = read_result

        print("Zone performance is ",self.zone_sensor_vals)
        logging.info(f"Zone performance is {self.zone_sensor_vals}")

        # run every minute
        await asyncio.sleep(60)

 
    async def evauluate_data(self):
        print("Evaluating the data!!!")
        logging.info(f"Overridden zones are {self.zones_overridden}") 
        print(f"Overridden zones are {self.zones_overridden}") 
        logging.info(f"Overridden zones are {self.zones_overridden}") 

        if not self.zones_overridden: # list is empty
            print("All zones have been released before event ended")
            logging.info("All zones have been released before event ended")

        else: 
            print("Checking for hi temps!!!")
            logging.info("Checking for hi temps!!!")

            for zone,temp in self.zone_sensor_vals.items():
                print(zone,temp)
                if (
                    temp >= HI_TEMP_SETPOINT
                    and zone in self.zones_overridden
                ):
                    print(f"Zone {zone} could be released!")
                    logging.info(f"Zone {zone} could be released!")

                    # if True lookup BACnet address
                    for group,devices in HVAC.items():
                        for device,info in devices.items():
                            dev_address = info["address"]

                            # setpoint is the original point overridden
                            setpoint = info["points"]["zone_setpoint"]

                            if device == zone:
                                print(f"found address of {dev_address} for {zone}")
                                logging.info("lets release it back the BAS!")
                                print("lets release it back the BAS!")
                                logging.info("lets release it back the BAS!")
                            

                                release_result = await BacNetWorker.do_things(
                                        action = "release",
                                        dev_address = dev_address,
                                        point_info = setpoint,
                                        priority = PRIORITY
                                        )

                                print(f"{zone} release status is: {release_result}")
                                logging.info(f"{zone} release status is: {release_result}")
                                self.zones_overridden.remove(zone)

        # run data analysis every 3 minutes
        await asyncio.sleep(120)



    async def check_time(self):
        elapsed_time = dt.now() - self.program_start
        if (dt.now() - self.program_start > td(seconds = self.duration_in_seconds)):
            self.event_has_expired = True
            print("Event is DONE!!!, elapsed time: ",elapsed_time)
            logging.info(f"Event is DONE!!!, elapsed time: {elapsed_time}")
        else:
            print("Event is not done!, elapsed time: ",elapsed_time)
            logging.info(f"Event is not done!, elapsed time: {elapsed_time}")

        await asyncio.sleep(5)



    async def on_end(self):

        print("On End Releasing All Overrides!")
        logging.info("On End Releasing All Overrides!")

        for group,devices in HVAC.items():
            for device,info in devices.items():
                dev_address = info["address"]

                # setpoint is the original point overridden
                setpoint = info["points"]["zone_setpoint"]

                
                # release EVERYTHING...
                release_result = await BacNetWorker.do_things(
                        action = "release",
                        dev_address = dev_address,
                        point_info = setpoint,
                        priority = PRIORITY
                        )

        print("Release All Success!")
        logging.info("Release All Success!")

        if self.bacnet_service_started == True:
            kill_status = await BacNetWorker.do_things(
                        action = "kill_switch"
                        )

            print("BACnet service stopped: ",kill_status)
            logging.info(f"BACnet service stopped: {kill_status}")



    async def main(self):
        # script starts, do only once self.on_start()
        await self.on_start()
        print("On Start Done!")
        logging.info("On Start Done!")

        while not self.tasks_cancelled_success:

            readings = asyncio.ensure_future(self.get_sensor_readings())
            analysis = asyncio.ensure_future(self.evauluate_data())
            checker = asyncio.ensure_future(self.check_time())

            await readings # run every 60 seconds
            await analysis # run every 120 seconds     
            await checker  # run every 5 seconds
                
                
            if self.event_has_expired:
                # close other tasks before final shutdown
                readings.cancel()
                analysis.cancel()
                checker.cancel()
                self.tasks_cancelled_success = True
                print("Asyncio Tasks All Cancelled Success!")
                logging.info("Asyncio Tasks All Cancelled Success!")

        # script ends, do only once self.on_end() when even is done
        await self.on_end()
        print("on_end called!")
        logging.info("on_end called!")


async def main():
    program = Program()
    await program.main()



if __name__ == "__main__":
    asyncio.run(main())