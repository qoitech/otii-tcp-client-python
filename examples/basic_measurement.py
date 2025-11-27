#!/usr/bin/env python3
'''
Otii 3 Basic Measurement

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

MEASUREMENT_DURATION = 5.0

class AppException(Exception):
    '''Application Exception'''

def basic_measurement(otii):
    '''
    This example shows you how to configure and
    start a recording of the main current channel.
    '''
    # Get a reference to a Arc or Ace device
    devices = otii.get_devices()
    if len(devices) == 0:
        raise AppException('No Arc or Ace connected!')
    device = devices[0]

    # Configure the device
    device.set_main_voltage(3.7)
    device.set_exp_voltage(3.3)
    device.set_max_current(0.5)

    # Enable the main current channel
    device.enable_channel('mc', True)

    # Get the active project
    project = otii.get_active_project()

    # Start a recording
    project.start_recording()

    # Turn on the main output of the selected device
    device.set_main(True)

    # Wait for a specified time
    time.sleep(MEASUREMENT_DURATION)

    # Turn off the main output of the selected device
    device.set_main(False)

    # Stop the recording
    project.stop_recording()

    # Get statistics for the recording
    recording = project.get_last_recording()

    print('Recording info')
    print('==============')
    print(f'Name:        {recording.name}')
    print(f'Start time:  {recording.start_time}')
    print('Measurements:')
    for measurement in recording.measurements:
        print('    ', end='')
        print(f'Device: {measurement["device_id"]}', end='')
        print(f', {measurement["channel"]}', end='')
        if 'sample_rate' in measurement:
            print(f', sample rate: {measurement["sample_rate"]}', end='')
        print('')
    print('')

    info = recording.get_channel_info(device.id, 'mc')
    statistics = recording.get_channel_statistics(device.id, 'mc', info['from'], info['to'])

    # Print the statistics
    print('Statistics')
    print('==========')
    print(f'From:        {info["from"]} s')
    print(f'To:          {info["to"]} s')
    print(f'Offset:      {info["offset"]} s')
    print(f'Sample rate: {info["sample_rate"]}')
    print('')

    print(f'Min:         {statistics["min"]:.5} A')
    print(f'Max:         {statistics["max"]:.5} A')
    print(f'Average:     {statistics["average"]:.5} A')
    print(f'Energy:      {statistics["energy"] / 3600:.5} Wh')

def main():
    '''Connect to the Otii 3 application and run the measurement'''
    client = otii_client.OtiiClient()
    with client.connect() as otii:
        basic_measurement(otii)

if __name__ == '__main__':
    main()
