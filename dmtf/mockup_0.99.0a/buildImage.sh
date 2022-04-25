#!/bin/bash

# Build and tag images
docker rmi redfish-simulator_0.99.0a
docker build -t "redfish-simulator_0.99.0a" .
