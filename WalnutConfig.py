import logging
import queue

from struct import unpack

from bluepy.btle import Scanner, DefaultDelegate, Peripheral, Service


# Supported hardware variants
HW_ID_CLIMATE = 4
HW_ID_CONFERENCE = 5


climate_configuration = [
    bytes("W=1,1,1", 'ascii'),          # Enable temperature sensor
    bytes("W=1,2,1", 'ascii'),          # Include temperature sensor in advertisement
    bytes("W=1,3,EA60", 'ascii'),       # Set measurement interval to 60s
    bytes("W=1,FFFE,FFFE", 'ascii'),    # Store temperature configuration in flash
    bytes("W=2,1,1", 'ascii'),          # Enable humidity sensor
    bytes("W=2,2,1", 'ascii'),          # Include humidity sensor in advertisement
    bytes("W=2,3,EA60", 'ascii'),       # Set measurement interval to 60s
    bytes("W=2,FFFE,FFFE", 'ascii'),    # Store humidity configuration in flash
    bytes("W=3,1,1", 'ascii'),          # Enable light sensor
    bytes("W=3,2,1", 'ascii'),          # Include light sensor in advertisement
    bytes("W=3,3,EA60", 'ascii'),       # Set measurement interval to 60s
    bytes("W=3,FFFE,FFFE", 'ascii'),    # Store light sensor configuration in flash
    bytes("W=9,1,1", 'ascii'),          # Enable pressure sensor
    bytes("W=9,2,1", 'ascii'),          # Include pressure sensor in advertisement
    bytes("W=9,3,EA60", 'ascii'),       # Set measurement interval to 60s
    bytes("W=9,FFFE,FFFE", 'ascii'),    # Store pressure sensor configuration in flash
    bytes("W=0,0,1", 'ascii'),          # Advertisement mode
    bytes("W=0,1,500", 'ascii'),        # Advertisement interval 1.28s
    bytes("W=0,2,4", 'ascii'),          # 4dBm output power
    bytes("W=0,FFFE,FFFE", 'ascii')     # Store settings
]

conference_configuration = [
    bytes("W=1,1,1", 'ascii'),          # Enable temperature sensor
    bytes("W=1,2,1", 'ascii'),          # Include temperature sensor in advertisement
    bytes("W=1,3,EA60", 'ascii'),       # Set measurement interval to 60s
    bytes("W=1,FFFE,FFFE", 'ascii'),    # Store temperature configuration in flash
    bytes("W=2,1,1", 'ascii'),          # Enable humidity sensor
    bytes("W=2,2,1", 'ascii'),          # Include humidity sensor in advertisement
    bytes("W=2,3,EA60", 'ascii'),       # Set measurement interval to 60s
    bytes("W=2,FFFE,FFFE", 'ascii'),    # Store humidity configuration in flash
    bytes("W=3,1,1", 'ascii'),          # Enable light sensor
    bytes("W=3,2,1", 'ascii'),          # Include light sensor in advertisement
    bytes("W=3,3,EA60", 'ascii'),       # Set measurement interval to 60s
    bytes("W=3,FFFE,FFFE", 'ascii'),    # Store light sensor configuration in flash
    bytes("W=8,1,1", 'ascii'),          # Enable PIR sensor
    bytes("W=8,2,1", 'ascii'),          # Include PIR sensor in advertisement
    bytes("W=8,8,1", 'ascii'),          # Set min_int
    bytes("W=8,9,0", 'ascii'),          # Set occupied_thld
    bytes("W=8,10,2", 'ascii'),         # Set quiet_time
    bytes("W=8,11,20", 'ascii'),        # Set timeout_period
    bytes("W=8,FFFE,FFFE", 'ascii'),    # Store light sensor configuration in flash
    bytes("W=0,0,1", 'ascii'),          # Advertisement mode
    bytes("W=0,1,500", 'ascii'),        # Advertisement interval 1.28s
    bytes("W=0,2,4", 'ascii'),          # 4dBm output power
    bytes("W=0,FFFE,FFFE", 'ascii')     # Store settings
]


class ConfigDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        logging.debug("Notification data: %s", data)
        # TODO: Handle errors in configuration
#        if data in "ERROR" or "OK":
#            index += 1


def configure_device(scanEntry):
    logging.info("Connecting to: %s", scanEntry.addr)
    try:
        peripheral_device = Peripheral(scanEntry)
    except:
        logging.warning("_-_-_ Failed to connect to: %s", scanEntry.addr)
    else:
        peripheral_device.setDelegate(ConfigDelegate())
        # serviceList = peripheral_device.getServices()
        # logging.debug(serviceList)
        # logging.debug(list(serviceList))
        # for service in peripheral_device.getServices():
        #     logging.debug("S: %s", service.uuid)
        #     for characteristic in service.getCharacteristics():
        #         logging.debug("C: %s", characteristic.uuid)

        # Read HW ID and apply corresponding configuration
        hw_id_char = peripheral_device.getCharacteristics(uuid="00001101-0f58-2ba7-72c3-4d8d58fa16de")[0]
        hw_id = unpack("H", hw_id_char.read())[0]
        logging.info("HWID:%s", hw_id)
        if hw_id == HW_ID_CLIMATE:
            config = climate_configuration
        elif hw_id == 5:
            config = conference_configuration
        else:
            peripheral_device.disconnect()
            return

        uartRxChar = peripheral_device.getCharacteristics(uuid="6e400003-b5a3-f393-e0a9-e50e24dcca9e")[0]
        uartTxChar = peripheral_device.getCharacteristics(uuid="6e400002-b5a3-f393-e0a9-e50e24dcca9e")[0]
        # logging.debug(uartRxChar)
        # logging.debug(uartTxChar)
        # logging.debug("RX char properties: %s", uartRxChar.propertiesToString())
        # logging.debug("TX char properties: %s", uartTxChar.propertiesToString())
        logging.debug("Enable notification")
        uartRxCharDescriptorHandle = uartRxChar.getHandle() + 1
        peripheral_device.writeCharacteristic(uartRxCharDescriptorHandle , (1).to_bytes(2, byteorder='little'))
        # logging.debug(uartRxChar.getHandle())
        # logging.debug(uartTxChar.getHandle())
        for x in range(0, len(config)):
            # logging.debug(x)
            uartTxChar.write(config[x])
            if peripheral_device.waitForNotifications(1):
                pass
                # logging.debug("Notification received")
            else:
                logging.debug("No notification received")
            peripheral_device.waitForNotifications(1)
        logging.info("Configuration complete")
        peripheral_device.disconnect()



#S 00001800-0000-1000-8000-00805f9b34fb
#C 00002a00-0000-1000-8000-00805f9b34fb
#C 00002a01-0000-1000-8000-00805f9b34fb
#C 00002a04-0000-1000-8000-00805f9b34fb
#S 00001801-0000-1000-8000-00805f9b34fb
#S 0000180a-0000-1000-8000-00805f9b34fb
#C 00002a29-0000-1000-8000-00805f9b34fb
#C 00002a24-0000-1000-8000-00805f9b34fb
#C 00002a27-0000-1000-8000-00805f9b34fb
#C 00002a26-0000-1000-8000-00805f9b34fb
#C 00002a28-0000-1000-8000-00805f9b34fb
#S 0000180f-0000-1000-8000-00805f9b34fb
#C 00002a19-0000-1000-8000-00805f9b34fb
#S 00001100-0f58-2ba7-72c3-4d8d58fa16de
#C 00001101-0f58-2ba7-72c3-4d8d58fa16de
#C 00001103-0f58-2ba7-72c3-4d8d58fa16de
#C 00001106-0f58-2ba7-72c3-4d8d58fa16de
#C 00001107-0f58-2ba7-72c3-4d8d58fa16de
#C 00001108-0f58-2ba7-72c3-4d8d58fa16de
#S 6e400001-b5a3-f393-e0a9-e50e24dcca9e
#C 6e400003-b5a3-f393-e0a9-e50e24dcca9e
#C 6e400002-b5a3-f393-e0a9-e50e24dcca9e
#S 00001530-1212-efde-1523-785feabcd123
#C 00001532-1212-efde-1523-785feabcd123
#C 00001531-1212-efde-1523-785feabcd123

