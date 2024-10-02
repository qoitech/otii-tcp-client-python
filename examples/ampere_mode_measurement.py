#!/usr/bin/env python3
'''
Otii 3 Ampere mode measurement

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

MEASUREMENT_INTERVAL = 1.0
VOLTAGE_THRESHOLD = 2.8

class AppException(Exception):
    '''Application Exception'''

def ampere_mode_measurement(otii):
    '''
    This example shows you how to compute the actual current
    consumption using the real power source of the device.
    The device is connected inline with the power source, see
    https://www.qoitech.com/usecases/ampere-mode-current-measurements-of-embedded-devices
    '''
    # Get a reference to a Arc or Ace device
    devices = otii.get_devices()
    if len(devices) != 1:
        raise AppException(
            f'Exactly 1 device expected to be connected, found {len(devices)} devices'
        )
    device = devices[0]

    # Enable channels
    device.enable_channel('mc', True)
    device.enable_channel('mv', True)
    device.enable_channel('mp', True)

    # Set inline mode
    device.set_power_regulation('inline')

    # Set 4-wire
    device.set_4wire(True)

    # Get the active project
    project = otii.get_active_project()

    # Start a recording
    project.start_recording()

    # Turn on the main output of the selected device
    device.set_main(True)

    # Loop until voltage is below threshold
    recording = project.get_last_recording()
    from_time = 0
    to_time = 0
    while True:
        time.sleep(MEASUREMENT_INTERVAL)
        info = recording.get_channel_info(device.id, 'mv')
        to_time = info['to']
        statistics = recording.get_channel_statistics(device.id, 'mv', from_time, to_time)
        if statistics['min'] < VOLTAGE_THRESHOLD:
            break
        from_time = to_time

    # Turn off the main output of the selected device
    device.set_main(False)

    # Stop the recording
    project.stop_recording()

    # Get energy for complete recording
    main_current_stats = recording.get_channel_statistics(device.id, 'mc', 0, to_time)
    energy = main_current_stats['energy'] / 3600

    main_voltage_stats = recording.get_channel_statistics(device.id, 'mv', 0, to_time)
    average_voltage = main_voltage_stats['average']
    capacity = energy / average_voltage

    print(f'Energy:   {energy} Wh')
    print(f'Capacity: {capacity} Ah')

def main():
    '''Connect to the Otii 3 application and run the measurement'''
    client = otii_client.OtiiClient()
    with client.connect() as otii:
        ampere_mode_measurement(otii)

if __name__ == '__main__':
    main()
