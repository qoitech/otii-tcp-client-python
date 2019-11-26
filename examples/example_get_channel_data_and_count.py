#!/usr/bin/env python
#encoding: utf-8
import sys, os
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))

from otii_tcp_client import otii_connection, otii_exception, otii
import example_config as cfg

def get_channel_data_count(recording, device_id, channel):
    samples = recording.get_channel_data_count(device_id, channel)
    print("No. samples: " + str(samples))

def get_channel_data(recording, device_id, channel, index, count):
    data = recording.get_channel_data(device_id, channel, index, count)
    print("No. samples: " + str(len(data["values"])))
    if len(data) > 0:
        print("First data item of " + str(len(data["values"])) + " is: " + str(data["timestamp"]) + " s, " + str(data["values"][0]) + " A")

#
# Need an active project with some recorded data
#

"""
    Channel Description	    Unit
    mc      Main Current    A
    mv      Main Voltage    V
    me      Main Energy     Wh
    ac      ADC Current     A
    av      ADC Voltage     V
    ae      ADC Energy      Wh
    sp      Sense+ Voltage  V
    sn      Sense- Voltage  V
    vb      VBUS            V
    vj      DC Jack         V
    tp      Temperature     °C
    rx      UART logs       text
"""
# Channel to get data from (name according to above list)
channel = "mc"
# Index of first value to fetch
index = 2
# No. values to fetch
count = 2

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
    proj = otii_object.get_active_project()
    recording = proj.get_last_recording()
    if recording:
        get_channel_data_count(recording, my_arc.id, channel)
        get_channel_data(recording, my_arc.id, channel, index, count)
    else:
        print("No recording in project")
except otii_exception.Otii_Exception as e:
    print("Error message: " + e.message)

print("Done!")
