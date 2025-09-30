#!/usr/bin/env python3
'''
Otii 3 AT command control of Nordic nRF91x1-DK
Example script how to test different power modes of LTE-M and NB-IoT
Designed to work with Nordic nRF9151-DK and nRF9161-DK

If you want the script to login and reserve a license automatically
add a configuration file called credentials.json in the current folder
using the following format:

    {
        "username": "YOUR USERNAME",
        "password": "YOUR PASSWORD"
    }

'''
import time
import os
from datetime import datetime
from otii_tcp_client import arc, otii_client, recording

MESSAGE_POLLING_TIME = 0.2
MEASUREMENT_TIMEOUT = 60*60*4 # 4 hours
MESSAGE_TIMEOUT = 5

PROJECT_FOLDER = os.path.join(os.getcwd(), 'nRF9151-DK_test')

class AppException(Exception):
    '''Application Exception'''

def error_response(recording: recording.Recording,
                   device: arc.Arc,
                   ok_text: str,
                   error_text: str) -> bool:
    ''' Wait for message on UART '''
    previous_samples = recording.get_channel_data_count(device.id, 'rx')
    error_message = False
    found_message = False
    start_time = datetime.now()

    # Loop until a message is found that is OK or error
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
                if error_text in data['value']:
                    print(f'Found error message: {data["value"]}')
                    error_message = True
                    found_message = True
                elif ok_text in data['value']:
                    print(f'Found OK message: {data["value"]}')
                    error_message = False
                    found_message = True
                else:
                    print(f'Found message: {data["value"]}')

            previous_samples = samples

        if (datetime.now() - start_time).seconds > MESSAGE_TIMEOUT > 0:
            print('Maximum time reached')
            error_message = True
            break

    return error_message

def reset_nrf6191_dk(recording: recording.Recording, device: arc.Arc) -> None:
    ''' Reset nRF91x1-dk '''
    print('Resetting nRF91x1-dk')
    device.set_main(False)
    device.enable_5v(0)
    time.sleep(1)
    device.enable_5v(5)
    time.sleep(1)
    device.set_main(True)
    error_response(recording, device, 'Ready', 'ERROR')
    print('nRF91x1-dk OK')

def send_commands(recording: recording.Recording, device: arc.Arc, commands: list[str]) -> None:
    ''' Send commands to device '''
    for command in commands:
        time.sleep(0.5)
        device.write_tx(command+'\r\n')
        if error_response(recording, device, 'OK', 'ERROR'):
            print(f'Error in command: {command}')
        else:
            print(f'Command sent successfully: {command}')

# pylint: disable=too-many-statements
def send_at_commands(otii: otii_client.Connect) -> None:
    '''
    Configure Otii Arc or Ace.
    Send AT commands to a connected DUT via UART TX and receive responses via UART RX.
    '''
    # Get a reference to a Arc or Ace device
    devices = otii.get_devices()
    if len(devices) == 0:
        raise AppException('No Arc or Ace connected!')
    device = devices[0]

    # Configure the device
    device.set_main_voltage(3.6)
    device.set_exp_voltage(1.8)
    device.set_max_current(1)
    device.enable_5v(5)

    # Enable the main current and UART channels
    device.enable_channel('mc', True)
    device.enable_channel('rx', True)
    device.set_uart_baudrate(115200)

    # Get the active project and save
    project = otii.get_active_project()
    project.save_as(PROJECT_FOLDER)

    # Start a recording and get reference to it
    project.start_recording()
    recording = project.get_last_recording()
    assert recording is not None

    # Turn on the main output of the selected device
    device.set_main(True)

    # Wait for Ready resonse
    error_response(recording, device, 'Ready', 'ERROR')

    # Send commands and wait for responses

    # General settings
    recording.rename('Initial settings')
    send_commands(recording, device, ['AT+CEREG=5','AT+CSCON=3'])
    send_commands(recording, device, ['AT+CPSMS=0','AT+CEDRXS=0'])

    # Test of LTE-M mode, no power save
    project.start_recording()
    recording = project.get_last_recording()
    assert recording is not None
    recording.rename('LTE-M, no power save')
    send_commands(recording, device, ['AT%XSYSTEMMODE=1,0,1,0','AT+CEDRXS=0','AT+CFUN=1'])
    time.sleep(MEASUREMENT_TIMEOUT)
    send_commands(recording, device, ['AT+CFUN=0'])
    time.sleep(1)
    reset_nrf6191_dk(recording, device)

    # Test of LTE-M mode, with eDRX power save
    project.start_recording()
    recording = project.get_last_recording()
    assert recording is not None
    recording.rename('LTE-M, eDRX timer 40.96s')
    send_commands(recording, device, ['AT%XSYSTEMMODE=1,0,1,0','AT+CEDRXS=2,4,"0011"','AT+CFUN=1'])
    time.sleep(MEASUREMENT_TIMEOUT)
    send_commands(recording, device, ['AT+CEDRXS=0','AT+CFUN=0'])
    time.sleep(1)
    reset_nrf6191_dk(recording, device)

    # Test of NB-IoT mode, no power save
    project.start_recording()
    recording = project.get_last_recording()
    assert recording is not None
    recording.rename('NB-IoT, no power save')
    send_commands(recording, device, ['AT%XSYSTEMMODE=0,1,1,0','AT+CFUN=1'])
    time.sleep(MEASUREMENT_TIMEOUT)
    send_commands(recording, device, ['AT+CFUN=0'])
    time.sleep(1)
    reset_nrf6191_dk(recording, device)

    # Test of NB-IoT mode, with eDRX power save
    project.start_recording()
    recording = project.get_last_recording()
    assert recording is not None
    recording.rename('NB-IoT, eDRX timer 40.96')
    send_commands(recording, device, ['AT%XSYSTEMMODE=0,1,1,0','AT+CEDRXS=2,5,"0011"','AT+CFUN=1'])
    time.sleep(MEASUREMENT_TIMEOUT)
    send_commands(recording, device, ['AT+CEDRXS=0','AT+CFUN=0'])
    time.sleep(1)
    reset_nrf6191_dk(recording, device)

    # Test of LTE-M mode, with PSM power save
    project.start_recording()
    recording = project.get_last_recording()
    assert recording is not None
    recording.rename('LTE-M, PSM T3412 timer 60min, T3324 timer 2min')
    send_commands(recording, device, ['AT%XSYSTEMMODE=1,0,1,0','AT+CPSMS=1,"","","00100001","00100010"','AT+CFUN=1'])
    time.sleep(MEASUREMENT_TIMEOUT)
    send_commands(recording, device, ['AT+CPSMS=0','AT+CFUN=0'])
    time.sleep(1)
    reset_nrf6191_dk(recording, device)

    # Test of NB-IoT mode, with PSM power save
    project.start_recording()
    recording = project.get_last_recording()
    assert recording is not None
    recording.rename('NB-IoT, PSM T3412 timer 60min, T3324 timer 2min')
    send_commands(recording, device, ['AT%XSYSTEMMODE=0,1,1,0','AT+CPSMS=1,"","","00100001","00100010"','AT+CFUN=1'])
    time.sleep(MEASUREMENT_TIMEOUT)
    send_commands(recording, device, ['AT+CPSMS=0','AT+CFUN=0'])
    time.sleep(1)
    reset_nrf6191_dk(recording, device)

    # Test of NB-IoT mode, with PSM and eDRX power save
    project.start_recording()
    recording = project.get_last_recording()
    assert recording is not None
    recording.rename('NB-IoT, PSM and eDRX')
    send_commands(recording, device, ['AT%XSYSTEMMODE=0,1,1,0','AT+CPSMS=1,"","","00100001","00100010"','AT+CEDRXS=2,5,"0011"','AT+CFUN=1'])
    time.sleep(MEASUREMENT_TIMEOUT)
    send_commands(recording, device, ['AT+CEDRXS=0','AT+CPSMS=0','AT+CFUN=0'])
    time.sleep(1)
    reset_nrf6191_dk(recording, device)

    # Test of LTE-M mode, with PSM and eDRX power save
    project.start_recording()
    recording = project.get_last_recording()
    assert recording is not None
    recording.rename('LTE-M, PSM and eDRX')
    send_commands(recording, device, ['AT%XSYSTEMMODE=1,0,1,0','AT+CPSMS=1,"","","00100001","00100010"','AT+CEDRXS=2,4,"0011"','AT+CFUN=1'])
    time.sleep(MEASUREMENT_TIMEOUT)
    send_commands(recording, device, ['AT+CEDRXS=0','AT+CPSMS=0','AT+CFUN=0'])
    time.sleep(1)

    project.stop_recording()
    device.set_main(False)
    device.enable_5v(0)
    project.save()

def main() -> None:
    '''Connect to the Otii 3 application and run the measurement'''
    client = otii_client.OtiiClient()
    with client.connect() as otii:
        send_at_commands(otii)

if __name__ == '__main__':
    main()
