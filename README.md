# Open DSM

![Alt text](/time_series_testing/plots/algorithm_snip.png)

This repository is dedicated to providing an open-source Demand Side Management (DSM) solution tailored for the building automation industry's demand-side management applications. It is designed to enhance the limitations of existing building automation systems commonly found in BACnet-based commercial buildings.

## Key Features

The DSM solution in this repository offers the following key features:

* **Design and Implementation:** Implement ongoing electrical load management strategies customized for typical commercial buildings. The solution helps building proprietors and operators curtail energy usage and mitigate peak demand.

* **Linux Device Integration:** Strategically position a small Linux device within the building's Operations Technology (OT) LAN to seamlessly transmit signals to the Building Automation System (BAS). This device functions as a recognizable BACnet device and engages with controls contractors for efficient BAS integration.

* **Power Meter Integration:** Integrate power meter data, a prerequisite for the algorithm's demand forecasting capabilities. Options like the [eGauge](https://www.egauge.net/commercial-energy-monitor/) device simplify configuration and data visualization, offering compatibility with Modbus, BACnet, or REST API. A requirement of this app is that the buildings power meter reading (kW) needs to be written to a writeable BACnet point.

* **Ongoing Monitoring:** Consistently engage with building owners to address concerns related to DSM solution risks, ensuring optimal demand charge management while maintaining indoor air quality, mechanical system efficiency, and overall building safety.

## Benefits

The DSM solution can significantly reduce energy consumption, save costs for building owners and operators, and enhance the reliability of the electrical grid.

## Future Possibilities

While this solution addresses current building automation limitations, the field continues to evolve. Future research may explore integrating similar algorithms directly into Building Automation Systems (BAS) or Internet of Things (IoT) frameworks to further optimize building operations.

Consider a scenario where algorithms seamlessly facilitate tasks like electric car charging, battery system management, and HVAC power consumption control within building automation systems. Such advancements may become commonplace in buildings of the future.

Thank you for exploring our DSM solution!


## Repository will offer 

1. Python based analyst scripts for pre-project engineering to create plots of electrical load profiles to study the buildings electrical use patterns. See sub directory `pre_project_analysis`.

2. A comprehensive financial spreadsheet to estimate project costs and ROI, see sub directory `financial`.

3. Ability to test algorithms offline on historical data, see `algorithm_testing` sub directory.

4. An API solution or app that would run on a small Linux device like a Raspberry Pi or Nano Pi that will ingest data from a power meter setup by the consulting engineer (or the buildings main meter if capable) and then communicate via a BACnet and/or REST server a signal which would represent a curtail level.

5. An open source Linux project inspired by Home Assistant

**Repo is still in beta or active development!**

**More comming soon for the edge device app!**

## Author

[linkedin](https://www.linkedin.com/in/ben-bartling-510a0961/)

## Legal Stuff

**Disclaimer:** The operation and implementation of this application are the sole responsibility of the person who chooses to set it up. The author and affiliates of this app are not liable for any consequences or incidents that may arise from the use of this application.

**Cybersecurity Notice:** This application is designed exclusively for use in operational technology (OT) environments that do not reside on the internet or have internet connectivity. It does not incorporate cybersecurity measures for internet-facing or IoT (Internet of Things) applications. 

Users are advised that the security of the application is limited to its use within isolated OT networks. The creator of this app and its affiliates are not responsible for cybersecurity incidents that result from poor IT practices, misconfiguration, or the use of this application in conjunction with internet-connected devices or applications.

It is essential to acknowledge that any negative outcomes, including but not limited to equipment damage, indoor air quality issues, or personal injuries, are the responsibility of the person or firm who deploys and operates the application within a building. Users are strongly encouraged to thoroughly evaluate and assess the application's suitability for their specific use case, implement appropriate cybersecurity measures where necessary, and take all required precautions to ensure safe and effective utilization.


## Licence

【MIT License】

Copyright 2023 Ben Bartling

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


