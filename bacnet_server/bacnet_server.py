#!/usr/bin/python

from bacpypes.debugging import bacpypes_debugging, ModuleLogger
from bacpypes.consolelogging import ConfigArgumentParser

from bacpypes.core import run
from bacpypes.task import RecurringTask
from bacpypes.app import BIPSimpleApplication
from bacpypes.object import AnalogValueObject, BinaryValueObject, register_object_type
from bacpypes.local.object import AnalogValueCmdObject
from bacpypes.local.device import LocalDeviceObject
from bacpypes.service.cov import ChangeOfValueServices
from bacpypes.service.object import ReadWritePropertyMultipleServices

_debug = 0
_log = ModuleLogger(globals())

register_object_type(AnalogValueCmdObject, vendor_id=999)

# sample data in seconds of power meter
# written to writeable AV
INTERVAL = 60.0


@bacpypes_debugging
class SampleApplication(
    BIPSimpleApplication, ReadWritePropertyMultipleServices, ChangeOfValueServices
):
    pass


@bacpypes_debugging
class DoDataScience(RecurringTask):
    def __init__(self, 
                 interval, 
                input_power, 
                one_hr_future_pwr,
                power_rate_of_change
                 ):
        super().__init__(interval * 1000)
        self.interval = interval
        self.input_power = input_power
        self.one_hr_future_pwr = one_hr_future_pwr
        self.power_rate_of_change = power_rate_of_change

    def process_task(self):

        # TODO Machine Learning to forecast power
        
        print("input_power \n",self.input_power.presentValue)
        print("one_hr_future_pwr \n",self.one_hr_future_pwr.presentValue)
        print("power_rate_of_change \n",self.power_rate_of_change.presentValue)


class BacnetServer:
    def __init__(self, ini_file, address):
        self.this_device = LocalDeviceObject(ini=ini_file)
        self.app = SampleApplication(self.this_device, address)

        self.input_power = AnalogValueCmdObject(
            objectIdentifier=("analogValue", 1),
            objectName="input-power-meter",
            presentValue=-1.0,
            statusFlags=[0, 0, 0, 0],
            covIncrement=1.0,
            description="writeable input for app buildings electricity power value"
        )
        self.app.add_object(self.input_power)
        
        self.one_hr_future_pwr = AnalogValueObject(
            objectIdentifier=("analogValue", 2),
            objectName="one-hour-future-power",
            presentValue=-1.0,
            statusFlags=[0, 0, 0, 0],
            covIncrement=1.0,
            description="electrical power one hour into future"
        )
        self.app.add_object(self.one_hr_future_pwr)

        self.power_rate_of_change = AnalogValueObject(
            objectIdentifier=("analogValue", 3),
            objectName="power-rate-of-change",
            presentValue=-1.0,
            statusFlags=[0, 0, 0, 0],
            covIncrement=1.0,
            description="current electrical power rate of change"
        )
        self.app.add_object(self.power_rate_of_change)

        self.task = DoDataScience(INTERVAL, 
                                self.input_power, 
                                self.one_hr_future_pwr,
                                self.power_rate_of_change
                                )
        self.task.install_task()
        
    def run(self):
        run()


def main():
    parser = ConfigArgumentParser(description=__doc__)
    args = parser.parse_args()

    server = BacnetServer(args.ini, args.ini.address)
    server.run()


if __name__ == "__main__":
    main()
