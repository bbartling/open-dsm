# BACnet Server with Tensorflow integration

This project introduces an innovative synergy between BACnet server capabilities and the formidable machine learning prowess of Keras, a powerful library seamlessly integrated into TensorFlow. Notably, an LSTM (Long Short-Term Memory) model is trained during overnight hours when electricity power levels are typically low. 
This model becomes a critical asset for predicting electricity consumption values for the upcoming hour.

During daytime hours, when control systems may be actively implementing demand-side management strategies to mitigate electrical power spikes, the trained LSTM model is leveraged every minute within the BACnet application. 
It generates a one-hour ahead forecast of electrical power values, which control systems can access via BACnet. This real-time forecasting capability empowers the system to optimize energy consumption, enhance the efficiency of building operations, and proactively address potential power fluctuations.

## Features
* **Time Series Forecasting** : Uses simple LSTM machine learning techniques to forecast the power meter readings 1 hour into the future. This aids in understanding potential power spikes or lapses.
* **Dynamic Model Training** : Trains a new model every midnight. This ensures that the model is always up-to-date, accommodating daily variations and subtle changes in the building's electricity usage patterns.
* **High & Low Load Indicators** : The BACnet Binary Values (BVs) are set to indicate high and low electrical usage based on the 90th and 30th percentiles respectively. This statistical approach ensures accurate indications of peak and low power consumption times.
* **Operational Technology (OT) Control System Integration** : Especially designed for buildings equipped with an OT control system. By using the forecasted values, the system can act preemptively to limit excess power usage and reduce demand spikes.

## Usage
**BACnet Server Analog Value Points**
1. `input-power-meter` (writeable)
2. `one-hour-future-power` (readonly)
3. `power-rate-of-change` (readonly)

## Requirements
- Python 3.10.x or newer
- BACpypes and scikit-learn libraries

## Installation
1. **pip install Python libraries**

```bash
pip install scikit-learn bacpypes tensorflow
```

2. **Clone repo, cd into into project directory**
```bash
git clone https://github.com/bbartling/open-dsm.git
```
```bash
cd open-dsm/simple_bacnet_server
```

3. (Optional) **run or test script from Linux terminal**
```bash
python bacnet_server.py
```


### Run `bacnet_server.py` as a linux service

1. **Create a Service Unit File**

   Open a terminal and navigate to the systemd service unit directory:

   ```bash
   cd /etc/systemd/system

   sudo nano bacnet_server.service
   ```

2. **Add the Service Configuration and `EDIT` file as necessary**

   ```bash
   [Unit]
   Description=BACnet Server
   After=network.target

   [Service]
   User=your_username
   WorkingDirectory=/home/your_username/open-dsm/simple_bacnet_server
   ExecStart=/usr/bin/python3 bacnet_server.py --debug
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```
   Replace `your_username` with your actual username.

2. **Save and Exit the Text Editor**
   After adding the configuration, save the file and exit the text editor.

3. **Enable and Start the Service**
   Enable the service to start on boot:
   ```bash
   sudo systemctl enable bacnet_server.service
   ```
   Then, start the service:
   ```bash
   sudo systemctl start bacnet_server.service
   ```
4. **Check the Service Status**
   Check the status of your service to ensure it's running without errors:
   ```bash
   sudo systemctl status bacnet_server.service
   ```
5. **If errors and need to update script**
   If you make changes to the script, stop the service to update it:
   ```bash
   sudo systemctl stop bacnet_server.service
   ```
6. **Start the Service After Updating**
   After making changes to the script, start the service again:
   ```bash
   sudo systemctl start bacnet_server.service
   ```
7. **Check the Updated Status**
   Check the status again to confirm that the updated script is running:
   ```bash
   sudo systemctl status bacnet_server.service
   ```

8. **Tail Linux Service Logs**
   See debug print statements:
   ```bash
   sudo journalctl -u bacnet_server.service -f
   ```

   * Below is an example that updates at 1-minute intervals. The presence of the value `30286.0` confirms that the control system is successfully writing to the `input-power-meter` point in the BACnet API. If the control system were not writing properly, the default BACnet present value would be `-1.0`.:

   ```bash
   Sep 30 09:28:00 vm-bbartling2 python3[296422]: DEBUG:__main__:input_power: 30286.0
   Sep 30 09:28:00 vm-bbartling2 python3[296422]: DEBUG:__main__:one_hr_future_pwr: -1.0
   Sep 30 09:28:00 vm-bbartling2 python3[296422]: DEBUG:__main__:power_rate_of_change: -1.0
   Sep 30 09:28:00 vm-bbartling2 python3[296422]: DEBUG:__main__:high_load_bv: inactive
   Sep 30 09:28:00 vm-bbartling2 python3[296422]: DEBUG:__main__:low_load_bv: inactive
   Sep 30 09:28:00 vm-bbartling2 python3[296422]: DEBUG:__main__:Data Cache Length: 3
   Sep 30 09:28:00 vm-bbartling2 python3[296422]: DEBUG:__main__:Current Hour: 9
   Sep 30 09:28:00 vm-bbartling2 python3[296422]: DEBUG:__main__:Current Minute: 28
   Sep 30 09:28:00 vm-bbartling2 python3[296422]: DEBUG:__main__:Training Started Today: False
   Sep 30 09:28:00 vm-bbartling2 python3[296422]: DEBUG:__main__:Model Availability: False
   Sep 30 09:28:00 vm-bbartling2 python3[296422]: DEBUG:__main__:Model training time: 0.00 minutes on None
   Sep 30 09:28:00 vm-bbartling2 python3[296422]: DEBUG:__main__:Data Cache last value: 30286.0
   Sep 30 09:28:00 vm-bbartling2 python3[296422]: DEBUG:__main__:data_cache_len < 65 - RETURN
   ```

### **Reload Linux service if modifiations are required to the .py file and or Linux service**
   Reload the systemd configuration. This tells systemd to recognize your changes:
   ```bash
   sudo systemctl daemon-reload
   ```

   Restart your service to apply the changes:
   ```bash
   sudo systemctl restart bacnet_server.service
   ```

   Check the status to ensure it's running as expected:
   ```bash
   sudo systemctl status bacnet_server.service
   ```

   See debug print statements:
   ```bash
   sudo journalctl -u bacnet_server.service -f
   ```