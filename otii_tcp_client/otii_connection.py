#!/usr/bin/env python3
# pylint: disable=missing-module-docstring
import datetime
import json
import socket
import time
from typing import Optional

class DisconnectedException(Exception):
    # pylint: disable=missing-class-docstring
    pass

trans_id: int = 0

def get_new_trans_id() -> str:
    # pylint: disable=missing-function-docstring
    global trans_id
    trans_id += 1
    return str(trans_id)

class OtiiConnection:
    """ Class to define the server connection handler

    Attributes:
        host_address (str): Server IP address.
        host_port (int): Connection port number.
        recv_buffer (int): Size of receive buffer.
        sock (socket): Communication socket.
        recv_msg (str): Buffer

    """
    host_address: str
    host_port: int
    recv_buffer: int
    sock: Optional[socket.socket]
    recv_msg: str = ""

    def __init__(self, address: str, port: int):
        """
        Args:
            address (str): Server IP address.
            port (int): Connection port number.

        """
        self.host_address = address
        self.host_port = port
        self.recv_buffer = 128 * 1024

    def close_connection(self) -> None:
        """ Close connection to server.

        """
        if self.sock is not None:
            self.sock.close()

    def connect_to_server(self, *, try_for_seconds: int = 0) -> dict:
        """ Connect to server.

        Args:
            try_for_seconds (int): Seconds to try to connect.

        Returns:
            Server information::

                {
                    "type": "information",
                    "info": "connected",
                    "data": {
                        "otii_version": "3.5.5",
                        "protocol_version": "0.1",
                        "server": "otii-server"
                    }
                }

        """
        start_time = datetime.datetime.now().timestamp()
        connected = False
        while not connected:
            try:
                self.sock = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.host_address, self.host_port))
                connected = True
            except socket.error:
                if self.sock is not None:
                    self.sock.close()
                    self.sock = None
                elapsed_time = datetime.datetime.now().timestamp() - start_time
                if elapsed_time > try_for_seconds:
                    raise
                time.sleep(0.5)

        return self.receive_response(3, "")

    def receive_response(self, timeout_seconds: Optional[float], trans_id: str) -> dict:
        """ Receive a JSON formated response from the server.

        Args:
            timeout_seconds (int): Transmission timeout (s).
            trans_id (str): ID of transmission.

        Returns:
            dict: Decoded JSON server response.

        """
        if self.sock is None:
            raise Exception("Not connected")

        response = None
        self.sock.settimeout(timeout_seconds)
        while not response:
            try:
                recv_data = self.sock.recv(self.recv_buffer)
                if len(recv_data) == 0:
                    raise DisconnectedException()
            except ConnectionResetError:
                raise DisconnectedException()
            self.recv_msg += recv_data.decode("utf-8")
            items = self.recv_msg.split("\r\n")
            self.recv_msg = items.pop()
            for item in items:
                json_data = json.loads(item)
                if json_data["type"] == "information":
                    response = json_data
                elif json_data["type"] == "progress":
                    pass
                elif json_data["trans_id"] != trans_id:
                    raise Exception("Transaction id mismatch")
                else:
                    response = json_data
        return response

    def send(self, request: str) -> None:
        """ Send request without waiting for response.

        Args:
            request (dict): Server request.

        """
        json_msg = json.dumps(request)
        self.send_request(json_msg)

    def send_and_receive(self, request: dict, timeout: Optional[float] = 3) -> dict:
        """ Send request and receive response from server.

        Args:
            request (dict): Server request.
            timeout (int, optional): Transmission timeout (s), default 3s.

        Returns:
            dict: Decoded JSON server response.

        """
        request["trans_id"] = get_new_trans_id()
        json_msg = json.dumps(request)
        self.send_request(json_msg)
        data = self.receive_response(timeout, request["trans_id"])
        if data["trans_id"] != request["trans_id"]:
            data["error"] = "Unexpected Transmission ID"
        return data

    def send_request(self, message: str) -> None:
        """ Send request to server.

        Args:
            message (str): Server request.

        """
        if self.sock is None:
            raise Exception("Not connected")

        totalsent = 0
        message = message + "\r\n"
        msg = message.encode("utf-8")
        while totalsent < len(msg):
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent
