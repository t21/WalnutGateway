#!/bin/bash

# Create Mosquitto folders
sudo mkdir -p ./volumes/mosquitto/data/
sudo mkdir -p ./volumes/mosquitto/log/
sudo mkdir -p ./volumes/mosquitto/pwfile/
sudo chown -R 1883:1883 ./volumes/mosquitto/
mkdir -p ./services/mosquitto
cp ./install/mosquitto/mosquitto.conf ./services/mosquitto/mosquitto.conf

# Create node-red folder
mkdir -p ./volumes/node-red-homekit/data
