"""
Example to draw constant current from device.
Intention is to measure I-V curve of photovoltaic cells.

Based on Energy_harvesting_2.lua provided by Qoitech
"""
import sys, os
import time
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))

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

def setup_channels(otii_object, proj, my_arc):
    print(my_arc.name + " supply voltage: " + str(my_arc.get_main_voltage()))
    my_arc.enable_channel("mc", True)
    print(my_arc.name + " enabled channel Main Current")
    my_arc.enable_channel("mv", True)
    print(my_arc.name + " enabled channel Main Voltage")

    my_arc.set_power_regulation("current")
    my_arc.set_main_current(0)

def run_measurement(otii_object, proj, my_arc):
    print("Starting measurement.")
    print("Stop measurement by KeyboardInterrupt, ctrl+c")
    otii_object.set_all_main(True)
    proj.start_recording()
    time.sleep(0.1)
    for current in range(20000):
        my_arc.set_main_current(-1*current*1e-6)
        time.sleep(0.1)

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
    setup_channels(otii_object, proj, my_arc)
    run_measurement(otii_object, proj, my_arc)
except otii_exception.Otii_Exception as e:
    print("Error message: " + e.message)
finally:
    proj.stop_recording()
    otii_object.set_all_main(False)
    my_arc.set_power_regulation("voltage")

print("Done!")