#!/usr/bin/env python3
# pylint: disable=missing-module-docstring
import unicodedata
from dateutil.parser import isoparse
from otii_tcp_client import otii_exception

CHUNK_SIZE = 40000

def remove_control_characters(s):
    # pylint: disable=missing-function-docstring
    return "".join(ch for ch in s if unicodedata.category(ch)[0] != "C")

class Recording:
    """ Class to define an Otii Recording object.

    Attributes:
        id (int): ID of the recording.
        name (string): Name of the recording.
        start_time (datetime.datetime): Start of the recording or None if unsupported by TCP server.
        measurements (dict): Measurements included in this recording
        connection (:py:class:`.OtiiConnection`): Object to handle connection to the Otii server.

    """
    def __init__(self, recording_dict, connection):
        """
        Args:
            recording_dict (dict): Dictionary with recording parameters.
            connection (:py:class:`.OtiiConnection`): Object to handle connection to the Otii server.

        """
        self.id = recording_dict["recording_id"]
        self.name = recording_dict["name"]
        starttimestring = recording_dict.get("start-time")
        self.start_time = isoparse(starttimestring) if starttimestring else None
        self.measurements = recording_dict.get("measurements")
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
        """ Downsample all recordings on a channel.

        .. table:: Channels available for downsampling
            :widths: auto

            ======= ============== ====
            Channel Description    Unit
            ======= ============== ====
            **mc**  Main Current   A
            **mv**  Main Voltage   V
            **me**  Main Energy    J
            **ac**  ADC Current    A
            **av**  ADC Voltage    V
            **ae**  ADC Energy     J
            **sp**  Sense+ Voltage V
            **sn**  Sense- Voltage V
            **vb**  VBUS           V
            **vj**  DC Jack        V
            **tp**  Temperature    °C
            ======= ============== ====

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

        For available channels see :py:meth:`.Arc.enable_channel`

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
        """ Get the index of a data entry in a channel for a given timestamp for the recording.

        For available channels see :py:meth:`.Arc.enable_channel`

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

        For available channels see :py:meth:`.Arc.enable_channel`

        Args:
            device_id (str): ID of device to get data from.
            channel (str): Name of the channel to get data from.
            index (int): Start position for fetching data, first value at index 0.
            count (int): Number of data entries to fetch.
            strip (bool): Strip control data from log channel, defaults to True.

        Returns:
            Data for analog channels::

                {
                    # Data type is analog
                    "data_type": 'analog',
                    # Timestamp in seconds of first sample
                    "timestamp": 3.250
                    # Interval in seconds between each sample
                    "interval": 0.00025,
                    # Array of samples
                    "values": [0.002453, 0.002675, 0.001945, 0.002444]
                }

            Data for digital channels::

                {
                    # Data type is digital
                    "data_type": "digital",
                    # Array of values
                    "values": [{
                        # Timestamp in seconds
                        "timestamp": 0.001,
                        # Digital value
                        "value": true
                    }, {
                        "timestamp": 2.132,
                        "value": false
                    }]
                }

            Data for the rx channel::

                {
                    # Data type is log
                    "data_type": "log",
                    "values": [{
                        # Timestamp in seconds
                        "timestamp": 0.001,
                        # Log text
                        "value": "Device booting"
                    }, {
                        "timsestamp": 2.132,
                        "value": "Going to sleep"
                    }]
                }

        """
        if channel in [ "rx", "i1", "i2" ]:
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
            if data is None:
                data = response["data"]
            else:
                data["values"].extend(response["data"]["values"])
            count -= chunk
            index += chunk
        return data

    def get_channel_info(self, device_id, channel):
        """ Get information for a channel in the recording.

        For available channels see :py:meth:`.Arc.enable_channel`

        Args:
            device_id (str): ID of device to get info from.
            channel (str): Name of the channel to get info from.

        Returns:
            Recording info::

                {
                    # The offset of the recording in seconds.
                    "offset": 0.0,
                    # The start of the recording in seconds.
                    "from": 0.0
                    # The end of the recording in seconds.
                    "to": 5.34,
                    # The sample rate of the recording.
                    "sample_rate": 4000
                }

        Examples:
            `basic_measurement.py <https://github.com/qoitech/otii-tcp-client-python/blob/master/examples/basic_measurement.py>`__

        """
        data = {"recording_id": self.id, "device_id": device_id, "channel": channel}
        request = {"type": "request", "cmd": "recording_get_channel_info", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return response["data"]

    def get_channel_statistics(self, device_id, channel, from_time, to_time):
        """ Get statistics for a channel for a given time interval in the recording.

        For available channels see :py:meth:`.Arc.enable_channel`

        Args:
            device_id (str): ID of device to get data from.
            channel (str): Name of the channel to get data from.
            from_time (float): Selection start in seconds.
            to_time (float): Selection end in seconds.

        Returns:
            Recording statistics::

                {
                    # The minimum value in the selected interval.
                    "min": -0,00565853156149387,
                    # The maximum value in the selected interval.
                    "max": 0,476982802152634,
                    # The average value in the selected interval.
                    "average": 0,0561770809812117,
                    # The energy consumed in the interval (if applicable).
                    "energy": 0,000290418408670424
                }

        """
        data = {"recording_id": self.id, "device_id": device_id, "channel": channel, "from": from_time, "to": to_time}
        request = {"type": "request", "cmd": "recording_get_channel_statistics", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return response["data"]

    def get_log_offset(self, device_id, channel):
        # pylint: disable=missing-class-docstring
        data = {"recording_id": self.id, "channel": channel}
        if device_id is not None:
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
        # pylint: disable=missing-class-docstring
        data = {"recording_id": self.id, "filename": filename, "converter": converter}
        request = {"type": "request", "cmd": "recording_import_log", "data": data}
        # Set timeout to None (blocking) as command can operate over large quantities of data to avoid timeout
        response = self.connection.send_and_receive(request, None)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return response["data"]["log_id"]

    def is_running(self):
        # pylint: disable=missing-class-docstring
        data = {"recording_id": self.id}
        request = {"type": "request", "cmd": "recording_is_running", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return response["data"]["running"]

    def log(self, text, timestamp = 0):
        # pylint: disable=missing-class-docstring
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
        # pylint: disable=missing-class-docstring
        data = {"recording_id": self.id, "channel": channel, "offset": offset}
        if device_id is not None:
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
