#!/usr/bin/env python
import unicodedata
from otii_tcp_client import otii_connection, otii_exception
from dateutil.parser import isoparse

CHUNK_SIZE = 2000

def remove_control_characters(s):
    return "".join(ch for ch in s if unicodedata.category(ch)[0] != "C")

class Recording:
    """ Class to define an Otii Recording object.

    Attributes:
        id (int): ID of the recording.
        name (string): Name of the recording.
        start_time (datetime.datetime): Start of the recording or None if unsupported by TCP server.
        connection (:obj:OtiiConnection): Object to handle connection to the Otii server.

    """
    def __init__(self, recording_dict, connection):
        """
        Args:
            recording_dict (dict): Dictionary with recording parameters.
            connection (:obj:OtiiConnection): Object to handle connection to the Otii server.

        """
        self.id = recording_dict["recording_id"]
        self.name = recording_dict["name"]
        starttimestring = recording_dict.get("start-time")
        self.start_time = isoparse(starttimestring) if starttimestring else None
        self.connection = connection

    def delete(self):
        """ Delete the recording.

        """
        data = {"recording_id": self.id}
        request = {"type": "request", "cmd": "recording_delete", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        self.id = -1

    def downsample_channel(self, device_id, channel, factor):
        """ Downsample the recording on a channel.

        Args:
            device_id (str): ID of device capturing the data.
            channel (str): Name of the channel to downsample.
            factor (int): Factor to downsample with.

        """
        data = {"recording_id": self.id, "device_id": device_id, "channel": channel, "factor": factor}
        request = {"type": "request", "cmd": "recording_downsample_channel", "data": data}
        # Set timeout to None (blocking) as command can operate over large quantities of data to avoid timeout
        response = self.connection.send_and_receive(request, None)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def get_channel_data_count(self, device_id, channel):
        """ Get number of data entries in a channel for the recording.

        Args:
            device_id (str): ID of device to get data from.
            channel (str): Name of the channel to get data from.

        Returns:
            int: Number of data entries in the channel.

        """
        data = {"recording_id": self.id, "device_id": device_id, "channel": channel}
        request = {"type": "request", "cmd": "recording_get_channel_data_count", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return response["data"]["count"]

    def get_channel_data_index(self, device_id, channel, timestamp):
        """ Get the index of a data entry in a channel for a specific recording for a given timestamp.

        Args:
            device_id (str): ID of device to get data from.
            channel (str): Name of the channel to get data from.
            timestamp (float): Timestamp to get index of in seconds (s).

        Returns:
            int: Index of data entry at the timestamp.

        """
        data = {"device_id": device_id, "recording_id": self.id, "channel": channel, "timestamp": timestamp}
        request = {"type": "request", "cmd": "recording_get_channel_data_index", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return response["data"]["index"]

    def get_channel_data(self, device_id, channel, index, count, strip = True):
        """ Get data entries from a specified channel of a specific recording.

        Args:
            device_id (str): ID of device to get data from.
            channel (str): Name of the channel to get data from.
            index (int): Start position for fetching data, first value at index 0.
            count (int): Number of data entries to fetch.
            strip (bool): Strip control data from log channel, defaults to True.

        Returns:
            :obj:data:

        """
        if channel == "rx" or channel == "i1" or channel == "i2":
            request_data = {"device_id": device_id, "recording_id": self.id, "channel": channel, "index": index, "count":count}
            request = {"type": "request", "cmd": "recording_get_channel_data", "data": request_data}
            response = self.connection.send_and_receive(request, None)
            if response["type"] == "error":
                raise otii_exception.Otii_Exception(response)
            data = response["data"]
            if channel == "rx" and strip:
                data["values"] = [
                    {"value": remove_control_characters(value["value"]), "timestamp": value["timestamp"]}
                    for value in data["values"]
                ]
            return data
        else:
            request_data = {"device_id": device_id, "recording_id": self.id, "channel": channel}
            request = {"type": "request", "cmd": "recording_get_channel_data", "data": request_data}
            data = None
            while count > 0:
                chunk = min(count, CHUNK_SIZE)
                request["data"]["index"] = index
                request["data"]["count"] = chunk
                response = self.connection.send_and_receive(request, None)
                if response["type"] == "error":
                    raise otii_exception.Otii_Exception(response)
                if data == None:
                    data = response["data"]
                else:
                    data["values"].extend(response["data"]["values"])
                count -= chunk
                index += chunk
            return data


    def get_log_offset(self, device_id, channel):
        """ Get the offset of an log

        Args:
            device_id (str): ID of the capturing device. Set to None for imported logs.
            channel (str): The channel name. For imported logs, set to log_id returned by import_log.

        Returns:
            int: The offset of the log

        """
        data = {"recording_id": self.id, "channel": channel}
        if (device_id != None):
            data["device_id"] = device_id
        request = {"type": "request", "cmd": "recording_get_log_offset", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return response["data"]["offset"]

    def get_offset(self):
        """ Get the offset of the recording

        Returns:
            int: The offset of the recording

        """
        data = {"recording_id": self.id}
        request = {"type": "request", "cmd": "recording_get_offset", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return response["data"]["offset"]

    def import_log(self, filename, converter):
        """ Import log into recording.

        Args:
            filename (str): Path to log to import.
            converter (str): Name of the llog converter to use.

        Returns:
            log_id (str): Id of the log.

        """
        data = {"recording_id": self.id, "filename": filename, "converter": converter}
        request = {"type": "request", "cmd": "recording_import_log", "data": data}
        # Set timeout to None (blocking) as command can operate over large quantities of data to avoid timeout
        response = self.connection.send_and_receive(request, None)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return response["data"]["log_id"]

    def is_running(self):
        """ Check if recording is ongoing.

        Returns:
            bool: True is recording is ongoing, False if stopped.

        """
        data = {"recording_id": self.id}
        request = {"type": "request", "cmd": "recording_is_running", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return response["data"]["running"]

    def log(self, text, timestamp = 0):
        """ Write text to time synchronized log window.

            This function will add a timestamped text to a log. The first time it is called, it will create a new log.
            Note that a recording has to be running for this to produce any output.

        Args:
            name (str): Text to add to the log window.
            timestamp (int): Timestamp in milliseconds since 1970-01-01. If omitted the current time will be used.

        """
        data = {"recording_id": self.id, "text": text, "timestamp": timestamp}
        request = {"type": "request", "cmd": "recording_log", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def rename(self, name):
        """ Change the name of the recording.

        Args:
            name (str): New name of recording.

        """
        data = {"recording_id": self.id, "name": name}
        request = {"type": "request", "cmd": "recording_rename", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        self.name = name

    def set_log_offset(self, device_id, channel, offset):
        """ Set the offset of an log

        Args:
            device_id (str): ID of the capturing device. Set to None for imported logs.
            channel (str): The channel name. For imported logs, set to log_id returned by import_log.
            offset (int): The new offset to apply in microseconds.

        """
        data = {"recording_id": self.id, "channel": channel, "offset": offset}
        if (device_id != None):
            data["device_id"] = device_id
        request = {"type": "request", "cmd": "recording_set_log_offset", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def set_offset(self, offset):
        """ Set the offset of the recording

        Args:
            offset (int): The new offset to apply in microseconds.

        """
        data = {"recording_id": self.id, "offset": offset}
        request = {"type": "request", "cmd": "recording_set_offset", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
