#!/usr/bin/python3

import logging
import os
import queue
import sys
from logging.handlers import RotatingFileHandler

from bluepy.btle import Scanner, DefaultDelegate, Peripheral, Service, BTLEManagementError
import paho.mqtt.client as mqtt

from WalnutScan import WalnutScanDelegate
from WalnutConfig import configure_device


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("MQTT Connection successful")
        print("MQTT Connection successful")
        return
    elif rc == 1:
        logging.info("MQTT Incorrect protocol version")
        print("MQTT Incorrect protocol version")
    elif rc == 2:
        logging.info("MQTT Connection refused - invalid client identifier")
        print("MQTT Connection refused - invalid client identifier")
    elif rc == 3:
        logging.info("MQTT Connection refused - server unavailable")
        print("MQTT Connection refused - server unavailable")
    elif rc == 4:
        logging.info("MQTT Connection refused - bad username or password")
        print("MQTT Connection refused - bad username or password")
    elif rc == 5:
        logging.info("MQTT Connection refused - not authorised")
        print("MQTT Connection refused - not authorised")
    return

def on_mqtt_disconnect(client, userdata, rc):
    if rc == 0:
        logging.info("MQTT disconnected")
        print("MQTT disconnected")
    else:
        logging.info("MQTT disconnected unexpectedly, code:" + str(rc))
        print("MQTT disconnected unexpectedly, code:" + str(rc))

def on_mqtt_publish(client, userdata, mid):
    pass
    logging.debug("Published")

def setup_logging(file):
    log_handler = RotatingFileHandler(file, maxBytes=1048576, backupCount=5)
    log_formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
    log_handler.setFormatter(log_formatter)
    LOG = logging.getLogger()
    LOG.addHandler(log_handler)
    LOG.setLevel(logging.INFO)
    # LOG.setLevel(logging.DEBUG)
    return LOG

def has_devices_to_configure(queue):
    if queue.qsize() > 0:
        return True
    return False

def main():
    btleErrorCount = 0
    setup_logging("/home/pi/WalnutGateway/WalnutGateway.log")
    logging.info("Starting Walnut Gateway")

    configure_device_queue = queue.Queue()

    client = mqtt.Client(client_id="WalnutGateway")
    client.on_connect = on_connect
    client.on_disconnect = on_mqtt_disconnect
    client.on_publish = on_mqtt_publish
    logging.info("Connecting MQTT broker.")
    client.connect("127.0.0.1")
    client.loop_start()

    scanner = Scanner().withDelegate(WalnutScanDelegate(configure_device_queue, client))
    logging.info("Starting BLE scan")

    while True:
        logging.debug("----- BLE scan -----")
        try:
            scanner.scan(timeout=1.2, passive=False)
        except BTLEManagementError:
            logging.error("BTLEManagementError")
            btleErrorCount += 1
            if btleErrorCount > 10:
                os.system('sudo shutdown -r now')
        except:
            logging.error("Unknown Error")
        else:
            btleErrorCount = 0
        while has_devices_to_configure(configure_device_queue):
            logging.info("Nbr of devices to configure: %s", configure_device_queue.qsize())
            scanEntry = configure_device_queue.get_nowait()
            configure_device(scanEntry)


if __name__ == '__main__':
    main()
