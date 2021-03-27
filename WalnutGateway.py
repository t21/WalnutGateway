#!/usr/bin/env python3

import logging
import queue
import sys
from logging.handlers import RotatingFileHandler

from bluepy.btle import Scanner, DefaultDelegate, Peripheral, Service
import paho.mqtt.client as mqtt

from WalnutScan import WalnutScanDelegate, Walnut
from WalnutConfig import configure_device


def on_connect(client, userdata, flags, rc):
    logging.info("Connected to MQTT broker")

def setup_logging(file):
    # logFormat = '%(asctime)s:%(levelname)s:%(message)s'
    # logFormat = '%(levelname)s:%(message)s'
    # logging.basicConfig(format=logFormat, encoding='utf-8', level=logging.INFO)
    # LOG.setFormat('%(asctime)s:%(levelname)s:%(message)s')
    log_handler = RotatingFileHandler(file, maxBytes=1048576, backupCount=5)
    log_formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
    log_handler.setFormatter(log_formatter)
    LOG = logging.getLogger()
    LOG.addHandler(log_handler)
    LOG.setLevel(logging.INFO)
    return LOG

def has_devices_to_configure(queue):
    if queue.qsize() > 0:
        return True
    return False

def main():
    setup_logging("/home/pi/projects/WalnutGateway.log")
    logging.info("Starting Walnut Gateway")

    configure_device_queue = queue.Queue()
    mqttPublishQueue = queue.Queue()

    client = mqtt.Client(client_id="WalnutGateway")
    client.on_connect = on_connect
    logging.info("Connecting MQTT broker.")
    client.connect("10.77.60.1")
    client.loop_start()

    scanner = Scanner().withDelegate(WalnutScanDelegate(configure_device_queue))

    while True:
        logging.info("----- BLE scan -----------------------------------------------------------------")
        scanEntryList = scanner.scan(timeout=10, passive=False)
        while has_devices_to_configure(configure_device_queue):
            logging.info("Nbr of devices to configure: %s", configure_device_queue.qsize())
            scanEntry = configure_device_queue.get_nowait()
            configure_device(scanEntry)
        while mqttPublishQueue.qsize() > 0:
            (topic, value) = mqttPublishQueue.get_nowait()
            logging.debug("Publish topic: %s value: %s", topic, value)
        for scanEntry in scanEntryList:
            dev = Walnut(scanEntry)
            if dev.isWalnut() == True:
                dev.printDebug()
                dev.append_device_data(mqttPublishQueue, client)


if __name__ == '__main__':
    main()
