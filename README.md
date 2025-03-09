# Walnut Gateway

## Setup

### Raspberry Pi

#### Raspberry Pi OS
Use Raspberry Pi Imager (https://www.raspberrypi.org/software/) to write an image of the Raspberry Py OS on your SD-card.

#### Enable ssh before inserting uSD-card in Raspberry Pi
Insert uSD-card in computer and add an empty file called ssh to the boot volume of the uSD-card.
touch ssh

#### Insert uSD-card in Raspberry Pi

ping raspberrypi.local

ssh pi@raspberrypi.local
password=raspberry

sudo apt-get update
sudo apt-get upgrade

##### raspi-config
Change Password
Change Hostname
Optional - Set Boot / Auto Login
Optional - Change default Display Resolution
Optional - Enable VNC
Optional - Configure Locale -> svUTF8 + lang en.GB
Set Timezone
Configure keyboard
Set WLAN country
Expand filesystem

sudo reboot

##### Install needed SW
sudo apt-get install build-essential - probably already installed

#### Connecting to Github with ssh
Follow the instructions here
https://docs.github.com/en/github/authenticating-to-github/connecting-to-github-with-ssh
to setup the ssh keys

Create key
ssh-keygen -t ed25519 -C "your_email@example.com"

Start ssh agent in background
eval "$(ssh-agent -s)"

Add key to agent
ssh-add ~/.ssh/id_ed25519

cat .ssh/id_ed25519.pub

Add key to Github

Configure git
git config --global user.name "Thomas Berg"
git config --global user.email "thomas.berg2@gmail.com"

#####
Clone WalnuGateway repo


-------

### Python reqs

bluepy3

https://pypi.org/project/bluepy3/


paho-mqtt

tested version 2.1.0



-------



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
http://www.steves-internet-guide.com/mosquitto-tls/
https://dzone.com/articles/mqtt-security-securing-a-mosquitto-server

openssl genrsa -out mosq-ca.key 2048
openssl req -new -x509 -days 1826 -key mosq-ca.key -out mosq-ca.crt

pi@raspberrypi:~/ssl-cert-mosq $ openssl req -new -x509 -days 1826 -key mosq-ca.key -out mosq-ca.crt
You are about to be asked to enter information that will be incorporated
into your certificate request.
What you are about to enter is what is called a Distinguished Name or a DN.
There are quite a few fields but you can leave some blank
For some fields there will be a default value,
If you enter '.', the field will be left blank.
-----
Country Name (2 letter code) [AU]:SE
State or Province Name (full name) [Some-State]:Skane
Locality Name (eg, city) []:Lund
Organization Name (eg, company) [Internet Widgits Pty Ltd]:OrgName
Organizational Unit Name (eg, section) []:Test
Common Name (e.g. server FQDN or YOUR name) []:127.0.0.1
Email Address []:test@blaha.com
---

openssl genrsa -out mosq-serv.key 2048

openssl req -new -key mosq-serv.key -out mosq-serv.csr

---
pi@raspberrypi:~/ssl-cert-mosq $ openssl req -new -key mosq-serv.key -out mosq-serv.csr
You are about to be asked to enter information that will be incorporated
into your certificate request.
What you are about to enter is what is called a Distinguished Name or a DN.
There are quite a few fields but you can leave some blank
For some fields there will be a default value,
If you enter '.', the field will be left blank.
-----
Country Name (2 letter code) [AU]:SE
State or Province Name (full name) [Some-State]:Skane
Locality Name (eg, city) []:Lund
Organization Name (eg, company) [Internet Widgits Pty Ltd]:OrgName
Organizational Unit Name (eg, section) []:Test
Common Name (e.g. server FQDN or YOUR name) []:127.0.0.1
Email Address []:test@blaha.com

Please enter the following 'extra' attributes
to be sent with your certificate request
A challenge password []:
An optional company name []:
---

openssl x509 -req -in mosq-serv.csr -CA mosq-ca.crt -CAkey mosq-ca.key -CAcreateserial -out mosq-serv.crt -days 365 -sha256


Locate the mosquitto.conf file that holds all the configuration parameters and add the following lines:

listener 8883
cafile /home/pi/ssl-cert-mosq/mosq-ca.crt
certfile /home/pi/ssl-cert-mosq/mosq-serv.crt
keyfile /home/pi/ssl-cert-mosq/mosq-serv.key



### Walnut -> MQTT Python script

### Node Red, MQTT -> HomeKit

https://nodered.org/docs/getting-started/raspberrypi

Install build essentials, probably already installed
sudo apt install build-essential git

Run script
bash <(curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered)

Enable autostart on boot
sudo systemctl enable nodered.service

Read log
node-red-log

#### General programming tips

http://noderedguide.com

#### MQTT broker

When adding the first MQTT input node will you be asked to set up the broker settings.


#### Homekit

https://github.com/NRCHKB/node-red-contrib-homekit-bridged/wiki/Characteristics


#### Node Red, SMHI

https://github.com/Naesstrom/SMHI-NodeRed-HomeAssistant


#### Dashboard

https://randomnerdtutorials.com/getting-started-with-node-red-dashboard/


## Links

### MQTT
https://mosquitto.org
https://mosquitto.org/download/

Beginners Guide To The Paho MQTT Python Client
http://www.steves-internet-guide.com/into-mqtt-python-client/
http://www.steves-internet-guide.com/install-mosquitto-linux/

https://www.switchdoc.com/2018/02/tutorial-installing-and-testing-mosquitto-mqtt-on-raspberry-pi/



