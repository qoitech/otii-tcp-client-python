#!/usr/bin/env python3
'''
Otii 3 Battery emulator voltage sweep

To control the battery emulation from a script you need an Battery Toolbox
license in addition to the Automation Toolbox license

The battery profiles used in this script can be found at
    https://github.com/qoitech/otii-battery-profiles/tree/master/battery-profiles.

If you want the script to login and reserve a license automatically
add a configuration file called credentials.json in the current folder
using the following format:

    {
        "username": "YOUR USERNAME",
        "password": "YOUR PASSWORD"
    }

Alternatively you can set the environment variables OTII_USERNAME and OTII_PASSWORD.

'''
import time
import sys
from datetime import datetime
from otii_tcp_client import otii_client

TEST_SCHEME = [{
    'name': 'LiPo-ICP632136HPST-Renata-WiFi-20',
    'soc': [ 100, 50, 20 ],
}, {
    'name': 'LiPo-ICP632136HPST-Renata_WiFi-5',
    'soc': [ 100, 50, 20 ],
}, {
    'name': 'LiPo-ICP632136HPST-Renata-WiFi-(-10)',
    'soc': [ 100, 50, 20 ],
}]

class AppException(Exception):
    '''Application Exception'''

def voltage_sweep_with_uart(otii):
    ''' Voltage sweep '''
    # Connect to Otii Arc/Ace
    devices = otii.get_devices()
    if len(devices) == 0:
        print("No device connected!")
        sys.exit()
    device = devices[0]
    device.add_to_project()

    # Get battery profiles
    profiles = otii.get_battery_profiles()

    # Set up and Enable channels
    for channel in ["mc", "mv", "mp", "rx"]:
        device.enable_channel(channel, True)
    time.sleep(0.1)
    for channel in ["mc", "mv", "mp"]:
        device.set_channel_samplerate(channel, 50000)
    project = otii.get_active_project()
    series = 1
    parallel = 1
    battery_profile_id = get_battery_profile_id(profiles, TEST_SCHEME[0]['name'])
    soc = TEST_SCHEME[0]['soc']
    battery_emulator = device.set_supply_battery_emulator(battery_profile_id,
                                                          series = series,
                                                          parallel = parallel,
                                                          soc = soc,
                                                          #used_capacity = 2000 * 3.6,
                                                          #tracking = False,
                                                          )
    device.set_max_current(1)
    device.set_uart_baudrate(115200)
    device.set_exp_voltage(3.3)
    wait_after_sleep = 0.2

    device.set_main(True)

    for test in TEST_SCHEME:
        name = test['name']
        battery_profile_id = get_battery_profile_id(profiles, name)

        for soc in test['soc']:
            print(f"\nSetting battery profile {name}, soc = {soc}")
            battery_emulator.update_profile(battery_profile_id, mode = 'keep_soc')
            battery_emulator.set_soc(soc)
            project.start_recording()
            timestamp_message = wait_for_message(project,
                                                 device,
                                                 "Entering sleep mode",
                                                 maximum_time=30
                                                 )
            if timestamp_message is not None:
                print(f"Message found at timestamp: {timestamp_message}")
            recording = project.get_last_recording()
            recording.rename(f"SOC {soc}, Profile {name}")
            time.sleep(wait_after_sleep)

    device.set_main(False)
    print("\nStopping recording")
    project.stop_recording()

    print("Done!")

def get_battery_profile_id(profiles, name):
    ''' Get battery profile id '''
    profile_id = [
        profile['battery_profile_id']
        for profile in profiles
        if profile['name'] == name
    ]
    if len(profile_id) == 0:
        raise AppException(f'Battery profile for {name} not installed')
    return profile_id[0]

def wait_for_message(project, device, message, maximum_time = 0):
    ''' Wait for message on UART '''
    start_time = datetime.now()
    found_message = False
    timestamp_message = None
    # Get the data from the recording
    recording = project.get_last_recording()
    previous_samples = recording.get_channel_data_count(device.id, "rx")

    # Loop until message is found or time-out
    while not found_message:
        time.sleep(0.2)
        # Count the number of messages received
        samples = recording.get_channel_data_count(device.id, "rx")
        if samples > previous_samples:
            # Get the new messages
            rx_data = recording.get_channel_data(device.id,
                                                 "rx",
                                                 previous_samples,
                                                 samples-previous_samples)
            for data in rx_data["values"]:
                if message in data["value"]:
                    found_message = True
                    timestamp_message = data["timestamp"]
            previous_samples = samples
        if (datetime.now() - start_time).seconds > maximum_time > 0:
            print("Maximum time reached, not found message")
            break
    return timestamp_message

def main():
    '''Connect to the Otii 3 application and run the measurement'''
    client = otii_client.OtiiClient()
    with client.connect(licenses = [ 'Automation', 'Battery' ]) as otii:
        voltage_sweep_with_uart(otii)

if __name__ == '__main__':
    main()
