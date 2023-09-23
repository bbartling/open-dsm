# BACnet Server with Sci-kit Learn Integration

This project offers an innovative approach by merging BACnet server capabilities with the power of scikit-learn, a popular machine learning library. By leveraging time series machine learning techniques, the server can predict electricity power values for the upcoming hour. This is invaluable for optimizing energy consumption, ensuring efficient building operations, and responding proactively to potential power spikes.

## Features
* **Time Series Forecasting** : Uses advanced machine learning techniques to forecast the power meter readings 1 hour into the future. This aids in understanding potential power spikes or lapses.
* **Dynamic Model Training** : Trains a new model every midnight. This ensures that the model is always up-to-date, accommodating daily variations and subtle changes in the building's electricity usage patterns.
* **High & Low Load Indicators** : The BACnet Binary Values (BVs) are set to indicate high and low electrical usage based on the 90th and 30th percentiles respectively. This statistical approach ensures accurate indications of peak and low power consumption times.
* **Operational Technology (OT) Control System Integration** : Especially designed for buildings equipped with an OT control system. By using the forecasted values, the system can act preemptively to limit excess power usage and reduce demand spikes.

## Requirements

- Python 3.x
- BACpypes library

## Installation

1. pip install

```bash
pip install bacpypes pandas numpy scikit-learn
```

2. Clone repo, cd into into `open-dsm/simple_bacnet_server` and edit the `BACpypes.ini` file for the IP address of the NIC card for the computer being used. 
Example .ini file that is included with the repo, edit the `address` field as necessary. Edit the `objectIdentifier` as necessary if the BACnet instance ID needs
to be modified to accomodate the buildings BACnet system. The computer running this app will show up on a BACnet discovery to another platform as `PowerForecaster`.

```bash
[BACpypes]
objectName: PowerForecaster
address: 192.168.0.109/24 
objectIdentifier: 500001
maxApduLengthAccepted: 1024
segmentationSupported: segmentedBoth
vendorIdentifier: 15
```

3. run or test script:

```bash
$ python bacnet_server.py
```

## Usage
**BACnet Server Analog Value Points**
1. `input-power-meter` (writeable)
2. `one-hour-future-power` (readonly)
3. `power-rate-of-change` (readonly)


### (Optional) Run `bacnet_server.py` as a linux service.

1. **Create a Service Unit File**

   Open a terminal on your Raspberry Pi and navigate to the systemd service unit directory:

   ```bash
   cd /etc/systemd/system

   sudo nano bacnet_server.service
   ```

2. **Add the Service Configuration**

   ```bash
   [Unit]
   Description=BACnet Server
   After=network.target

   [Service]
   User=your_username
   WorkingDirectory=/home/your_username/open-dsm/simple_bacnet_server
   ExecStart=/usr/bin/python3 bacnet_server.py
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

## Docker
**Start docker container**
   ```bash
	$ sudo docker build -t bacnet-server .
	$ sudo docker run --network="host" bacnet-server
   ```

**Stop docker container**
   ```bash
	$ sudo docker ps
	$ sudo docker stop <CONTAINER_ID>
	```