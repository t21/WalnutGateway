# Walnut Gateway

## Setup

### Raspberry Pi
*** TODO ***

### MQTT broker
Update the package database
sudo apt-get update

Download and install Mosquitto MQTT broker
sudo apt-get install mosquitto
sudo apt-get install mosquitto mosquitto-clients
-> version 1.5.7 = not the latest # TODO: Investigate other installation methods ...

Mosquitto is installed as a service and should start automatically after install

To Stop and start the service I needed to use

sudo service mosquitto stop
sudo service mosquitto start

When debugging start MQTT broker with
mosquitto -v

Configuration

Start with special configuration file
mosquitto -c filename

You can find the mosquitto.conf template file in the /etc/mosquitto/ folder.

Setting up security
https://dzone.com/articles/mqtt-security-securing-a-mosquitto-server



### Walnut -> MQTT Python script

### Node Red, MQTT -> HomeKit

### Node Red, SMHI

## Links

### MQTT
https://mosquitto.org
https://mosquitto.org/download/

Beginners Guide To The Paho MQTT Python Client
http://www.steves-internet-guide.com/into-mqtt-python-client/
http://www.steves-internet-guide.com/install-mosquitto-linux/

https://www.switchdoc.com/2018/02/tutorial-installing-and-testing-mosquitto-mqtt-on-raspberry-pi/



