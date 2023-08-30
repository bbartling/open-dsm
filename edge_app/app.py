import asyncio
import logging
from logging.handlers import TimedRotatingFileHandler
import BAC0
from bacpypes.primitivedata import Real
from BAC0.core.devices.local.models import analog_value
from aiohttp import web
import os


# Use a local REST API to share DR signal to OT LAN
USE_REST = True

# BACnet NIC setup:
IP_ADDRESS = "192.168.0.109"
BACNET_INST_ID = 341234
SUBNET_MASK_CIDAR = 24
PORT = "47820"
BBMD = None

# Logging setup
SAVE_LOGS_TO_FILE = True

if SAVE_LOGS_TO_FILE:
    script_directory = os.path.dirname(os.path.abspath(__file__))
    log_filename = os.path.join(script_directory, "app_log.log")
    logging.basicConfig(level=logging.INFO)
    log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler = TimedRotatingFileHandler(
        log_filename, when="midnight", interval=1, backupCount=7
    )
    file_handler.setFormatter(log_formatter)
    logging.getLogger("").addHandler(file_handler)


class BACnetApp:
    @classmethod
    async def create(cls):
        self = BACnetApp()
        self.bacnet = await asyncio.to_thread(
            BAC0.lite,
            ip=IP_ADDRESS,
            port=PORT,
            mask=SUBNET_MASK_CIDAR,
            deviceId=BACNET_INST_ID,
            bbmdAddress=BBMD,
        )
        self.current_power_level = 0.0
        self.future_power_level = 0
        self.model_error = None
        _new_objects = self.create_objects()
        _new_objects.add_objects_to_application(self.bacnet)
        logging.info("BACnet APP Created Success!")
        return self

    def create_objects(self):
        _new_objects = analog_value(
            name="current-power-level-in",
            description="Writeable point for electric meter reading",
            presentValue=0,
            is_commandable=True,
        )
        _new_objects = analog_value(
            name="future-power-level-out",
            description="one hour future power level",
            presentValue=0,
            is_commandable=False,
        )
        return _new_objects

    async def get_future_power_meter_reading(self, request):
        logging.info("Received request.")
        payload = {"future_power_level": self.future_power_level}
        logging.info(f"Returning payload: {payload}")
        return web.json_response(payload)

    async def start_rest_api(self):
        app = web.Application()
        app.router.add_get("/api/future-power-level-out", self.get_last_server_payload)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", 8080)  # Bind to all network interfaces
        await site.start()

    async def update_bacnet_api(self, value):
        electric_meter_current = self.bacnet.this_application.get_object_name(
            "current-power-level-in"
        )
        electric_meter_current.presentValue = value

        # default value is a BACnet primitive data type called Real that
        if isinstance(electric_meter_current.presentValue, Real):
            self.current_power_level = electric_meter_current.presentValue.value
        else:
            self.current_power_level = electric_meter_current.presentValue

        electric_meter_future = self.bacnet.this_application.get_object_name(
            "future-power-level-out"
        )
        electric_meter_future.presentValue = Real(value)

        logging.info(
            f"Future Power Level: {self.future_power_level}, Current Power Level: {self.current_power_level}, Error: {self.model_error}"
        )

    async def keep_baco_alive(self):
        counter = 0
        while True:
            counter += 1
            await asyncio.sleep(0.01)
            if counter == 100:
                counter = 0
                async with self.server_check_lock:
                    await self.update_bacnet_api(self.future_power_level)

    async def predict_future_power(self):
        while True:
            try:
                return self.current_power_level

            except Exception as e:
                logging.error(f"Error forecast value: {e}")

            await asyncio.sleep()


async def main():
    bacnet_app = await BACnetApp.create()

    tasks = [bacnet_app.keep_baco_alive()]

    if USE_REST:
        tasks.append(bacnet_app.start_rest_api())

    bacnet_app.server_check_lock = asyncio.Lock()  # Create a lock for synchronization

    await asyncio.gather(*tasks)


asyncio.run(main())
