#!/usr/bin/env python3
'''
Otii 3 Compared with saved

If you want the script to login and reserve a license automatically
add a configuration file called credentials.json in the current folder
using the following format:

    {
        "username": "YOUR USERNAME",
        "password": "YOUR PASSWORD"
    }

'''
import os
import time
from otii_tcp_client import otii_client

MEASUREMENT_DURATION = 5.0
PROJECTS_FOLDER = os.path.join(os.getcwd(), 'projects')
PROJECT_FOLDER = os.path.join(os.getcwd(), PROJECTS_FOLDER, 'compare_with_saved')
MAX_NO_OF_RECORDINGS = 10

class AppException(Exception):
    '''Application Exception'''

def compare_with_saved(otii):
    '''
    This example shows you how to compare a new
    recording with a previously saved one.
    '''
    # Try to open a previously saved project
    if not os.path.isdir(PROJECTS_FOLDER):
        os.mkdir(PROJECTS_FOLDER)

    if os.path.isdir(PROJECT_FOLDER):
        project = otii.open_project(PROJECT_FOLDER)
    else:
        project = otii.create_project()

    # Get a reference to an Arc or Ace device
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

    # Get statistics for the last two recordings
    print_header()
    recordings = project.get_recordings()
    for recording in recordings[-2:]:
        info = recording.get_channel_info(device.id, 'mc')
        statistics = recording.get_channel_statistics(device.id, 'mc', info['from'], info['to'])
        print_statistics(recording, info, statistics)

    # Only keep the last recordings in the project defined by MAX_NO_OF_RECORDINGS
    if len(recordings) > MAX_NO_OF_RECORDINGS:
        delete_recs = recordings[:len(recordings) - MAX_NO_OF_RECORDINGS]
        for rec in delete_recs:
            rec.delete()

    # Save the project
    project.save_as(PROJECT_FOLDER)

def print_header():
    ''' Prints the header for the statistics '''
    print('Recording             From (s)     To (s) Offset (s)  Sample rate    '
          'Min (A)    Max (A)  Average (A)    Energy (Wh)')

def print_statistics(recording, info, statistics):
    ''' Prints the statistics '''
    print(f'{recording.name} {info["from"]:10} {info["to"]:10} {info["offset"]:10}        '
          f'{info["sample_rate"]:5} ', end='')
    print(f'{statistics["min"]:10.5f} {statistics["max"]:10.5f}   {statistics["average"]:10.5f}   '
          f'{statistics["energy"] / 3600:12.6}')

def main():
    '''Connect to the Otii 3 application and run the measurement'''
    client = otii_client.OtiiClient()
    with client.connect() as otii:
        compare_with_saved(otii)

if __name__ == '__main__':
    main()
