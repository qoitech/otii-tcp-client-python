#!/usr/bin/env python3
'''
Otii 3 Multiple devices

If you want the script to login and reserve a license automatically
add a configuration file called credentials.json in the current folder
using the following format:

    {
        "username": "YOUR USERNAME",
        "password": "YOUR PASSWORD"
    }

'''
import time
from otii_tcp_client import otii_client

DEVICE1 = 'Arc 1'
DEVICE2 = 'Arc 2'

DEVICE1_MAIN_VOLTAGE = 3.3
DEVICE2_MAIN_VOLTAGE = 3.7

class AppException(Exception):
    '''Application Exception'''

def get_device(otii, name):
    '''
    Find a named device.
    Will throw an exception if no device with that name is found,
    or if multiple devices with the same name is found.
    '''
    devices = [device for device in otii.get_devices() if device.name == name]
    if len(devices) == 0:
        raise AppException(f'No device named {name} found')
    if len(devices) > 1:
        raise AppException(f'Multiple devices named {name} found')
    return devices[0]

def multiple_devices(otii):
    '''
    This example shows you how you can record data
    from multiple devices at once.
    You need to give each device a unique name in the Otii 3 Desktop App.
    '''
    device1 = get_device(otii, DEVICE1)
    device2 = get_device(otii, DEVICE2)

    device1.set_main_voltage(DEVICE1_MAIN_VOLTAGE)
    device2.set_main_voltage(DEVICE2_MAIN_VOLTAGE)

    for channel in ['mc', 'mv', 'mp']:
        device1.enable_channel(channel, True)
        device2.enable_channel(channel, True)

    project = otii.get_active_project()
    project.start_recording()

    device1.set_main(True)
    device2.set_main(True)

    time.sleep(5.0)

    device1.set_main(False)
    device2.set_main(False)

    project.stop_recording()

def main():
    '''Connect to the Otii 3 application and run the measurement'''
    client = otii_client.OtiiClient()
    with client.connect() as otii:
        multiple_devices(otii)

if __name__ == '__main__':
    main()
