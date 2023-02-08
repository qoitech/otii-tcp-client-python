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
from otii_tcp_client import otii_connection, otii as otii_application

# The default hostname and port of the Otii 3 application
HOSTNAME = '127.0.0.1'
PORT = 1905

CREDENTIALS = './credentials.json'
ABBREVATIONS = {
    "Automation": "AT",
    "Battery": "BT",
    "BatteryValidation": "BVT",
}

def list_and_reserve_licenses():
    '''
    This example shows you how to login,
    list licenses, reserve and return a license,
    and how to logout.
    '''
    if not os.path.isfile(CREDENTIALS):
        raise Exception('You need to create a credentials.json file')

    # Connect to the Otii 3 application
    connection = otii_connection.OtiiConnection(HOSTNAME, PORT)
    connect_response = connection.connect_to_server(try_for_seconds=10)
    if connect_response['type'] == 'error':
        raise Exception(f'Exit! Error code: {connect_response["errorcode"]}, '
                        f'Description: {connect_response["payload"]["message"]}')
    otii = otii_application.Otii(connection)

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

if __name__ == '__main__':
    list_and_reserve_licenses()
