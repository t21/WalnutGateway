import logging
import queue
import struct
from bluepy3.btle import Scanner, DefaultDelegate, Peripheral, Service, ScanEntry

#*** db:36:70:83:be:52 -66
#[(8, 'Short Local Name', 'W'),
#(1, 'Flags', '05'),
#(6, 'Incomplete 128b Services', '00001100-0f58-2ba7-72c3-4d8d58fa16de'),
#(22, '16b Service Data', '0f1864')]

class WalnutDevice():
    def __init__(self, scanEntry: ScanEntry):
        self.scanEntry = scanEntry
        self.newDevice = False
        self.configured: bool = scanEntry.getValueText(1) == "06"
        self.hasNewData = True
        self.hasManufacturerData = False
        self.clearDeviceData()
        self.addr = scanEntry.addr
        self.flags = scanEntry.getValueText(ScanEntry.FLAGS)
        self.rssi = scanEntry.rssi
        completeName = scanEntry.getValue(ScanEntry.COMPLETE_LOCAL_NAME)
        shortName = scanEntry.getValue(ScanEntry.SHORT_LOCAL_NAME)
        self.name = completeName or shortName
        serviceData = struct.unpack(">HB", bytes.fromhex(scanEntry.getValueText(ScanEntry.SERVICE_DATA_16B)))
        if serviceData[0] == 0x0f18:
            self.batteryLevel = serviceData[1]
        self.hasManufacturerData = self.parseManufacturerData(scanEntry)

    def __eq__(self, other):
        if isinstance(other, WalnutDevice):
            return self.addr == other.addr
        return False

    @staticmethod
    def isWalnut(scanEntry) -> bool:
        '''
            Check if: Incomplete 128bit Service == '00001100-0f58-2ba7-72c3-4d8d58fa16de'
        '''
        # if scanEntry is None:
        #     return False
        # if '00001100-0f58-2ba7-72c3-4d8d58fa16de' == scanEntry.getValueText(ScanEntry.INCOMPLETE_128B_SERVICES):
        #     return True
        # return False
        is_walnut = scanEntry is not None and scanEntry.getValueText(ScanEntry.INCOMPLETE_128B_SERVICES) == '00001100-0f58-2ba7-72c3-4d8d58fa16de'
        return is_walnut


    def isConfigured(self, scanEntry):
        if scanEntry is None:
            return None
        if scanEntry.getValueText(1) == "06":
            return True
        return False

    def printDebug(self):
        logging.debug("--- Debug print of sensor data start ---")
        logging.debug("Name: %s Addr: %s Flags: %s RSSI: %sdBm" % (self.name, self.addr, self.flags, self.rssi))
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
        logging.debug(logStr)
        # for str in self.scanEntry.getScanData():
        #     print(str)
        #     pass
        logging.debug("--- Debug print of sensor data end ---")

    def clearDeviceData(self):
        self.isWalnutVar = False
        self.name = None
        self.addr = None
        self.flags = None
        self.rssi = None
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
        self.batteryLevel = None

    def getDeviceName(self):
        return self.name

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
        return self.batteryLevel

    def getCO2(self):
        if self.hasManufacturerData:
            return self.co2
        return None

    def parseManufacturerData(self, scanEntry):
        manufacturerData = scanEntry.getValueText(255)
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
