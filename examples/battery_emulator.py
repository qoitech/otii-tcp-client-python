#!/usr/bin/env python3
'''
Otii 3 Battery Emulator

To control the battery emulation from a script you need an Battery Toolbox
license in addition to the Automation Toolbox license

If you want the script to login and reserve a license autmatically
Add a configuration file called credentials.json in the current folder
using the following format:

    {
        "username": "YOUR USERNAME",
        "password": "YOUR PASSWORD",
        "license_ids": ["YOUR AUTOMATION LICENSE", "YOUR BATTERY LICENSE"]
    }

'''
import json
import os
import time
from otii_tcp_client import otii as otii_client

CREDENTIALS = '~/credentials.json'
MODEL = 'LM17500'

def run_emulator():
    # Connect to the Otii 3 application
    otii = otii_client.Otii()
    otii.connect()

    # Optional login to the license server and reserve a license
    if os.path.isfile(CREDENTIALS):
        with open(CREDENTIALS, encoding='utf-8') as file:
            credentials = json.load(file)
            otii.login(credentials['username'], credentials['password'])
            for license in credentials['license_ids']:
                otii.reserve_license(license)

    # Get a reference to a Arc or Ace device and add it to the project
    devices = otii.get_devices()
    if len(devices) == 0:
        raise Exception('No Arc or Ace connected!')
    device = devices[0]
    device.add_to_project()

    # Make sure device is in power box mode
    supply_mode = device.get_supply_mode()
    print(f'Device is in {supply_mode} mode')

    # Get battery profiles
    profiles = otii.get_battery_profiles()
    for profile in profiles:
        print(profile)

    # Select a profile
    lm_profiles = [
        profile
        for profile in profiles
        if 'model' in profile and profile['model'] == MODEL
    ]
    if len(lm_profiles) == 0:
        raise Exception(f'Cannot find a battery profile for {MODEL}')
    profile = lm_profiles[0]
    battery_profile_id = profile['battery_profile_id']

    # Select the profile for emulation
    series = 2
    parallel = 3
    battery_emulator = device.set_supply_battery_emulator(battery_profile_id,
                                                          series = series,
                                                          parallel = parallel,
                                                          soc = 50,
                                                          #used_capacity = 2000 * 3.6,
                                                          #tracking = False,
                                                          )

    # Do something
    time.sleep(1.0)

    # Configure profile
    #battery_emulator.set_soc(70)
    #battery_emulator.set_used_capacity(500)
    #battery_emulator.set_soc_tracking(False)

    # Show all data
    info = otii.get_battery_profile_info(battery_profile_id)
    print(f'Profile id:    {battery_profile_id}')
    print(f'Capacity:      {info['battery']['capacity'] * parallel} mAh')
    print(f'Parallel:      {battery_emulator.get_parallel()}')
    print(f'Series:        {battery_emulator.get_series()}')
    print(f'SOC:           {battery_emulator.get_soc()}%')
    print(f'Tracking:      {battery_emulator.get_soc_tracking()}')
    print(f'Used capacity: {battery_emulator.get_used_capacity() / 3.6} mAh')

    # Restore power box mode
    # device.set_supply_power_box()

    # Disconnect from the Otii 3 application
    otii.close()

if __name__ == '__main__':
    run_emulator()
