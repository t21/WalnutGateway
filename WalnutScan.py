import logging
import queue
import struct
# from bluepy3.btle import Scanner, DefaultDelegate, Peripheral, Service
import bluepy3

from WalnutDevice import WalnutDevice


class WalnutScanDelegate(bluepy3.btle.DefaultDelegate):
    def __init__(self, configure_device_queue, mqtt_client, walnut_device_list: list[WalnutDevice]):
        bluepy3.btle.DefaultDelegate.__init__(self)
        self.configure_device_queue = configure_device_queue
        self.mqtt_client = mqtt_client
        self.walnut_device_list = walnut_device_list

    def handleDiscovery(self, scanEntry: bluepy3.btle.ScanEntry, isNewDev: bool, isNewData: bool):
        if WalnutDevice.isWalnut(scanEntry):
            walnut = WalnutDevice(scanEntry)
            # print(scanEntry.addr + " isNewDev:" + str(isNewDev) + " isNewData:" + str(isNewData))
            self.publishWalnutMqtt(walnut)

            # Check if walnut exists in the list
            walnut_found = False
            for existing_walnut in self.walnut_device_list:
                if existing_walnut == walnut:  # Or compare based on a unique identifier
                    existing_walnut = walnut
                    walnut_found = True
                    break

            # If not found, append it to the list
            if not walnut_found:
                walnut.newDevice = True
                self.walnut_device_list.append(walnut)

            #if walnut not in self.walnut_device_list:
            #    walnut.newDevice = True
            #    self.walnut_device_list.append(walnut)


            if isNewDev and not walnut.isConfigured(scanEntry):
                self.configure_device_queue.put(scanEntry)

    def publishWalnutMqtt(self, walnut: WalnutDevice):
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

