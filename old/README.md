# load_shed_concept
* load shed BACnet concept idea for simple demand response event that could be around 1 - 3 hour duration around peak load times when electric grid is stressed.

## mapping.py
* demand response event duration in minutes:
`event_duration = 2`

* demand response event HVAC zone adjust zone setpoints in degrees F:
`setpoint_adj = 3.0`

* demand response event applying overrides on BACnet priority:
`write_priority = 9`

* when the demand response event it True and zones have been set back via GTA. Perform BACnet reads of zone sensors every minute. Every 3 minutes evaulate if any of the zones rises above `zone_hi_temp_release_setpoint` release this zone back to the BAS:
`zone_hi_temp_release_setpoint = 75.0`

* HVAC system config file of BACnet device and point addresses currently split between 4 thermal groups for north and south first and second floors

## main.py
run by `$python main.py`