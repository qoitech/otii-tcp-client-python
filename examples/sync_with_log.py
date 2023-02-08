#!/usr/bin/env python3
'''
Otii 3 Sync with log

If you want the script to login and reserve a license autmatically
Add a configuration file called credentials.json in the current folder
using the following format:

    {
        "username": "YOUR USERNAME",
        "password": "YOUR PASSWORD",
        "license_id": "YOUR LICENSE ID"
    }

'''
import json
import os
import time
from otii_tcp_client import otii_connection, otii as otii_application

# The default hostname and port of the Otii 3 application
HOSTNAME = '127.0.0.1'
PORT = 1905

CREDENTIALS = './credentials.json'
MEASUREMENT_DURATION = 50.0
START_OF_CYCLE_MESSAGE = 'Connecting...'

def sync_with_log():
    '''
    This example shows you how to use the log output
    to find the start and end point of a complete
    cycle of activity and sleep mode of an IoT device.

    This code expects the messaged defined in START_OF_CYCLE_MSG
    to be written to the log input of the Arc/Ace in the beginning
    of each cycle.

    By finding two consectuive messages, we can get the statistics
    between those points.
    '''
    # Connect to the Otii 3 application
    connection = otii_connection.OtiiConnection(HOSTNAME, PORT)
    connect_response = connection.connect_to_server(try_for_seconds=10)
    if connect_response['type'] == 'error':
        raise Exception(f'Exit! Error code: {connect_response["errorcode"]}, '
                        f'Description: {connect_response["payload"]["message"]}')
    otii = otii_application.Otii(connection)

    # Optional login to the license server and reserve a license
    if os.path.isfile(CREDENTIALS):
        with open(CREDENTIALS, encoding='utf-8') as file:
            credentials = json.load(file)
            otii.login(credentials['username'], credentials['password'])
            otii.reserve_license(credentials['license_id'])

    # Get a reference to a Arc or Ace device
    devices = otii.get_devices()
    if len(devices) == 0:
        raise Exception('No Arc or Ace connected!')
    device = devices[0]

    # Configure the device
    device.set_main_voltage(3.7)
    device.set_exp_voltage(3.3)
    device.set_max_current(0.5)
    device.set_uart_baudrate(115200)
    device.enable_uart(True)
    device.enable_exp_port(True)

    # Enable the main current and rx channel
    device.enable_channel('mc', True)
    device.enable_channel('rx', True)

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

    # Find at least two log messages
    recording = project.get_last_recording()
    count = recording.get_channel_data_count(device.id, 'rx')
    data = recording.get_channel_data(device.id, 'rx', 0, count)
    values = data['values']
    timestamps = [
        value['timestamp'] for value in values
        if value['value'] == START_OF_CYCLE_MESSAGE
    ]
    if len(timestamps) < 2:
        raise Exception(f'Need at least two "{START_OF_CYCLE_MESSAGE}" timestamps')
    from_time = timestamps[0]
    to_time = timestamps[1]

    # Get statistics for the time between the two log entries
    info = recording.get_channel_info(device.id, 'mc')
    statistics = recording.get_channel_statistics(device.id, 'mc', from_time, to_time)

    # Print the statistics
    print(f'From:        {from_time} s')
    print(f'To:          {to_time} s')
    print(f'Offset:      {info["offset"]} s')
    print(f'Sample rate: {info["sample_rate"]}')

    print(f'Min:         {statistics["min"]:.5} A')
    print(f'Max:         {statistics["max"]:.5} A')
    print(f'Average:     {statistics["average"]:.5} A')
    print(f'Energy:      {statistics["energy"] / 3600:.5} Wh')

    # Disconnect from the Otii 3 application
    connection.close_connection()

if __name__ == '__main__':
    sync_with_log()
