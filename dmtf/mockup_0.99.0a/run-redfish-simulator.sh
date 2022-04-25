#!/bin/bash

docker ps -a | grep -q "redfish-simulator_0.99.0a"
if [ "$?" -eq 0 ]; then
	docker rm -f "redfish-simulator_0.99.0a"
fi
# The -p option needs to be after the run command. No warning is given if before but doesn't work
docker run -d -p 8000:80 --name "redfish-simulator_0.99.0a" redfish-simulator_0.99.0a:latest
echo "Launch your browser and load http://localhost:8000/redfish/v1"
