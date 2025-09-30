#!/usr/bin/env python3
# pylint: disable=missing-module-docstring
from typing import Optional
from otii_tcp_client import otii_connection, otii_exception, recording

class Project:
    """ Class to define an Otii Project object.

    Attributes:
        id (int): ID of project.
        connection (:py:class:`.OtiiConnection`): Object to handle connection to the Otii server.

    """
    id: int
    connection: otii_connection.OtiiConnection

    def __init__(self, id: int, connection: otii_connection.OtiiConnection):
        """
        Args:
            id (int): ID of project.
            filename (str): Name of project. Set when project is opened or saved.
            connection (:py:class:`OtiiConnection`): Object to handle connection to the Otii server.

        """
        self.id = id
        self.filename = ""
        self.connection = connection

    def close(self, force: bool = False) -> None:
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

    def crop_data(self, start: float, end: float) -> None:
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

    def get_last_recording(self) -> Optional[recording.Recording]:
        """ Get the latest recording in the project.

        Returns:
            :py:class:`.Recording`

        """
        data = {"project_id": self.id}
        request = {"type": "request", "cmd": "project_get_last_recording", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        if response["data"]["recording_id"] == -1:
            return None

        return recording.Recording(response["data"], self.connection)

    def get_recordings(self) -> list[recording.Recording]:
        """ List captured recordings.

        Returns:
            :list[:py:class:`.Recording`]

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

    def save(self, progress: bool = False) -> str:
        """ Save the project.

        Args:
            progress (bool, optional): True to receive notifications about save progress, False to not receive any notifications.

        Returns:
            str: Name of saved file.

        """
        if self.filename == "":
            raise otii_exception.Otii_Exception({"errorcode": "Missing file name"})
        return self.save_as(self.filename, True, progress)

    def save_as(self, filename: str, force: bool = False, progress: bool = False) -> str:
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

    def start_recording(self) -> None:
        """ Start a new recording.

        """
        data = {"project_id": self.id}
        request = {"type": "request", "cmd": "project_start_recording", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def stop_recording(self) -> None:
        """ Stop the running recording.

        """
        data = {"project_id": self.id}
        request = {"type": "request", "cmd": "project_stop_recording", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def create_user_log(self, user_log_id: str) -> str:
        """ Create a user log.

        Args:
            user_log_id (str): Id of the user log to create

        Returns:
            str: Id of created user log

        """

        data = {"project_id": self.id, "id": user_log_id}
        request = {"type": "request", "cmd": "project_create_user_log", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

        return response["data"]["id"]
