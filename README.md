# load_shed_concept
* load shed BACnet concept idea for simple demand response event that could be around 1 - 3 hour duration around peak load times when electric grid is stressed.

## mapping.py
* HVAC setpoint adjust param float or int value
* HVAC system config file of BACnet addresses currently split between 4 thermal groups for north and south first and second floors.

## helpers.py
* functions with predefined for JCI and Trane VAV boxes in HVAC system zone temperature setpoint "points." BACnet write functions override HVAC setpoints on BACnet priority 10. Release functions release BACnet priority 10.

## load_shed_start.py
* this script runs on load shead demand response event start to take electrical cooling load off of chiller cooling system.

## load_shed_release.py
* this script runs on load shed demand response event experiration to release HVAC setopints back to the BAS.