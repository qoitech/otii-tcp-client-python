#!/usr/bin/env python
import time
import sys, os
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))

from otii_tcp_client import otii_connection, otii_exception, otii
import example_config as cfg

def check_create_project(otii_object):
    try:
        proj = otii_object.get_active_project()
        if proj:
            print("Project already active")
        else:
            proj = otii_object.create_project()
            print("Project with id \"" + str(proj.id) + "\" created")
        proj.close(True)
        print("Project closed")
    except otii_exception.Otii_Exception as otii_except:
        print(otii_except.type)
        print(otii_except.message)

connection = otii_connection.OtiiConnection(cfg.HOST["IP"], cfg.HOST["PORT"])
connect_response = connection.connect_to_server()
if connect_response["type"] == "error":
    print("Exit! Error code: " + connect_response["errorcode"] + ", Description: " + connect_response["data"]["message"])
    sys.exit()
try:
    otii_object = otii.Otii(connection)
    check_create_project(otii_object)
except otii_exception.Otii_Exception as e:
    print("Error message: " + e.message)

print("Done!")
