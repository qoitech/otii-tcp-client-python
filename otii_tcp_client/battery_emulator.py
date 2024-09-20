#!/usr/bin/env python3
# pylint: disable=missing-module-docstring
from otii_tcp_client import otii_exception

class BatteryEmulator:
    """ Class to define a Battery Emulator object.

    Attributes:
        id (string): Id of the battery emulator.
        connection (:obj:OtiiConnection): Object to handle connection to the Otii server.

    """
    def __init__(self, battery_emulator_id, connection):
        """
        Args:
            battery_emulator_id (string): Id of the battery emulator.
            connection (:obj:OtiiConnection): Object to handle connection to the Otii server.

        """
        self.id = battery_emulator_id
        self.connection = connection

    def get_parallel(self):
        """ Get current number of emulated batteries in parallel.

        Returns:
            int: Number of batteries in parallel.

        """
        data = {"battery_emulator_id": self.id}
        request = {"type": "request", "cmd": "battery_emulator_get_parallel", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return response["data"]["value"]

    def get_series(self):
        """ Get current number of simulated batteries in series.

        Returns:
            int: Number of batteries in series.

        """
        data = {"battery_emulator_id": self.id}
        request = {"type": "request", "cmd": "battery_emulator_get_series", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return response["data"]["value"]

    def get_soc(self):
        """ Get State of Charge.

        Returns:
            float: State of charge in percent.

        """
        data = {"battery_emulator_id": self.id}
        request = {
            "type": "request",
            "cmd": "battery_emulator_get_soc",
            "data": data
        }
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return response["data"]["value"]

    def get_soc_tracking(self):
        """ Get current state of battery emulator State of Charge tracking.

        Returns:
            bool: True if State fo Charge tracking is enabled, False if disabled.

        """
        data = {"battery_emulator_id": self.id}
        request = {"type": "request", "cmd": "battery_emulator_get_soc_tracking", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return response["data"]["enabled"]

    def get_used_capacity(self):
        """ Get current battery emulator used capacity.

        Returns:
            float: Used capacity in coulomb (C).

        """
        data = {"battery_emulator_id": self.id}
        request = {"type": "request", "cmd": "battery_emulator_get_used_capacity", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return response["data"]["value"]

    def set_soc(self, value):
        """ Set State of Charge.

        Args:
            value (float): State of charge in percent

        """
        data = {
            "battery_emulator_id": self.id,
            "value": value
        }
        request = {
            "type": "request",
            "cmd": "battery_emulator_set_soc",
            "data": data
        }
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def set_soc_tracking(self, enable):
        """ Set State of Charge tracking.

        Args:
            enable (bool): True to enable State of Charge tracking, False to disable.

        """
        data = {"battery_emulator_id": self.id, "enable": enable}
        request = {"type": "request", "cmd": "battery_emulator_set_soc_tracking", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def set_used_capacity(self, value):
        """ Set used capacity.

        Args:
            value (float): Capacity used in coulombs (C), multiply mAh by 3.6 to get C.

        """
        data = {"battery_emulator_id": self.id, "value": value}
        request = {"type": "request", "cmd": "battery_emulator_set_used_capacity", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def update_profile(self, battery_profile_id, mode):
        """ Update battery profile.

        Args:
            battery_profile_id (string): Id of battery profile, as returned by otii.get_battery_profiles.
            mode (string): "keep_soc" or "reset"

        """
        data = {
            "battery_emulator_id": self.id,
            "battery_profile_id": battery_profile_id,
            "mode": mode
        }
        request = {
            "type": "request",
            "cmd": "battery_emulator_update_profile",
            "data": data,
        }
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
