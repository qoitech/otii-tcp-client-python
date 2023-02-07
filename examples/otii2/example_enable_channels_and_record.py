#!/usr/bin/env python
import time
import sys, os
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))

from otii_tcp_client import otii_connection, otii_exception, otii
import example_config as cfg

def check_create_project(otii_object):
    proj = otii_object.get_active_project()
    if proj:
        print("Project already active")
    else:
        proj = otii_object.create_project()
        print("Project created")
    return proj

def enable_channels_record(otii_object, proj, my_arc):
    print(my_arc.name + " supply voltage: " + str(my_arc.get_main_voltage()))
    my_arc.enable_channel("mc", True)
    print(my_arc.name + " enabled channel Main Current")
    my_arc.enable_channel("mv", True)
    print(my_arc.name + " enabled channel Main Voltage")
    otii_object.set_all_main(True)
    print("Set all supply: on")
    proj.start_recording()
    print("New recording started with id: " + str(proj.get_last_recording().id))
    time.sleep(2)
    print("Recording ongoing: " + str(proj.get_last_recording().is_running()))
    time.sleep(2)
    proj.start_recording()
    print("New recording started with id: " + str(proj.get_last_recording().id))
    time.sleep(4)
    proj.stop_recording()
    print("Stopped recording with id: " + str(proj.get_last_recording().id))
    my_arc.enable_channel("mv", False)
    print(my_arc.name + " disabled channel Main Voltage")
    proj.start_recording()
    print("New recording started with id: " + str(proj.get_last_recording().id))
    time.sleep(4)
    proj.stop_recording()
    print("Stopped recording with id: " + str(proj.get_last_recording().id))
    otii_object.set_all_main(False)
    print("Set all supply: off")

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
    proj = check_create_project(otii_object)
    enable_channels_record(otii_object, proj, my_arc)
except otii_exception.Otii_Exception as e:
    print("Error message: " + e.message)

print("Done!")
