#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "otii_tcp_client",
# ]
# ///
'''
Otii 3 Log from a USB UART

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

class AppException(Exception):
    '''Application Exception'''

def usb_uart_log(otii: otii_client.Connect) -> None:
    ''' USB Uart logging '''
    devices = otii.get_devices(devicefilter=['Ace', 'Uart'])
    if len(devices) == 0:
        raise AppException('No devices connected!')

    for device in devices:
        # NOTE: USB UARTs must always be explicitly added to the project
        device.add_to_project()
        device.enable_channel('rx', True)

    otii_device = [ device
        for device in devices
        if device.type == 'Ace'
    ][0]
    assert otii_device

    uart_device = [ device
        for device in devices
        if device.type == 'Uart'
    ][0]
    assert uart_device

    project = otii.get_active_project()
    project.start_recording()
    otii_device.set_main(True)

    time.sleep(5)

    otii_device.set_main(False)
    project.stop_recording()

    recording = project.get_last_recording()
    assert recording
    count = recording.get_channel_data_count(uart_device.id, "rx")
    print(count)
    data = recording.get_channel_data(uart_device.id, "rx", 0, count)
    print(data)

def main() -> None:
    '''Connect to the Otii 3 application and run the measurement'''
    client = otii_client.OtiiClient()
    with client.connect() as otii:
        usb_uart_log(otii)

if __name__ == '__main__':
    main()
