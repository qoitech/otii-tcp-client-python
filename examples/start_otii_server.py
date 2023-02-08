#!/usr/bin/env python3
'''
Otii 3 Start otii_server
'''
import subprocess
from basic_measurement import basic_measurement

# Remember to add the directory of the otii_server to the path.
OTII_SERVER = 'otii_server'

def start_otii_server():
    '''
    This example shows how to start otii_server from Python
    before running a script
    '''
    cmd = f'{OTII_SERVER}'

    with subprocess.Popen(cmd, stdout=subprocess.PIPE) as server:
        def print_output():
            print(server.stdout.read1().decode('utf-8'))

        print_output()

        try:
            basic_measurement()
        except Exception as error:
            print(f'Error: {error}')

        print_output()

        server.kill()
        server.wait(5)

if __name__ == '__main__':
    start_otii_server()
