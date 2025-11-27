#!/usr/bin/env python3
'''
Otii 3 Controlling the switchboard

If you want the script to login and reserve a license automatically
add a configuration file called credentials.json in the current folder
using the following format:

    {
        "username": "YOUR USERNAME",
        "password": "YOUR PASSWORD"
    }

'''
from otii_tcp_client import otii_client

class AppException(Exception):
    '''Application Exception'''

def control_switchboard(otii):
    '''
    This example shows you how to control the switchboard.
    '''
    # Get a reference to a Arc or Ace device
    devices = otii.get_devices()
    if len(devices) == 0:
        raise AppException('No Arc or Ace connected!')
    device = devices[0]

    # Switch on 5V on the +5V/0-15V pin
    if device.type == 'Arc':
        device.enable_5v(True)
    else:
        device.enable_5v(5)

    # Set GPO1 high
    device.set_gpo(1, True)
    # Set GPO2 low
    device.set_gpo(2, False)

    # Switch off 5V on the +5V/0-15V pin
    if device.type == 'Arc':
        device.enable_5v(False)
    else:
        device.enable_5v(0)

def main():
    '''Connect to the Otii 3 application and run the measurement'''
    client = otii_client.OtiiClient()
    with client.connect() as otii:
        control_switchboard(otii)

if __name__ == '__main__':
    main()
