## Key Features

This DSM (Demand Side Management) solution includes a BACnet server running on a Linux distribution of choice, providing several essential features for building automation and energy management:

* **Electrical Power Forecasting:** The BACnet server can forecast a building's electrical power one hour into the future, enabling proactive load management strategies. Building proprietors and operators can efficiently plan and optimize energy usage, reducing costs and mitigating peak demand.

* **Linux Device Integration:** Seamlessly integrate a small Linux device into the building's Operations Technology (OT) LAN. This Linux device acts as a recognized BACnet device and facilitates communication with the Building Automation System (BAS) using common BACnet setup practices. This integration enhances the BAS with advanced capabilities.

* **Power Meter Integration:** To enable demand forecasting, the solution requires the integration of power meter data. This integration ensures accurate predictions and effective load management. Compatible with various power meters, including the user-friendly [eGauge](https://www.egauge.net/commercial-energy-monitor/) device, the solution simplifies configuration and data visualization. It supports protocols like Modbus, BACnet, or REST API. A prerequisite for using this app is that the building's power meter readings (kW) can be written to a writable BACnet point.

* **Ongoing Monitoring:** Maintain continuous engagement with building owners to address concerns related to DSM solution risks. This includes optimizing demand charge management, preserving indoor air quality, enhancing mechanical system efficiency, and ensuring overall building safety. Regular monitoring ensures efficient operation and alignment with energy management goals.

These features empower building owners and operators to proactively manage energy consumption, reduce costs, and maintain a safe and efficient building environment.

## Benefits

The DSM solution can significantly reduce power consumption, save costs for building owners and operators in demand charges, and enhance the reliability of the electrical grid.

## Future Possibilities

While this solution addresses current building automation limitations, the field continues to evolve. Future research may explore evolving  the project into something like Home Assistant which is a neat open sourced Linux project.

Consider a scenario where algorithms seamlessly facilitate tasks like electric car charging, battery system management, and HVAC power consumption control within building automation systems. Such advancements may become commonplace in buildings of the future.

Thank you for exploring our DSM solution!

## Repository will offer 

1. Python-based analyst scripts for pre-project engineering to create plots of electrical load profiles to study the building's electrical use patterns. See the subdirectory `pre_project_analysis`.

2. A comprehensive financial spreadsheet to estimate project costs and ROI, see the subdirectory `financial`.

3. Ability to test algorithms offline on historical data, see the `algorithm_testing` subdirectory.

4. An API solution or app that would run on a small Linux device like a Raspberry Pi or Nano Pi that will ingest data from a power meter setup by the consulting engineer (or the building's main meter if capable) and then communicate via a BACnet and/or REST server a signal that would represent a curtail level.

5. An open-source Linux project inspired by Home Assistant.

**Repo is still in beta or active development!**

**More coming soon for the edge device app!**

## Author

[LinkedIn](https://www.linkedin.com/in/ben-bartling-510a0961/)

## Legal Stuff

**Disclaimer:** The operation and implementation of this application are the sole responsibility of the person who chooses to set it up. The author and affiliates of this app are not liable for any consequences or incidents that may arise from the use of this application.

**Cybersecurity Notice:** This application is designed exclusively for use in operational technology (OT) environments that do not reside on the internet or have internet connectivity. It does not incorporate cybersecurity measures for internet-facing or IoT (Internet of Things) applications. 

Users are advised that the security of the application is limited to its use within isolated OT networks. The creator of this app and its affiliates are not responsible for cybersecurity incidents that result from poor IT practices, misconfiguration, or the use of this application in conjunction with internet-connected devices or applications.

It is essential to acknowledge that any negative outcomes, including but not limited to equipment damage, indoor air quality issues, or personal injuries, are the responsibility of the person or firm who deploys and operates the application within a building. Users are strongly encouraged to thoroughly evaluate and assess the application's suitability for their specific use case, implement appropriate cybersecurity measures where necessary, and take all required precautions to ensure safe and effective utilization.

## License

【MIT License】

Copyright 2023 Ben Bartling

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
