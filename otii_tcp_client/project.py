#!/usr/bin/env python
from otii_tcp_client import otii_connection, otii_exception, recording

class Project:
    """ Class to define an Otii Project object.

    Attributes:
        id (int): ID of project.
        connection (:obj:OtiiConnection): Object to handle connection to the Otii server.

    """
    def __init__(self, id, connection):
        """
        Args:
            id (int): ID of project.
            filename (str): Name of project. Set when project is opened or saved.
            connection (:obj:OtiiConnection): Object to handle connection to the Otii server.

        """
        self.id = id
        self.filename = ""
        self.connection = connection

    def close(self, force=False ):
        """ Close the project.

        Args:
            force (bool, optional): True to force close, e.g. ignore unsaved data warning, False to not override warnings.

        """
        data = {"project_id": self.id, "force": force}
        request = {"type": "request", "cmd": "project_close", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        self.id = -1

    def crop_data(self, start, end):
        """ Crop all data before start and after end.

        Args:
            start (float): From sample at time start (s).
            end (float): To sample at time end (s).

        """
        data = {"project_id": self.id, "start": start, "end": end}
        request = {"type": "request", "cmd": "project_crop_data", "data": data}
        # Set timeout to None (blocking) as command can operate over large quantities of data to avoid timeout
        response = self.connection.send_and_receive(request, None)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def get_last_recording(self):
        """ Get the latest recording in the project.

        Returns:
            :obj:Recording: Recording Object.

        """
        data = {"project_id": self.id}
        request = {"type": "request", "cmd": "project_get_last_recording", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        if response["data"]["recording_id"] == -1:
            return None
        else:
            return recording.Recording(response["data"], self.connection)

    def get_recordings(self):
        """ List captured recordings.

        Returns:
            list: List of recording objects.

        """
        data = {"project_id": self.id}
        request = {"type": "request", "cmd": "project_get_recordings", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        recording_objects = []
        for recording_dict in response["data"]["recordings"]:
            recording_object = recording.Recording(recording_dict, self.connection)
            recording_objects.append(recording_object)
        return recording_objects

    def save(self, progress=False):
        """ Save the project.

        Args:
            progress (bool, optional): True to receive notifications about save progress, False to not receive any notifications.

        Returns:
            str: Name of saved file.

        """
        if self.filename == "":
            raise otii_exception.Otii_Exception({"errorcode": "Missing file name"})
        return self.save_as(self.filename, True, progress)

    def save_as(self, filename, force=False, progress=False):
        """ Save the project as.

        Args:
            filename (str): Name of project file.
            force (bool, optional): True to overwrite existing file, False to not overwrite.
            progress (bool, optional): True to receive notifications about save progress, False to not receive any notifications.

        Returns:
            str: Name of saved file.

        """
        data = {"project_id": self.id, "filename": filename, "force": force, "progress": progress}
        request = {"type": "request", "cmd": "project_save", "data": data}
        # Set timeout to None (blocking) as command can operate over large quantities of data to avoid timeout
        response = self.connection.send_and_receive(request, None)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        self.filename = response["data"]["filename"]
        return response["data"]["filename"]

    def start_recording(self):
        """ Start a new recording.

        """
        data = {"project_id": self.id}
        request = {"type": "request", "cmd": "project_start_recording", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def stop_recording(self):
        """ Stop the running recording.

        """
        data = {"project_id": self.id}
        request = {"type": "request", "cmd": "project_stop_recording", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
