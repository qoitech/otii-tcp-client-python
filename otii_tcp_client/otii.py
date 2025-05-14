#!/usr/bin/env python3
# pylint: disable=missing-module-docstring
from otii_tcp_client import otii_connection, otii_exception, project, arc

class Otii:
    """ Class to define an Otii object.

    Attributes:
        connection (:obj:OtiiConnection): Object to handle connection to the Otii server.

    """
    def __init__(self, connection=None):
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
        return project.Project(response["data"]["project_id"], self.connection)

    def get_battery_profile_info(self, battery_profile_id):
        """ Returns informatiion about a battery profile.

        Args:
            battery_profile_id (string): Battery profile id.
        """
        data = {"battery_profile_id": battery_profile_id}
        request = {"type": "request", "cmd": "otii_get_battery_profile_info", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return response["data"]

    def get_battery_profiles(self):
        """ Returns a list of available battery profiles.

        Returns:
            list: List of battery profile objects

        """
        request = {"type": "request", "cmd": "otii_get_battery_profiles"}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return response["data"]["battery_profiles"]

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

    def get_devices(self, timeout = 10, devicefilter = None):
        """ Get a list of connected devices.

        Args:
            timeout (int, optional): Timeout in seconds to wait for avaliable devices.
            devicefilter (tuple, optional): Override default device filter

        Returns:
            list: List of Arc device objects.

        """
        data = {"timeout": timeout}
        request = {"type": "request", "cmd": "otii_get_devices", "data": data}
        response = self.connection.send_and_receive(request, timeout + 3)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        if not response["data"]:
            return []
        device_objects = []
        for device in response["data"]["devices"]:
            devfilter = ("Arc", "Ace", "Simulator") if devicefilter is None else devicefilter
            if device["type"] in devfilter:
                device_object = arc.Arc(device, self.connection)
                device_objects.append(device_object)
        return device_objects

    def get_licenses(self):
        """ Return a list of all licenses for logged in user

        Returns:
            list: List of licenses

            .. code-block:: json

                [{
                    "id":1234,
                    "type":"Pro",
                    "available":true,
                    "reserved_to":"",
                    "hostname":"",
                    "addons":[{
                        "id":"Automation",
                        "attributes":null
                    }]
                }]

        """
        request = {"type": "request", "cmd": "otii_get_licenses"}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return response["data"]["licenses"]

    def has_license(self, license_type):
        """ Check if user has a reserved license

            Args:
                license_type: Type of licenses

            Returns:
                bool: True if license is reserved, otherwise False
        """
        data = {"license_type": license_type}
        request = {"type": "request", "cmd": "otii_has_license", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return response["data"]["has_license"]

    def is_logged_in(self):
        """ Check if user is logged in

            Returns:
                bool: True if user is logged in, otherwise False
        """
        request = {"type": "request", "cmd": "otii_is_logged_in"}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return response["data"]["logged_in"]

    def login(self, username, password):
        """ Login user

            Args:
                username: Name of Otii user
                password: Password of Otii user
        """
        data = {"username": username, "password": password}
        request = {"type": "request", "cmd": "otii_login", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def logout(self):
        """ Logout user
        """
        request = {"type": "request", "cmd": "otii_logout"}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def open_project(self, filename, force = False, progress = False):
        """ Open an existing project.

        Args:
            filename (str): Name of project file.
            force (bool, optional): True to open even if unsaved data exists, False not to.
            progress (bool, optional): True to receive notifications about progress of opening file,
            False not to.

        Returns:
            int: ID of opened project.

        """
        data = {"filename": filename, "force": force, "progress": progress}
        request = {"type": "request", "cmd": "otii_open_project", "data": data}
        # Set timeout to None (blocking) as command can operate
        # over large quantities of data to avoid timeout
        response = self.connection.send_and_receive(request, None)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        proj = project.Project(response["data"]["project_id"], self.connection)
        proj.filename = response["data"]["filename"]
        return proj

    def reserve_license(self, license_id):
        """ Reserve license

        Args:
            license_id (int): The license id to reserve.
        """
        data = {"license_id": license_id}
        request = {"type": "request", "cmd": "otii_reserve_license", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def return_license(self, license_id):
        """ Return license

        Args:
            license_id (int): The license id to return.
        """
        data = {"license_id": license_id}
        request = {"type": "request", "cmd": "otii_return_license", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

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
