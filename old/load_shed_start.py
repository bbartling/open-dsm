
import mapping
import asyncio
from bacnet_actions import BacNetWorker

# import config file of device address & setpoint adj
devices = mapping.nested_group_map
setpoint_adj = mapping.setpoint_adj
priority = mapping.setpoint_adj




read_results = {}
async def read_zone_temps():
    for group,vavs in devices.items():
        for vav,point in vavs.items():
            while True:
                await asyncio.sleep(10)

                print("ZONE TEMPS READING!!")

                """
                read_pv = await BacNetWorker.do_things(
                "read",
                point['address'],
                point['object_type'],
                point['object_instance']
                )
                """


async def check_event_status():



def main():
    loop = asyncio.get_event_loop()
    readZoneTemps = asyncio.ensure_future(read_zone_temps())
    loop.run_until_complete(readZoneTemps)

    checkEventStatus = asyncio.ensure_future(check_event_status())
    loop.run_until_complete(checkEventStatus)



if __name__ == '__main__':
    main()