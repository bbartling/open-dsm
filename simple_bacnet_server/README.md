# BACnet server with Sci-kit Learn Integration

use legacy bacpypes version until bacpypes 3 version is stable

## Schematic

Update to include a network schematic:
The Building Automation System (BAS) retrieves the current electrical power reading from the building's power meter, using protocols such as Modbus, BACnet, REST, among others. This value, representing the instantaneous electrical power usage (measured in kW, not kWh), is then written to the Data Science BACnet App. Subsequently, the BAS accesses forecasted electrical power data, rate-of-change metrics, and high/low load indicators from BACnet Analog Value and Binary Value objects, respectively. Equipped with this data, the BAS can execute logic to either shed loads or maintain a specific power threshold. This sequence, typically crafted by a consulting engineer, is then brought to fruition by an HVAC controls contractor technician.

```mermaid
sequenceDiagram
    participant BAS
    participant DataScienceBacnetApp
    participant PowerMeter
    
    BAS->>PowerMeter: Read Electrical Power

    PowerMeter-->>BAS: Return Electrical Power Value
    Note right of PowerMeter: Fetch current power value<br>On some protocol
    Note right of DataScienceBacnetApp: Writeable BACnet<br>AnalogValue Object<br>Input Power Meter Reading to App
    BAS->>DataScienceBacnetApp: BACnet Write Electrical Power AnalogValue

    Note right of DataScienceBacnetApp: Value Cached<br>Run Data Science<br>processes...Update<br>BACnet API every 60 seconds

    BAS->>DataScienceBacnetApp: BACnet Read Future Electrical Power AnalogValue
    Note right of DataScienceBacnetApp: Read Only BACnet<br>AnalogValues Objects<br>To represent future power & ROC
    DataScienceBacnetApp-->>BAS: Return Future Electrical Power

    BAS->>DataScienceBacnetApp: BACnet Read Electrical Rate-Of-Change AnalogValue
    DataScienceBacnetApp-->>BAS: Return Electrical Rate-Of-Change


    BAS->>DataScienceBacnetApp: BACnet Read High-Load BinaryValue
    Note right of DataScienceBacnetApp: Read Only BACnet<br>BinaryValue Objects<br>To represent Peak or Valley

    DataScienceBacnetApp-->>BAS: Return High-Load

    BAS->>DataScienceBacnetApp: BACnet Read Low-Load BinaryValue
    DataScienceBacnetApp-->>BAS: Return High-Load
```

## Writeup:

* [linkedin story](https://www.linkedin.com/pulse/bacnet-data-science-app-grafana-ben-bartling%3FtrackingId=LLsyrLv8yC6I4n7lqYF42w%253D%253D/?trackingId=LLsyrLv8yC6I4n7lqYF42w%3D%3D)