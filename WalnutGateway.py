#!/usr/bin/python3

import json
import logging
import os
import queue
import sys
from logging.handlers import RotatingFileHandler

from bluepy3.btle import Scanner, DefaultDelegate, Peripheral, Service, BTLEManagementError
import paho.mqtt.client as mqtt

from WalnutScan import WalnutScanDelegate
from WalnutConfig import configure_device
from WalnutDevice import WalnutDevice


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("MQTT Connection successful")
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

def publishNewWalnutConfig(mqtt_client, walnut: WalnutDevice):
    unique_id = "walnut_" + walnut.addr.replace(":", "")
    topic = "homeassistant/device/" + unique_id + "/config"
    device_config = {
        "dev": {
            "ids": "[" + unique_id + "]",
            "name": "Walnut",
            "mf": "Berg",
            "mdl": "Walnut Climate",
            "sw": "1.0",
            "sn": unique_id,
            "hw": "2.1"
        },
        "o": {
            "name": "WalnutGateway.local",
            "sw": "1.1"
        },
        "cmps": {
            "temperature": {
                "p": "sensor",
                "device_class": "temperature",
                "unit_of_measurement": "°C",
                "value_template": "{{ value_json.temperature }}",
                "unique_id": unique_id + "_t"
            },
            "humidity": {
                "p": "sensor",
                "device_class": "humidity",
                "unit_of_measurement": "%",
                "value_template": "{{ value_json.humidity }}",
                "unique_id": unique_id + "_h"
            }
        },
        "state_topic": "walnuts/" + walnut.addr.replace(":", "") + "/state",
        "qos": 2
    }

    json_string = json.dumps(device_config)

    logging.info("Publish config:" + topic)
    logging.info("Message:" + json_string)
    mqtt_client.publish(topic, json_string)


def publishNewWalnutSensorData(mqtt_client, walnut: WalnutDevice):
    unique_id = "walnut_" + walnut.addr.replace(":", "")
    topic = "walnuts/" + walnut.addr.replace(":", "") + "/state"
    sensor_data = {
        "temperature": walnut.getTemperature()
    }
    # device_config = {
    #     "dev": {
    #         "ids": "[" + unique_id + "]",
    #         "name": "Walnut",
    #         "mf": "Berg",
    #         "mdl": "Walnut Climate",
    #         "sw": "1.0",
    #         "sn": unique_id,
    #         "hw": "2.1"
    #     },
    #     "o": {
    #         "name": "WalnutGateway.local",
    #         "sw": "1.1"
    #     },
    #     "cmps": {
    #         "temperature": {
    #             "p": "sensor",
    #             "device_class": "temperature",
    #             "unit_of_measurement": "°C",
    #             "value_template": "{{ value_json.temperature }}",
    #             "unique_id": unique_id + "_t"
    #         },
    #         "humidity": {
    #             "p": "sensor",
    #             "device_class": "humidity",
    #             "unit_of_measurement": "%",
    #             "value_template": "{{ value_json.humidity }}",
    #             "unique_id": unique_id + "_h"
    #         }
    #     },
    #     "state_topic": "walnuts/" + walnut.addr.replace(":", "") + "/state",
    #     "qos": 2
    # }

    json_string = json.dumps(sensor_data)

    # logging.info("Publish config:" + topic)
    # logging.info("Message:" + json_string)
    mqtt_client.publish(topic, json_string)


def main():
    btleErrorCount = 0
    setup_logging("/home/thomas/WalnutGateway/WalnutGateway.log")
    logging.info("Starting Walnut Gateway")

    configure_device_queue = queue.Queue()
    walnut_device_list: list[WalnutDevice] = []

    client = mqtt.Client(client_id="WalnutGateway")
    client.username_pw_set(username="thomas", password="berg")
    client.on_connect = on_connect
    client.on_disconnect = on_mqtt_disconnect
    client.on_publish = on_mqtt_publish
    logging.info("Connecting MQTT broker.")
    client.connect("homer.local")
    client.loop_start()

    scanner = Scanner().withDelegate(WalnutScanDelegate(configure_device_queue, client, walnut_device_list))
    logging.info("Starting BLE scan")

    while True:
        logging.debug("----- BLE scan -----")
        try:
            scanner.scan(timeout=30, passive=False)
        except BTLEManagementError:
            logging.error("BTLEManagementError")
            btleErrorCount += 1
            if btleErrorCount > 10:
                # os.system('sudo shutdown -r now')
                pass
        except:
            logging.error("Unknown Error")
        else:
            btleErrorCount = 0

        # Configure new Walnut Devices
        while has_devices_to_configure(configure_device_queue):
            logging.info("Nbr of devices to configure: %s", configure_device_queue.qsize())
            scanEntry = configure_device_queue.get_nowait()
            configure_device(scanEntry)

        # Send Home Assistant config to MQTT broker
        for walnut in walnut_device_list:
            if walnut.newDevice:
                publishNewWalnutConfig(client, walnut)
                walnut.newDevice = False

        # Send Walnut sensor data to MQTT broker
        for walnut in walnut_device_list:
            if walnut.hasNewData:
                publishNewWalnutSensorData(client, walnut)
                walnut.hasNewData = False

        logging.info("=====")
        logging.info(len(walnut_device_list))
        for walnut in walnut_device_list:
            logging.info(walnut.addr)
            logging.info(walnut.newDevice)
            logging.info(walnut.configured)
        logging.info("=====")


if __name__ == '__main__':
    main()
