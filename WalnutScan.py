import logging
import queue
import struct
from bluepy.btle import Scanner, DefaultDelegate, Peripheral, Service

#*** db:36:70:83:be:52 -66
#[(8, 'Short Local Name', 'W'),
#(1, 'Flags', '05'),
#(6, 'Incomplete 128b Services', '00001100-0f58-2ba7-72c3-4d8d58fa16de'),
#(22, '16b Service Data', '0f1864')]

class Walnut():
    def __init__(self, scanEntry):
        self.scanEntry = scanEntry
        self.hasManufacturerData = False
        self.clearDeviceData()
        if self.isWalnut():
            self.hasManufacturerData = self.parseManufacturerData()

    def isWalnut(self):
        # TODO: Change detection method
        if 'W' == self.scanEntry.getValueText(8):
#            print("*****", self.scanEntry.addr, self.scanEntry.rssi)
#            print('*****', self.scanEntry.getScanData())
            return True
        return False

    def isConfigured(self):
        if self.scanEntry.getValueText(1) == "06":
            return True
        return False

    def printDebug(self):
        logging.debug("--- Debug print of sensor data start ---")
        logging.info("Name: %s Addr: %s Flags: %s RSSI: %sdBm" % (self.getDeviceName(), self.scanEntry.addr, self.scanEntry.getValueText(1), self.scanEntry.rssi))
        logStr = ""
        if (self.getTemperature() != None):
            logStr += "T:" + str(self.getTemperature()) + "degC "
        if (self.getRelativeHumidity() is not None):
            logStr += "RH:" + str(self.getRelativeHumidity()) + "% "
        if self.getAmbientLight() is not None:
            logStr += str(self.getAmbientLight()) + "Lux "
        if self.getPresence() is not None:
            logStr += "M:" + str(self.getPresence()) + " "
        if self.getBarometricPressure() is not None:
            logStr += "P:" + str(self.getBarometricPressure()) + "mbar "
        if self.getBatteryLevel() is not None:
            logStr += "Bat:" + str(self.getBatteryLevel()) + "% "
        logging.info(logStr)
        # for str in self.scanEntry.getScanData():
        #     print(str)
        #     pass
        logging.debug("--- Debug print of sensor data end ---")

    def clearDeviceData(self):
        self.temperature = None
        self.humidity = None
        self.ambientLight = None
        self.moisture = None
        self.accel_x = None
        self.accel_y = None
        self.accel_z = None
        self.gyro_x = None
        self.gyro_y = None
        self.gyro_z = None
        self.magnetometer_x = None
        self.magnetometer_y = None
        self.magnetometer_z = None
        self.presence = None
        self.baroPressure = None
        self.led = None
        self.manufacturerBatteryLevel = None
        self.co2 = None
        self.alarm1 = None
        self.pm25 = None
        self.pm10 = None
        self.pm1 = None
        self.button = None
        self.battery = None

    def getDeviceName(self):
        completeName = self.scanEntry.getValue(9)
        shortName = self.scanEntry.getValue(8)
        if completeName is not None:
            return completeName
        elif shortName is not None:
            return shortName
        return None

    def getTemperature(self):
        if self.hasManufacturerData:
            return self.temperature
        return None

    def getRelativeHumidity(self):
        if self.hasManufacturerData:
            return self.humidity
        return None

    def getAmbientLight(self):
        if self.hasManufacturerData:
            return self.ambientLight
        return None

    def getPresence(self):
        if self.hasManufacturerData:
            return self.presence
        return None

    def getBarometricPressure(self):
        if self.hasManufacturerData:
            return self.baroPressure
        return None

    def getBatteryLevel(self):
        if not self.isWalnut:
            return None
        if self.hasManufacturerData and self.manufacturerBatteryLevel is not None:
            return self.manufacturerBatteryLevel
        serviceData = struct.unpack(">HB", bytes.fromhex(self.scanEntry.getValueText(22)))
        if serviceData[0] == 0x0f18:
            batteryLevel = serviceData[1]
            return batteryLevel
        return None

    def getCO2(self):
        if self.hasManufacturerData:
            return self.co2
        return None

    def parseManufacturerData(self):
        manufacturerData = self.scanEntry.getValueText(255)
        if manufacturerData == None:
            return False
        logging.debug("--- Parsing advertisement start ---")
        manufacturer = manufacturerData[0:4]
        logging.debug("Manufacturer: %s", manufacturer)
        idx = 4
        while idx < len(manufacturerData):
            sensorId = manufacturerData[idx:idx + 4]
            idx += 4
            logging.debug("SensorID: %s", sensorId)
            if sensorId == "0001":
                self.temperature = struct.unpack('>h', bytes.fromhex(manufacturerData[idx:idx + 4]))[0] / 10
                idx += 4
            elif sensorId == "0002":
                self.humidity = int(manufacturerData[idx:idx + 4], 16) / 10
                idx += 4
            elif sensorId == "0003":
                self.ambientLight = int(manufacturerData[idx:idx + 4], 16)
                idx += 4
            elif sensorId == "0004":
                self.moisture = int(manufacturerData[idx:idx + 4], 16)
                # print(self.moisture)
                idx += 4
            elif sensorId == "0005":
                self.accel_x = int(manufacturerData[idx:idx + 2], 16)
                self.accel_y = int(manufacturerData[idx + 2:idx + 4], 16)
                self.accel_z = int(manufacturerData[idx + 4:idx + 6], 16)
                # print(self.accel_x, self.accel_y, self.accel_z)
                idx += 6
            elif sensorId == "0006":
                self.gyro_x = int(manufacturerData[idx:idx + 2], 16)
                self.gyro_y = int(manufacturerData[idx + 2:idx + 4], 16)
                self.gyro_z = int(manufacturerData[idx + 4:idx + 6], 16)
                # print(self.gyro_x, self.gyro_y, self.gyro_z)
                idx += 6
            elif sensorId == "0007":
                self.magnetometer_x = int(manufacturerData[idx:idx + 2], 16)
                self.magnetometer_y = int(manufacturerData[idx + 2:idx + 4], 16)
                self.magnetometer_z = int(manufacturerData[idx + 4:idx + 6], 16)
                # print(self.magnetometer_x, self.magnetometer_y, self.magnetometer_z)
                idx += 6
            elif sensorId == "0008":
                self.presence = int(manufacturerData[idx:idx + 2], 16)
                idx += 2
            elif sensorId == "0009":
                self.baroPressure = int(manufacturerData[idx:idx + 4], 16) / 10
                idx += 4
            elif sensorId == "000a" :
                self.led = int(manufacturerData[idx:idx + 2], 16)
                # print(self.led)
                idx += 2
            elif sensorId == "000b":
                self.battery = int(manufacturerData[idx:idx + 2], 16)
                # print(self.battery)
                idx += 2
            elif sensorId == "000c":
                self.co2 = int(manufacturerData[idx:idx + 4], 16)
                # print(self.co2)
                idx += 4
            elif sensorId == "000d":
                self.alarm1 = int(manufacturerData[idx:idx + 2], 16)
                # print(self.alarm1)
                idx += 2
            elif sensorId == "0010":
                self.pm25 = int(manufacturerData[idx:idx + 4], 16)
                # print(self.pm25)
                idx += 4
            elif sensorId == "0011":
                self.pm10 = int(manufacturerData[idx:idx + 4], 16)
                # print(self.pm10)
                idx += 4
            elif sensorId == "0012":
                self.pm1 = int(manufacturerData[idx:idx + 4], 16)
                # print(self.pm1)
                idx += 4
            elif sensorId == "0013":
                self.button = int(manufacturerData[idx:idx + 2], 16)
                # print(self.button)
                idx += 2
        logging.debug("--- Parsing advertisement end ---")
        return True

    def append_device_data(self, queue, mqtt_client=None):
        base_topic = "walnuts/" + self.scanEntry.addr + "/"
        rssi_topic = base_topic + "rssi"
        if mqtt_client is None:
            queue.put_nowait((rssi_topic, self.scanEntry.rssi))
        else:
            mqtt_client.publish(rssi_topic, self.scanEntry.rssi)
        if self.getTemperature() != None:
            temperature_topic = base_topic + "sensors/temperature"
            if mqtt_client is None:
                queue.put_nowait((temperature_topic, self.getTemperature()))
            else:
                mqtt_client.publish(temperature_topic, self.getTemperature())
        if self.getRelativeHumidity() is not None:
            relative_humidity_topic = base_topic + "sensors/relative_humidity"
            if mqtt_client is None:
                queue.put_nowait((relative_humidity_topic, self.getRelativeHumidity()))
            else:
                mqtt_client.publish(relative_humidity_topic, self.getRelativeHumidity())
        if self.getAmbientLight() is not None:
            ambient_light_topic = base_topic + "sensors/ambient_light"
            if mqtt_client is None:
                queue.put_nowait((ambient_light_topic, self.getAmbientLight()))
            else:
                mqtt_client.publish(ambient_light_topic, self.getAmbientLight())
        if self.getPresence() is not None:
            presence_topic = base_topic + "sensors/presence"
            if mqtt_client is None:
                queue.put_nowait((presence_topic, self.getPresence()))
            else:
                mqtt_client.publish(presence_topic, self.getPresence())
        if self.getBarometricPressure() is not None:
            barometric_pressure_topic = base_topic + "sensors/barometric_pressure"
            if mqtt_client is None:
                queue.put_nowait((barometric_pressure_topic, self.getBarometricPressure()))
            else:
                mqtt_client.publish(barometric_pressure_topic, self.getBarometricPressure())
        if self.getBatteryLevel() is not None:
            battery_level_topic = base_topic + "battery"
            if mqtt_client is None:
                queue.put_nowait((battery_level_topic, self.getBatteryLevel()))
            else:
                mqtt_client.publish(battery_level_topic, self.getBatteryLevel())
        if self.getCO2() is not None:
            co2_topic = base_topic + "sensors/co2"
            if mqtt_client is None:
                queue.put_nowait((co2_topic, self.getCO2()))
            else:
                mqtt_client.publish(co2_topic, self.getCO2())


class WalnutScanDelegate(DefaultDelegate):
    def __init__(self, configure_device_queue, mqtt_publish_queue=None, mqtt_client=None):
        DefaultDelegate.__init__(self)
        self.configure_device_queue = configure_device_queue
        self.mqtt_publish_queue = mqtt_publish_queue
        self.mqttc = mqtt_client

    def handleDiscovery(self, scanEntry, isNewDev, isNewData):
        dev = Walnut(scanEntry)
        if dev.isWalnut() and self.mqtt_publish_queue is not None:
            dev.printDebug()
            logging.info("isNewDev:%s isNewData:%s", isNewDev, isNewData)
            dev.append_device_data(self.mqtt_publish_queue, self.mqttc)
        if isNewDev and dev.isWalnut() == True and dev.isConfigured() == False:
            self.configure_device_queue.put(scanEntry)
