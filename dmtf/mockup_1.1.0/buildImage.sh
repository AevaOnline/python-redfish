#!/bin/bash

# Build and tag images
docker rmi redfish-simulator_1.1.0
docker build -t "redfish-simulator_1.1.0" .
