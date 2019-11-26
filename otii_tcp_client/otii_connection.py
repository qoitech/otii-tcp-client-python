#!/usr/bin/env python
import sys
import json
import socket

from otii_tcp_client import otii_exception

trans_id = 0

def get_new_trans_id():
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

    """
    def __init__(self, address, port, sock=None):
        """
        Args:
            address (str): Server IP address.
            port (int): Connection port number.
            sock (socket, optional): Communication socket.

        """
        self.host_address = address
        self.host_port = port
        self.recv_buffer = 4096

        if sock is None:
            self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def close_connection(self):
        """ Close connection to server.

        """
        self.sock.close()

    def connect_to_server(self):
        """ Connect to server.

        Returns:
            dict: Decoded JSON connection response.

        """
        try:
            self.sock.connect((self.host_address, self.host_port))
        except socket.error as e:
            self.sock.close()
            self.sock = None
            print(e)
            sys.exit(1)
        self.sock.setblocking(0)
        self.sock.settimeout(3)
        json_data = json.loads((self.sock.recv(self.recv_buffer)).decode("utf-8"))
        if json_data["type"] == "information":
            print("Info: " + json_data["info"])
        return json_data

    def receive_response(self, timeout_seconds, trans_id):
        """ Receive a JSON formated response from the server.

        Args:
            timeout_seconds (int): Transmission timeout (s).
            trans_id (int): ID of transmission.

        Returns:
            dict: Decoded JSON server response.

        """
        recv_msg = ""
        json_object = False
        self.sock.setblocking(0)
        self.sock.settimeout(timeout_seconds)
        while not json_object:
            recv_msg += (self.sock.recv(self.recv_buffer)).decode("utf-8")
            try:
                json_data = json.loads(recv_msg)
                if json_data["type"] == "information":
                    print("Info: " + json_data["info"])
                    recv_msg = ""
                elif json_data["type"] == "progress":
                    print("Progress on " + json_data["cmd"] + " is " + str(json_data["progress_value"]))
                    recv_msg = ""
                elif json_data["trans_id"] != trans_id:
                    recv_msg = ""
                else:
                    json_object = True
            except ValueError:
                continue
        return json_data

    def send_and_receive(self, request, timeout=3):
        """ Send request and receive response from server.

        Args:
            message (str): JSON encoded server request.
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

    def send_request(self, message):
        """ Send request to server.

        Args:
            message (str): JSON encoded server request.

        """
        totalsent = 0
        message = message + "\r\n"
        msg = message.encode("utf-8")
        while totalsent < len(msg):
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent
