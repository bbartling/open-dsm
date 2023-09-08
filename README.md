# Open DSM

![Alt text](/time_series_testing/plots/algorithm_snip.png)


This repository is dedicated to providing an open-source Demand Side Management (DSM) solution finely tuned for the specific requirements of consulting engineers. It empowers them to implement ongoing electrical load management strategies tailored for typical commercial buildings. This DSM solution holds immense potential for consulting engineers looking to aid clients in curtailing energy usage and mitigating peak demand. Moreover, it serves as a valuable resource for building proprietors and operators aiming to enhance cost savings and the dependability of energy consumption. For consulting engineers eager to actively engage in fieldwork, this free and open-source tool offers an ideal opportunity. It places them at the forefront, taking on responsibilities that encompass:

* **Design the DSM solution** through standard consulting engineering methodologies, the Demand-Side Management (DSM) solution is designed, encompassing energy calculations, strategy formulation, and Sequence of Operations (SOO) development. This SOO guides the implementation of demand reduction strategies in collaboration with a controls contractor, who configures the building automation system (BAS) accordingly. Rigorous testing, commissioning, and performance monitoring ensure alignment with goals. Documentation and stakeholder education enhance project transparency and operational efficiency. This structured approach guarantees effective DSM solution deployment and optimization, akin to established building re-tuning practices.

* **Set up a small Linux device**, similar to the Raspberry Pi, can be strategically positioned within the Operations Technology (OT) LAN of the building. This device will effectively transmit signals to the Building Automation System (BAS) that operates within the building. Functioning as a recognizable BACnet device, the Linux unit will seamlessly engage with the controls contractor, seamlessly integrating into the BAS through established controls contracting practices. Alternatively, another viable and potentially cost-free solution involves collaborating with the organization's IT department. This approach entails setting up a Linux virtual machine (VM) on the OT LAN. The option of leveraging a VM provided by the IT department offers distinct advantages. Notably, it is a collaborative approach that involves the IT department in the project, enhancing project security from a cybersecurity standpoint. This collaborative effort ensures that the project aligns with robust cybersecurity measures.

* **Power meter integration** which is a prerequisite for the Linux device's algorithm to forecast demand is to have the necessary setup. An accessible alternative, particularly user-friendly for engineers and scientists, could involve using an [eGauge](https://www.egauge.net/commercial-energy-monitor/) device. This device offers a straightforward setup through a graphical user interface (GUI), and it could potentially prove simpler than attempting to integrate the building's power meter (assuming compatibility). The eGauge device provides options for effortless configuration using Modbus, BACnet, or REST API, alongside a GUI for data visualization that includes customizable energy accounting features. Moreover, it has the capacity to store up to a year's worth of data. Notably, the manufacturer offers a service that allows secure remote access to the eGauge device over the internet. This service enables data retrieval through a dashboard and even permits configuration adjustments if needed.

* **On-going monitoring** consistently engage with the building owner (typical consulting engineer practices) regarding any concerns related to DSM solution risks, including occupant comfort complaints, noise, and IAQ. This service could potentially be integrated into ongoing monitoring or building commissioning (MBx) initiatives. By incorporating other engineering consulting services, it becomes possible to ensure that as demand charges are optimized for the building, essential factors such as healthy IAQ, efficient operation of mechanical systems, and overall safety and effectiveness of the building are maintained.

The DSM solution can help to reduce energy consumption and peak demand, which can save money for building owners and operators. It can also help to improve the reliability of the electrical grid.

## Repository will offer 

1. Python based analyst scripts for pre-project engineering to create plots of electrical load profiles to study the buildings electrical use patterns. See sub directory `pre_project_analysis`.

2. A comprehensive financial spreadsheet to estimate project costs and ROI, see sub directory `financial`.

3. Ability to test algorithms offline on historical data, see `algorithm_testing` sub directory.

4. An API solution or app that would run on a small Linux device like a Raspberry Pi or Nano Pi that will ingest data from a power meter setup by the consulting engineer (or the buildings main meter if capable) and then communicate via a BACnet and/or REST server a signal which would represent a curtail level.

5. A future discord channel and YouTube channel for tutorials and community support!

**Repo is still in beta or active development!**

**More comming soon for the edge device app!**

## Author

[linkedin](https://www.linkedin.com/in/ben-bartling-510a0961/)

## Legal Stuff

**Disclaimer:** The operation and implementation of this application are the sole responsibility of the person who chooses to set it up. The author and affiliates of this app are not liable for any consequences or incidents that may arise from the use of this application. It is essential to acknowledge that any negative outcomes, including but not limited to equipment damage, indoor air quality issues, or personal injuries, are the responsibility of the person or firm who deploys and operates the application within a building. Users are advised to thoroughly evaluate and assess the application's suitability for their specific use case and take necessary precautions to ensure safe and effective utilization.

## Licence

【MIT License】

Copyright 2023 Ben Bartling

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


