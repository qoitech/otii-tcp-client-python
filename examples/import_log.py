#!/usr/bin/env python3
'''
Otii 3 Import log to an existing project

This imports a text file with the following format:
    timestamp;Log message

If you want the script to login and reserve a license automatically
add a configuration file called credentials.json in the current folder
using the following format:

    {
        "username": "YOUR USERNAME",
        "password": "YOUR PASSWORD"
    }

'''
import unicodedata
from otii_tcp_client import otii_client

LOG_ID = 'Signaling'
LOG_FILE = 'signaling_trace.log'

def import_log(otii: otii_client.Connect) -> None:
    ''' Import text log '''
    project = otii.get_active_project()
    imported_log_id = project.create_user_log(LOG_ID)
    recording = project.get_last_recording()
    assert recording is not None

    with open(LOG_FILE, mode ='r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            timestamp = float(line.split(';')[0])
            columns = line.split(';')[1]
            message = ''.join(col for col in columns if unicodedata.category(col)[0] != 'C')
            recording.append_user_log(imported_log_id, timestamp, message)

def main() -> None:
    '''Connect to the Otii 3 application and run the measurement'''
    client = otii_client.OtiiClient()
    with client.connect() as otii:
        import_log(otii)

if __name__ == '__main__':
    main()
