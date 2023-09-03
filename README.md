# Demand Side Management On A Budget!

![Alt text](/algorithm_testing/plots/algorithm_snip.png)


This repository aims to offer an open-source Demand Side Management (DSM) solution tailored to the unique needs of consulting engineers to implement continuous electrical load management strategies at typical commercial type buildings. The DSM solution could be a valuable tool for consulting engineers who want to help their clients reduce energy consumption and peak demand. It is also a valuable tool for building owners and operators who want to save money and improve the reliability of their energy use. This would be a good free open sourced tool for the consulting engineer that wants to get their hands dirty in the field where would be responsible for:

* Design the DSM solution through typical consulting engineering practices to meet the specific needs of the building.

* Setting up a user-friendly Linux device like the Raspberry Pi on the buildings operations technology (OT) LAN which can communicate a signal to the building automation system (BAS) running inside the building.

* Hire and communicate to the controls contractor the DSM solution and commission systems inside the building as needed.

* Consult to the customer and organizations facilities management any concerns the DSM solution risks such as occupant comfort complaints, noise, IAQ, etc.

* Consult with the owner for effective and efficient building mechanical and electrical systems operations and energy management.

The DSM solution can help to reduce energy consumption and peak demand, which can save money for building owners and operators. It can also help to improve the reliability of the electrical grid.

* It is based on open source software, which makes it affordable and easy to customize.

* It is designed to be scalable, so it can be used in buildings of all sizes.

* It is easy to use, so consulting engineers can quickly and easily configure it to meet the specific needs of the building.

## Repository will offer 

1. Python based analyst scripts for pre-project engineering to create plots of electrical load profiles to study the buildings electrical use patterns. See sub directory `pre_project_analysis`.

2. A comprehensive financial spreadsheet to estimate project costs and ROI, see sub directory `financial`.

3. Ability to test algorithms offline on historical data, see `algorithm_testing` sub directory.

4. An API solution or app that would run on a small Linux device like a Raspberry Pi or Nano Pi that will ingest data from a power meter setup by the consulting engineer (or the buildings main meter if capable) and then communicate via a BACnet and/or REST server a signal which would represent a curtail level.

5. A future discord channel and YouTube channel for tutorials and community support!

**Repo is still in beta or active development!**

**More comming soon for the edge device app!**

