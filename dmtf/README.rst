DMTF Redfish specification
--------------------------

This directory contains the current references from the DMTF on the Redfish 
specification (1.0.0 at the time of the writing)

In order to ease test, the DMTF has published a mockup environment to simulate 
a Redfish based system so it is possible to write programs without real Redfish 
compliant hardware platform.

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
