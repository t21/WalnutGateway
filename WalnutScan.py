import logging
import queue
import struct
from bluepy.btle import Scanner, DefaultDelegate, Peripheral, Service

from WalnutDevice import WalnutDevice


class WalnutScanDelegate(DefaultDelegate):
    def __init__(self, configure_device_queue, mqtt_client):
        DefaultDelegate.__init__(self)
        self.configure_device_queue = configure_device_queue
        self.mqtt_client = mqtt_client

    def handleDiscovery(self, scanEntry, isNewDev, isNewData):
        walnut = WalnutDevice(scanEntry)
        if walnut.isWalnut():
            # print("isNewDev:" + str(isNewDev) + "isNewData:" + str(isNewData))
            # print(walnut.addr)
            # print(walnut.getTemperature())
            self.publishWalnutMqtt(walnut)
        # if dev.isWalnut() and self.mqtt_publish_queue is not None:
        #     dev.printDebug()
        #     logging.info("isNewDev:%s isNewData:%s", isNewDev, isNewData)
        #     dev.append_device_data(self.mqtt_publish_queue, self.mqtt_client)
        if isNewDev and walnut.isWalnut() and not walnut.isConfigured(scanEntry):
            self.configure_device_queue.put(scanEntry)

    def publishWalnutMqtt(self, walnut):
        if self.mqtt_client is None or walnut is None:
            return
        base_topic = "walnuts/" + walnut.addr + "/"
        self.publishWalnutRssi(base_topic, walnut.rssi)
        self.publishWalnutTemperature(base_topic, walnut.getTemperature())
        self.publishWalnutHumidity(base_topic, walnut.getRelativeHumidity())
        self.publishWalnutAmbientLight(base_topic, walnut.getAmbientLight())
        self.publishWalnutPresence(base_topic, walnut.getPresence())
        self.publishWalnutBarometricPressure(base_topic, walnut.getBarometricPressure())
        self.publishWalnutBatteryLevel(base_topic, walnut.getBatteryLevel())
        self.publishWalnutCO2(base_topic, walnut.getCO2())
        walnut.printDebug()

    def publishWalnutRssi(self, base_topic, rssi):
        self.mqtt_client.publish(base_topic + "rssi", rssi)

    def publishWalnutTemperature(self, base_topic, temperature):
        if base_topic and temperature is not None:
            self.mqtt_client.publish(base_topic + "sensors/temperature", temperature)

    def publishWalnutHumidity(self, base_topic, humidity):
        if base_topic and humidity is not None:
            self.mqtt_client.publish(base_topic + "sensors/relative_humidity", humidity)

    def publishWalnutAmbientLight(self, base_topic, ambient_light):
        if base_topic and ambient_light is not None:
            self.mqtt_client.publish(base_topic + "sensors/ambient_light", ambient_light)

    def publishWalnutPresence(self, base_topic, presence):
        if base_topic and presence is not None:
            self.mqtt_client.publish(base_topic + "sensors/presence", presence)

    def publishWalnutBarometricPressure(self, base_topic, barometric_pressure):
        if base_topic and barometric_pressure is not None:
            self.mqtt_client.publish(base_topic + "sensors/barometric_pressure", barometric_pressure)

    def publishWalnutBatteryLevel(self, base_topic, battery_level):
        if base_topic and battery_level is not None:
            self.mqtt_client.publish(base_topic + "sensors/battery", battery_level)

    def publishWalnutCO2(self, base_topic, co2):
        if base_topic and co2 is not None:
            self.mqtt_client.publish(base_topic + "sensors/co2", co2)
