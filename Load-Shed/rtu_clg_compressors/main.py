import aiohttp
import asyncio
from datetime import datetime, timezone, timedelta
import aiocron



# replace with real open ADR event when it slides in
# use for testing purposes
dummy_event = {
	"active_period": {
		"dstart": datetime.now(timezone.utc),
		"duration": 120,
		"notification": "null",
		"ramp_up": "null",
		"recovery": "null",
		"tolerance": {
			"tolerate": {
				"startafter": "null"
			}
		}
	},
	"event_signals": [
		{
			"current_value": 2.0,
			"intervals": [
				{
                "duration": timedelta(minutes=5),
                                    #"dtstart": datetime.now(timezone.utc)+timedelta(minutes=5),
                                    #"dtstart": datetime(2022, 6, 6, 14, 30, 0, 0, tzinfo=timezone.utc),
                                    "dtstart": datetime.now(timezone.utc) + timedelta(seconds=30),
                "signal_payload": 1.0,
                "uid": 0
				}
			],
			"signal_id": "SIG_01",
			"signal_name": "SIMPLE",
			"signal_type": "level"
		}
	],
	"response_required": "always",
	"target_by_type": {
		"ven_id": [
			"slipstream-ven4"
		]
	},
	"targets": [
		{
			"ven_id": "slipstream-ven4"
		}
	]
}





class Program:
    def __init__(self):
        self.compressor_count = 0
        self.cron_service_started = False
        self.cron_service = aiocron.crontab('*/1 * * * *',
                            func=self.evaluate_data,
                            start=False)


    def event_checkr(self):
        now_utc = datetime.now(timezone.utc)
        if now_utc >= self.adr_start and now_utc <= self.adr_event_ends: #future time is greater
            
            return True
        else:
            return False


    def process_adr_event(self,event):

        now_utc = datetime.now(timezone.utc)
        signal = event['event_signals'][0]
        intervals = signal['intervals']

        # loop through open ADR payload
        for interval in intervals:
            self.adr_start = interval['dtstart']
            self.adr_payload_value = interval['signal_payload']
            self.adr_duration = interval['duration']

            self.adr_event_ends = self.adr_start + self.adr_duration

    
    async def get_data(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(read_url, json=my_rtu_reads) as resp:
                print(resp.status)
                resp_data = await resp.json()
                print("resp_data: ",resp_data)
                
                counter = 0
                for obj in resp_data:
                    if obj == 'active':
                        counter += 1       
                self.compressor_count = counter
                print("Active Cooling Count: ", self.compressor_count)


    async def turn_stages_off(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(write_url, json=write_url) as resp:
                
                print(resp.status)
                resp_data = await resp.json()


                

    async def evaluate_data(self):
        print("EVALUATE DATA CALLED, HOUR IS: ", datetime.now(timezone.utc))

        await self.get_data()
        
        if self.compressor_count == 0:
            print("No compressors are running, passing....")
        elif self.compressor_count == 3:
            print("3 stages of cooling are running, overriding stage 3 and 4 OFF....")
        elif self.compressor_count == 4:
            print("4 stages of cooling are running, overriding stage ONLY stage 4 OFF....")
        else:
            print("Not enough cooling running to override OFF for load shed")      

        #await asyncio.sleep(60)

            
            
async def main():
    loop = asyncio.get_running_loop()
    program = Program()

    # process dummy event
    program.process_adr_event(dummy_event)

    while True:
        
        # run event checker in the default loop's executor:
        event_is_true = await loop.run_in_executor(None, program.event_checkr)

        print("program.cron_service_started: ",program.cron_service_started)
        print("event_is_true: ",event_is_true)
        
        if event_is_true and not program.cron_service_started:
            program.cron_service.start()
            program.cron_service_started = True
            print("cron start!!")

        elif event_is_true and program.cron_service_started:
            pass

        elif not event_is_true and program.cron_service_started:
            program.cron_service.stop()
            program.cron_service_started = False
            print("cron stop!!")
            
        else:
            pass
            
        await asyncio.sleep(5)  


asyncio.run(main())






