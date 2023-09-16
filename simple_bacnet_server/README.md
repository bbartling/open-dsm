# BACnet Server with Flask Integration

This project creates a BACnet server that collects and provides data related to electricity power values. It also includes a Flask-based web dashboard to display this data and an API endpoint to fetch the BACnet server's data.

## Requirements

- Python 3.x
- Flask
- BACpypes library

## Installation

1. pip install

```bash
pip install flask bacpypes
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
**Web Dashboard**
* Access the web dashboard by navigating to `http://<server_ip>:5000/` in your web browser.

**API Endpoint**
* Fetch data from the BACnet server using the API endpoint:

**Endpoint**: http://<server_ip>:5000/api/data
* Method: GET

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

   