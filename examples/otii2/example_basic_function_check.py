#!/usr/bin/env python
import time
import sys, os
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))

from otii_tcp_client import otii_connection, otii_exception, otii

import example_config as cfg

def basic_function_check(otii_object, my_arc):
    proj = otii_object.get_active_project()
    if proj:
        print("Project already active")
    else:
        proj = otii_object.create_project()
        print("Project created")
    devices = otii_object.get_devices()
    for device in devices:
        print("Found Arc device: " + device.name + " - " + device.id)
        print(device.name + " is connected: " + str(device.is_connected()))

    print("Start calibration of " + my_arc.type + ": " + my_arc.name)
    my_arc.calibrate()
    print("Calibration finished")
    time.sleep(1)
    print(my_arc.name + " turn supply: on")
    my_arc.set_main(True)
    time.sleep(4)
    print("Turn all supply: off")
    otii_object.set_all_main(False)

connection = otii_connection.OtiiConnection(cfg.HOST["IP"], cfg.HOST["PORT"])
connect_response = connection.connect_to_server()
if connect_response["type"] == "error":
    print("Exit! Error code: " + connect_response["errorcode"] + ", Description: " + connect_response["data"]["message"])
    sys.exit()
try:
    otii_object = otii.Otii(connection)
    devices = otii_object.get_devices()
    if len(devices) == 0:
        print("No Arc connected!")
        sys.exit()
    my_arc = devices[0]
    basic_function_check(otii_object, my_arc)
except otii_exception.Otii_Exception as e:
    print("Error message: " + e.message)

print("Done!")
