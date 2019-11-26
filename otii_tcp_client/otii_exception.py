#!/usr/bin/env python
class Otii_Exception(Exception):
    """ Class to define an Otii Exception object

    Attributes:
        type (str): Error code type.
        message (str): Human readable error message.

    """
    def __init__(self, response):
        """
        Args:
            response (dict): Dictionary with error message from server.

        """
        self.type = response["errorcode"]
        if self.type == "Command failure":
            self.message = response["cmd"] + " Error: \"" + self.type + "\"\tMessage: \"" + response["data"]["message"] + "\""
        elif self.type == "Command not valid for device type":
            self.message = response
        elif self.type == "Command timeout":
            self.message = response
        elif self.type == "Connection denied":
            self.message = response
        elif self.type == "Device not connected":
            self.message = response["cmd"] + " Error: \"" + self.type + "\"\tCannot find Arc with ID: \"" + response["data"]["device_id"] + "\""
        elif self.type == "Invalid command":
            self.message = response["cmd"] + " Error: \"" + self.type + "\""
        elif self.type == "Invalid key type":
            self.message = response["cmd"] + " Error: \"" + self.type + "\"\tInvalid key: \"" + response["data"]["key"] + "\"\texpected_type: \"" + response["data"]["expected_type"] + "\"\treceived_type: \"" + response["data"]["received_type"] + "\""
        elif self.type == "Invalid key value":
            self.message = response["cmd"] + " Error: \"" + self.type + "\"\tInvalid value: \"" + response["data"]["key"] + "\"\tvalue: \"" + str(response["data"]["value"]) + "\""
        elif self.type == "Missing key in request":
            if "cmd" in response:
                self.message = response["cmd"] + " Error: \"" + self.type + "\"\tMissing key: \"" + response["data"]["key"] + "\""
            else:
                self.message = "Error: \"" + self.type + "\"\tMissing key: \"" + response["data"]["key"] + "\""
        elif self.type == "Not able to parse request":
            self.message = response["cmd"] + " Error: \"" + self.type + "\"\tJSON parse error msg: \"" + response["data"]["parse_error"] + "\"\tmessage: \"" + str(response["data"]["data"]) + "\""
        elif self.type == "Request too large":
            self.message = response["cmd"] + " Error: \"" + self.type + "\"\tBytes received when aborted: \"" + response["data"]["read_size"] + "\"\tmax allowed bytes: \"" + str(response["data"]["max_size"]) + "\""
        # Temporary to handle unexpected messages when waiting for replay, to be updated when client is updated to handle asynchronous communication
        elif self.type == "Unexpected Transmission ID":
            self.message = "Unexpected transmission ID in received message"
        elif self.type == "Missing file name":
            self.message = "Save failed, no file name specified"
        else:
            self.message = "Undocumented error: " + str(response)
