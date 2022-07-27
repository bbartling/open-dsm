
from datetime import datetime
import os


# local time zone
# year, month, day, hour, minute
target_start = datetime(2022, 7, 18, 14, 0)
dt_string = target_start.strftime("%m/%d/%Y %H:%M:%S")

def timer(countdown_to):
    last_minute = datetime.now().minute
    while datetime.now() <= countdown_to:
        if datetime.now().minute != last_minute:
            print('Time left:', int((countdown_to - datetime.now()).total_seconds()), 'seconds')
            print('Time left:', int((countdown_to - datetime.now()).total_seconds() // 60), 'minutes')
            print('Time left:', int((countdown_to - datetime.now()).total_seconds() // 60 // 60), 'hours')
            print('Time now:', datetime.now())
            last_minute = datetime.now().minute


try:
    print(f"TIMER GO... to run at {dt_string}")
    timer(target_start)

    dir_path = os.path.dirname(os.path.realpath(__file__))
    main_script = os.path.join(dir_path,'main.py')

    print("READY to run main script now!!")
    os.system(f'python {main_script}')

    print("ALL DONE !!!!")


except Exception as error:
    print("ERROR!!!! ",error)
