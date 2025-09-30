#!/usr/bin/env python3
'''
Otii 3 Voltage sweep

If you want the script to login and reserve a license automatically
add a configuration file called credentials.json in the current folder
using the following format:

    {
        "username": "YOUR USERNAME",
        "password": "YOUR PASSWORD"
    }

'''
import time
from datetime import datetime
from typing import Literal, Optional
from otii_tcp_client import arc, otii_client, recording

# Sweep settings
START_VOLTAGE = 4.2
STOP_VOLTAGE = 3.0
STEP = 0.1
WAIT_AFTER_CONDITION = 0.2

# Device settings
OVERCURRENT = 1
BAUDRATE = 115200
DIGITAL_VOLTAGE = 3.3

# Condition type
ConditionType = Literal["message", "falling_edge", "gpio"]
INITIAL_CONDITION_TYPE: ConditionType = 'message'
CONDITION_TYPE: ConditionType = 'message'

# Condition - wait for message
MESSAGE_TEXT = 'Entering sleep mode'
MESSAGE_POLLING_TIME = 0.2
MESSAGE_TIMEOUT = 60

# Condition - wait for falling_edge
FALLING_EDGE_CURRENT_THRESHOLD = 0.040
FALLING_EDGE_SAMPLE_TIME = 0.2
FALLING_EDGE_TIMEOUT = 60

# Condition - wait for GPI1 change
GPI1_EDGE = 'any' # 'falling', 'raising' or 'any'
GPI1_POLLING_TIME = 0.2
GPI1_TIMEOUT = 60

class AppException(Exception):
    '''Application Exception'''

def voltage_sweep(otii: otii_client.Connect) -> None:
    '''
    This example shows how an automatic voltage sweep can be done, triggering on
    an UART message, a falling edge in current measurement or a GPI change.
    '''
    # Get a reference to a Arc or Ace device
    devices = otii.get_devices()
    if len(devices) != 1:
        raise AppException(
            f'Exactly 1 device expected to be connected, found {len(devices)} devices'
        )
    device = devices[0]

    # Set up and enable channels
    for channel in ['mc', 'mv', 'mp', 'gpi1', 'rx']:
        device.enable_channel(channel, True)

    # Set sample rate
    for channel in ['mc', 'mv', 'mp']:
        device.set_channel_samplerate(channel, 50000)

    # Configure device
    device.set_main_voltage(START_VOLTAGE)
    device.set_max_current(OVERCURRENT)
    device.set_uart_baudrate(BAUDRATE)
    device.set_exp_voltage(DIGITAL_VOLTAGE)

    # Start measuring
    print('Starting and waiting for initial condition')
    project = otii.get_active_project()
    project.start_recording()
    device.set_main(True)

    recording = project.get_last_recording()
    assert recording is not None
    timestamp_condition = wait_for_condition(INITIAL_CONDITION_TYPE, recording, device)
    recording.rename('Initialization')

    print(f'Initializing done at timestamp: {timestamp_condition}')
    time.sleep(WAIT_AFTER_CONDITION)

    # Start voltage sweep
    start_voltage = int(START_VOLTAGE * 1000)
    stop_voltage = int(STOP_VOLTAGE * 1000)
    step = int(-STEP * 1000)
    for voltage in range(start_voltage, stop_voltage, step):
        print(f'\nSetting {voltage / 1000} output voltage')
        device.set_main_voltage(voltage / 1000)
        project.start_recording()

        recording = project.get_last_recording()
        assert recording is not None
        timestamp_condition = wait_for_condition(CONDITION_TYPE, recording, device)
        if timestamp_condition is not None:
            print(f'Condition {CONDITION_TYPE} found at timestamp: {timestamp_condition}')

        recording.rename(f'Voltage {voltage / 1000:.2f}')
        time.sleep(WAIT_AFTER_CONDITION)

    device.set_main(False)

    print('\nStopping recording')
    project.stop_recording()

    print('Done!')

def wait_for_condition(condition_type: ConditionType, recording: recording.Recording, device: arc.Arc) -> Optional[float]:
    ''' Wait for a condition '''
    if condition_type == 'message':
        return wait_for_message(recording, device)

    if condition_type == 'falling_edge':
        return wait_for_falling_edge(recording, device)

    if condition_type == 'gpio':
        return wait_for_gpi(recording, device)

    raise AppException(f'Unknown condition type {condition_type}')

def wait_for_message(recording: recording.Recording, device: arc.Arc) -> Optional[float]:
    ''' Wait for message on UART '''
    start_time = datetime.now()
    found_message = False
    timestamp = None
    previous_samples = recording.get_channel_data_count(device.id, 'rx')

    # Loop until message is found or time-out
    while not found_message:
        time.sleep(MESSAGE_POLLING_TIME)

        # Count the number of messages received
        samples = recording.get_channel_data_count(device.id, 'rx')

        if samples > previous_samples:
            # Get the new messages
            rx_data = recording.get_channel_data(device.id,
                                                 'rx',
                                                 previous_samples,
                                                 samples - previous_samples
                                                 )
            for data in rx_data['values']:
                if MESSAGE_TEXT in data['value']:
                    found_message = True
                    timestamp = data['timestamp']

            previous_samples = samples

        if (datetime.now() - start_time).seconds > MESSAGE_TIMEOUT > 0:
            print('Maximum time reached, not found message')
            break

    return timestamp

def wait_for_falling_edge(recording: recording.Recording, device: arc.Arc) -> Optional[float]:
    ''' Wait for falling edge '''
    start_time = datetime.now()
    from_time = 0
    last_average = 0

    while True:
        time.sleep(FALLING_EDGE_SAMPLE_TIME)

        info = recording.get_channel_info(device.id, 'mc')
        to_time = info['to']
        statistics = recording.get_channel_statistics(device.id, 'mc', from_time, to_time)
        from_time = to_time

        average = statistics['average']
        if last_average > FALLING_EDGE_CURRENT_THRESHOLD > average:
            return to_time
        last_average = average

        if (datetime.now() - start_time).seconds > FALLING_EDGE_TIMEOUT > 0:
            print('Maximum time reached, not found falling edge')
            return None

def wait_for_gpi(recording: recording.Recording, device: arc.Arc) -> Optional[float]:
    ''' Wait for GPI change '''
    start_time = datetime.now()
    last_count = 0
    last_value = 0

    while True:
        time.sleep(GPI1_POLLING_TIME)

        count = recording.get_channel_data_count(device.id, 'gpi1')

        if count - last_count > 0:
            gpi1_data = recording.get_channel_data(device.id,
                                                   'gpi1',
                                                   last_count,
                                                   count - last_count
                                                   )
            last_count = count

            for data in gpi1_data['values']:
                if GPI1_EDGE == 'falling':
                    if data['value'] < last_value:
                        return data['timestamp']
                elif GPI1_EDGE == 'raising':
                    if data['value'] > last_value:
                        return data['timestamp']
                elif GPI1_EDGE == 'any':
                    if data['value'] != last_value:
                        return data['timestamp']
                else:
                    raise AppException(f'Unknown GPI edge type {GPI1_EDGE}')

                last_value = data['value']

        if (datetime.now() - start_time).seconds > GPI1_TIMEOUT > 0:
            print('Maximum time reached, not found falling edge')
            return None

def main() -> None:
    '''Connect to the Otii 3 application and run the measurement'''
    client = otii_client.OtiiClient()
    with client.connect() as otii:
        voltage_sweep(otii)

if __name__ == '__main__':
    main()
