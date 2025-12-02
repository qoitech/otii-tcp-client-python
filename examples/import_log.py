#!/usr/bin/env python3
'''
Otii 3 Import log to an existing project

This imports a csv file with the following format:
    timestamp,message
    0.0,[Starting line - setting up]
    22.134,['Random Access Preamble'] ['L2 message'] ['UE --> SS']
    22.134,['Random Access Response'] ['L2 message'] ['UE <-- SS']
    22.254,['Description_none'] ['RRCConnectionRequest'] ['UE --> SS']
    ...0

If you want the script to login and reserve a license automatically
add a configuration file called credentials.json in the current folder
using the following format:

    {
        "username": "YOUR USERNAME",
        "password": "YOUR PASSWORD"
    }

'''
import csv
from otii_tcp_client import otii_client

LOG_NAME = 'Signaling'
LOG_FILE = 'signaling_trace.log'

def import_log(otii: otii_client.Connect) -> None:
    ''' Import text log '''
    project = otii.get_active_project()
    log_id = project.create_user_log(LOG_NAME)
    recording = project.get_last_recording()
    assert recording is not None

    with open(LOG_FILE, newline ='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            timestamp = float(row['timestamp'])
            message = row['message']
            recording.append_user_log(log_id, timestamp, message)

def main() -> None:
    '''Connect to the Otii 3 application and run the measurement'''
    client = otii_client.OtiiClient()
    with client.connect() as otii:
        import_log(otii)

if __name__ == '__main__':
    main()
