#!/usr/bin/env python3
# pylint: disable=missing-module-docstring

class Measurement:
    """ Class to define an Otii Measurement object.

    Attributes:
        id (int): ID of the measurement.
        name (string): Name of the measurement.
        device_id: (string) Id of the measurement device
        channel_name: (string) Name of the measurement channel

    """
    id: int
    name: str
    device_id: str
    channel: str

    def __init__(self, measurement_dict: dict):
        """
        Args:
            measurement_dict (dict): Dictionary with measurement parameters.

        """
        self.id = measurement_dict["id"]
        self.name = measurement_dict["name"]
        self.device_id = measurement_dict["device_id"]
        self.channel = measurement_dict["channel"]
