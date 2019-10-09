#!/usr/bin/env python
from otii_tcp_client import otii_connection, otii_exception, project, arc

class Otii:
    """ Class to define an Otii object.

    Attributes:
        connection (:obj:OtiiConnection): Object to handle connection to the Otii server.

    """
    def __init__(self, connection):
        """
        Args:
            connection (:obj:OtiiConnection): Object to handle connection to the Otii server.

        """
        self.connection = connection

    def create_project(self):
        """ Create a new project.

        Returns:
            int: ID of created project.

        """
        request = {"type": "request", "cmd": "otii_create_project"}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return project.Project(response["data"]["project_id"], self.connection)

    def get_active_project(self):
        """ Returns the active project if there is one.

        Returns:
            :obj:Project: Project object.

        """
        request = {"type": "request", "cmd": "otii_get_active_project"}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        if response["data"]["project_id"] == -1:
            return None
        else:
            return project.Project(response["data"]["project_id"], self.connection)

    def get_device_id(self, device_name):
        """ Get device id from device name.

        Args:
            device_name (str): Name of device to get ID of.

        Returns:
            str: Device ID of requested device.

        """
        data = {"device_name": device_name}
        request = {"type": "request", "cmd": "otii_get_device_id", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return response["data"]["device_id"]

    def get_devices(self):
        """ Get a list of connected devices.

        Returns:
            list: List of Arc device objects.

        """
        request = {"type": "request", "cmd": "otii_get_devices"}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        elif not response["data"]:
            return []
        device_objects = []
        for device in response["data"]["devices"]:
            if device["type"] == "Arc":
                device_object = arc.Arc(device, self.connection)
                device_objects.append(device_object)
        return device_objects

    def open_project(self, filename, force = False, progress = False):
        """ Open an existing project.

        Args:
            filename (str): Name of project file.
            force (bool, optional): True to open even if unsaved data exists, False not to.
            progress (bool, optional): True to receive notifications about progress of opening file, False not to.

        Returns:
            int: ID of opened project.

        """
        data = {"filename": filename, "force": force, "progress": progress}
        request = {"type": "request", "cmd": "otii_open_project", "data": data}
        # Set timeout to None (blocking) as command can operate over large quantities of data to avoid timeout
        response = self.connection.send_and_receive(request, None)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        proj = project.Project(response["data"]["project_id"], self.connection)
        proj.filename = response["data"]["filename"]
        return proj

    def set_all_main(self, enable):
        """ Turn on or off the main power on all connected devices.

        Args:
            enable (bool): True to turn on main power, False to turn off.

        """
        data = {"enable": enable}
        request = {"type": "request", "cmd": "otii_set_all_main", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def shutdown(self):
        """ Shutdown Otii

        """
        request = {"type": "request", "cmd": "otii_shutdown"}
        try:
            response = self.connection.send_and_receive(request)
            if response["type"] == "error":
                raise otii_exception.Otii_Exception(response)
        except otii_connection.DisconnectedException:
            pass
