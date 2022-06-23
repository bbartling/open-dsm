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
PRIORITY = mapping.write_priority
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
        self.clg_compressor_vals = {}
        self.clg_compressor_overridden = []
        self.num_of_clg_stages = 0
        self.num_of_clg_stages_active = 0
        

    async def on_start(self):

        print("On Start Event Start! Applying Overrides!!!")
        logging.info("On Start Event Start! Applying Overrides!!!")

        for devices in HVAC.values():
            for info in devices.values():

                dev_address = info["address"]
                clg_output = info["points"]

                print("The number of clg stages is: ", len(clg_output))
                self.num_of_clg_stages = len(clg_output)

                for clg_stage,clg_point_address in clg_output.items():

                    read_result = await BacNetWorker.do_things(
                            action = "read",
                            dev_address = dev_address,
                            point_info = clg_point_address
                            )

                    print(f"{clg_stage} is: {read_result}")
                    logging.info(f"{clg_stage} is: {read_result}")

                    # store zone sensor readings
                    self.clg_compressor_vals[clg_stage] = read_result


        self.bacnet_service_started = True
        print(self.clg_compressor_vals)
        logging.info(f"{self.clg_compressor_vals}")




    async def get_compresor_readings(self):
        print("Getting Cooling Compressor Readings!!!")

        for devices in HVAC.values():
            for info in devices.values():

                dev_address = info["address"]
                clg_output = info["points"]

                for clg_stage,clg_point_address in clg_output.items():

                    read_result = await BacNetWorker.do_things(
                            action = "read",
                            dev_address = dev_address,
                            point_info = clg_point_address
                            )

                    print(f"{clg_stage} is: {read_result}")
                    logging.info(f"{clg_stage} is: {read_result}")

                    # store zone sensor readings
                    self.clg_compressor_vals[clg_stage] = read_result


        print(self.clg_compressor_vals)
        logging.info(f"{self.clg_compressor_vals}")

        # run every minute
        await asyncio.sleep(60)

 
    async def evauluate_data(self):

        print("Evaluating the compressor data!!!")
        print(f"Overridden zones are {self.clg_compressor_overridden}") 
        logging.info(f"Overridden zones are {self.clg_compressor_overridden}") 

        if not self.clg_compressor_overridden: # list is empty
            print("All zones have been released before event ended")
            logging.info("All zones have been released before event ended")

        else: 
            print("Checking compressor statuses...")
            logging.info("Checking compressor statuses...")

            
            print("self.clg_compressor_vals is: ",self.clg_compressor_vals)

            '''
            •	Check RTU compressor 1-4 status once every 60 seconds
                o	If ALL the “Override Flag” variable on Comp #1 to #4 is OFF (or 0):
                    	IF only Comp#1 ON OR only both Comp#1 And Comp#2 ON: 
                        •	PASS (do nothing)
                    	Eles if Comp#1, #2, and #3 ON AND Comp#4 OFF:
                        •	Override Comp#3 AND #4 OFF
                        •	Set “Override Flag” on Comp #3 and #4 ON (so at the end of the event remember to release both Compressor overrides)
                        •	Wait to the end of the event to release both Comp #3 and #4 overrides
                    	Else if Comp#1, #2, #3 and #4 all are ON:
                        •	Override Comp#4 OFF
                        •	Set “Override Flag” on #4 ON (so at the end of the event remember to release it)
                        •	Wait to the end of the event to release Comp #4 override
                o	Else
                    	Do nothing

            '''

            for clg_stage,status in self.clg_compressor_vals.items():
                print("clg_stage,status is:",clg_stage,status)
                self.num_of_clg_stages_active += 1



        # run data analysis every 3 minutes
        await asyncio.sleep(120)



    async def check_time(self):
        elapsed_time = dt.now() - self.program_start
        if (dt.now() - self.program_start > td(seconds = self.duration_in_seconds)):
            self.event_has_expired = True
            print("Event is DONE!!!, elapsed time: ",elapsed_time)
            logging.info(f"Event is DONE!!!, elapsed time: {elapsed_time}")
        else:
            print("Event is STILL RUNNING!!!, elapsed time: ",elapsed_time)
            logging.info(f"Event is not done!, elapsed time: {elapsed_time}")

        await asyncio.sleep(5)



    async def on_end(self):

        print("On End Releasing All Overrides!")
        logging.info("On End Releasing All Overrides!")

        for devices in HVAC.values():
            for info in devices.values():

                dev_address = info["address"]
                clg_output = info["points"]

                for clg_stage,clg_point_address in clg_output.items():

                    print(f"Releasing {clg_stage} on {clg_point_address}")
                    logging.info(f"Releasing {clg_stage} on {clg_point_address}")
                
                    # release EVERYTHING...
                    release_result = await BacNetWorker.do_things(
                            action = "release",
                            dev_address = dev_address,
                            point_info = clg_point_address,
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


            analysis = asyncio.ensure_future(self.evauluate_data())
            readings = asyncio.ensure_future(self.get_compresor_readings())
            checker = asyncio.ensure_future(self.check_time())

            await analysis # run every 120 seconds  
            await readings # run every 60 seconds   
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