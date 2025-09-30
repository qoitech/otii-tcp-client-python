#!/usr/bin/env python3
'''
Otii 3 Compared with saved

To use this script you need to add a configuration file called
credentials.json in the current folder using the following format:

    {
        "username": "YOUR USERNAME",
        "password": "YOUR PASSWORD",
        "license_id": "YOUR LICENSE ID"
    }

'''
import json
import os
import time
from otii_tcp_client import otii_client

CREDENTIALS = './credentials.json'
ABBREVATIONS = {
    "Automation": "AT",
    "Battery": "BT",
    "BatteryValidation": "BVT",
}

class AppException(Exception):
    '''Application Exception'''

def list_and_reserve_licenses(otii: otii_client.Connect) -> None:
    '''
    This example shows you how to login,
    list licenses, reserve and return a license,
    and how to logout.
    '''
    if not os.path.isfile(CREDENTIALS):
        raise AppException('You need to create a credentials.json file')

    # Read the credentials
    with open(CREDENTIALS, encoding='utf-8') as file:
        credentials = json.load(file)

    # Login to the Otii license server
    otii.login(credentials['username'], credentials['password'])

    # List all available licenses
    otii_licenses = otii.get_licenses()
    print('  Id Type         Available Reserved to     Hostname')
    for otii_license in otii_licenses:
        available = "Yes" if otii_license["available"] else "No "
        print(f'{otii_license["id"]:4d} {otii_license["type"]:12} {available}       '
              f'{otii_license["reserved_to"]:15} {otii_license["hostname"]}')
        for addon in otii_license['addons']:
            print(f'     - {addon["id"]}')

    # Reserve a license that includes access to Automation Toolbox
    otii.reserve_license(credentials['license_id'])

    # Do your stuff
    time.sleep(3)

    # Return the license and logout
    otii.return_license(credentials['license_id'])
    otii.logout()

def main() -> None:
    '''Connect to the Otii 3 application and run the measurement'''
    client = otii_client.OtiiClient()
    with client.connect(licensing = otii_client.LicensingMode.MANUAL) as otii:
        list_and_reserve_licenses(otii)

if __name__ == '__main__':
    main()
