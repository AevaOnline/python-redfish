#!/bin/bash

docker ps -a | grep -q "redfish-simulator_1.1.0"
if [ "$?" -eq 0 ]; then
	docker rm -f "redfish-simulator_1.1.0"
fi
# The -p option needs to be after the run command. No warning is given if before but doesn't work
docker run -d -p 8001:8001 -p 8002:8002 -p 8003:8003 -p 8004:8004 -p 8005:8005 -p 8006:8006 --name "redfish-simulator_1.1.0" redfish-simulator_1.1.0:latest
echo "Launch your browser and load http://localhost:8001/ to access public-bladed profile"
echo "Launch your browser and load http://localhost:8002/ to access public-catfish profile"
echo "Launch your browser and load http://localhost:8003/ to access public-localstorage profile"
echo "Launch your browser and load http://localhost:8004/ to access public-rackmount1 profile"
echo "Launch your browser and load http://localhost:8005/ to access public-sasfabric profile"
echo "Launch your browser and load http://localhost:8006/ to access documentation and all files"
