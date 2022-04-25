DMTF Redfish specification
--------------------------

This directory contains the current references from the DMTF on the Redfish
specification (1.0.1 at the time of the writing)

The overall protocol documentation can be found online at:
 http://www.dmtf.org/standards/redfish

The specification can be found locally in DSP0266_1.0.1.pdf or online at:
 http://www.dmtf.org/sites/default/files/standards/documents/DSP0266_1.0.1.pdf

The data model documentation can be found locally in DSP8010_1.0.0.zip or online at:
 http://redfish.dmtf.org/schemas/


In order to ease test, the DMTF has published a mockup environment to simulate
a Redfish based system so it is possible to write programs without real Redfish
compliant hardware platform.

Note: Mockup release is still 0.99.0a and so not aligned with specification release
number.

Docker container
----------------

In order to help testing python-redfish, this directory provides a script which
you should be able to run on your system (providing you have docker support and 
a docker registry) which will create a docker container running the DMTF Redfish 
mockup on the port 8000.

To build your container, just issue:  ./buildImage.sh
To launch it, just issue: ./run-redfish-simulator.sh
To use it, just issue: firefox http://localhost:8000/redfish/v1

Systems entry point:
http://localhost:8000/redfish/v1/Systems

Chassis entry point:
http://localhost:8000/redfish/v1/Chassis

Managers entry point:
http://localhost:8000/redfish/v1/Managers
