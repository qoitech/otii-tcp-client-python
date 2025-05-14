#!/usr/bin/env python3
# pylint: disable=missing-module-docstring
import json
import os
import time
from enum import Enum
from otii_tcp_client import otii, otii_connection, otii_exception

class LicensingMode(Enum):
    # pylint: disable=missing-class-docstring
    AUTO = 'auto'
    MANUAL = 'manual'

class OtiiClientException(Exception):
    pass

DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 1905
DEFAULT_CONNECTION_TIMEOUT = 10
DEFAULT_LICENSING_MODE = LicensingMode.AUTO
DEFAULT_CREDENTIALS = './credentials.json'
DEFAULT_LICENSES = None

OTII_USERNAME = 'OTII_USERNAME'
OTII_PASSWORD = 'OTII_PASSWORD'

LICENSE_MAP = {
    'Admin':      [ 'Automation', 'Battery' ],
    'All':        [ 'Automation', 'Battery' ],
    'Automation': [ 'Automation' ],
    'Battery':    [ 'Battery' ],
    'Enterprise': [ 'Automation', 'Battery' ],
    'Log':        [],
    'Pro':        [],
    'Standard':   [],
}

class Connect(otii.Otii):
    # pylint: disable=missing-class-docstring
    def __init__(self,
                 host,
                 port,
                 try_for_seconds,
                 licensing,
                 credentials,
                 licenses,
                 ):
        self.auto_logged_in = False
        self.auto_reserved_licenses = []
        try_until = time.time() + try_for_seconds

        connection = otii_connection.OtiiConnection(host, port)
        connect_response = connection.connect_to_server(try_for_seconds = try_for_seconds)
        if connect_response['type'] == 'error':
            raise otii_exception.Otii_Exception(connect_response)
        super().__init__(connection)

        if licensing == LicensingMode.AUTO:
            if not self.is_logged_in():
                self._login(credentials)
                self.auto_logged_in = True

            wanted_licenses = [ 'Automation' ] if licenses is None else licenses
            self._reserve_licenses(wanted_licenses, try_until)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.disconnect()

    def _login(self, credentials_path):
        # pylint: disable=missing-function-docstring
        if os.path.isfile(credentials_path):
            with open(credentials_path, encoding='utf-8') as file:
                credentials = json.load(file)
                self.login(credentials['username'], credentials['password'])
        else:
            try:
                username = os.environ[OTII_USERNAME]
                password = os.environ[OTII_PASSWORD]
                self.login(username, password)
            except KeyError:
                pass

    def _reserve_licenses(self, licenses, try_until):
        # pylint: disable=missing-function-docstring
        all_licenses = self.get_licenses()
        for wanted_license in licenses:
            reserved = False
            while not reserved:
                try:
                    self._reserve_license(all_licenses, wanted_license)
                    reserved = True
                except OtiiClientException:
                    if time.time() > try_until:
                        print('Timed out')
                        raise
                    time.sleep(1.0)
                    all_licenses = self.get_licenses()

    def _reserve_license(self, all_licenses, wanted_license):
        reserved_by_me = [
            license
            for license in all_licenses
            if license['reserved_to'] != ''
                and license['available']
                and license['type'] in LICENSE_MAP
                and wanted_license in LICENSE_MAP[license['type']]
        ]
        available = [
            license
            for license in all_licenses
            if license['reserved_to'] == ''
                and license['available']
                and license['type'] in LICENSE_MAP
                and wanted_license in LICENSE_MAP[license['type']]
        ]
        if len(reserved_by_me) == 0:
            if len(available) > 0:
                license_id = available[0]['id']
                self.reserve_license(license_id)
                self.auto_reserved_licenses.append(license_id)
            else:
                raise OtiiClientException('Cannot reserve licenses')

    def disconnect(self):
        # pylint: disable=missing-function-docstring
        for license_id in self.auto_reserved_licenses:
            self.return_license(license_id)
        if self.auto_logged_in:
            self.logout()
        self.connection.close_connection()

class OtiiClient:
    """ Use this class to easily create a connected Otii object."""
    def __init__(self):
        self.otii = None

    def connect(self, *,
                host = DEFAULT_HOST,
                port = DEFAULT_PORT,
                try_for_seconds = DEFAULT_CONNECTION_TIMEOUT,
                licensing = DEFAULT_LICENSING_MODE,
                credentials = DEFAULT_CREDENTIALS,
                licenses = DEFAULT_LICENSES,
                ):
        """ Connect to Otii.

        Setting the licensing parameter to AUTO:

            * If not logged in, tries to log in using provided credentials
              and will logout when disconnected
            * If not all licenses specified in licenses already are reserved,
              it will try to automatically reserve the needed licenses,
              and then return them when disconnected

            Credentials will be read from the file credentials, or read from the
            environment variables OTII_USERNAME and OTII_PASSWORD.

        Args:
            host (str): Server address.
            port (int): Connection port number.
            try_for_seconds (int): Seconds to try to connect.
            licensing (str): 'auto' or 'manual'.
            credentials (str): Path to a file containing credentials.
            licenses (str[]): Array of license types ('Automation', 'Battery') needed.

        """
        self.otii = Connect(host, port, try_for_seconds, licensing, credentials, licenses)
        return self.otii

    def disconnect(self):
        """ Disconnect from Otii. """
        self.otii.disconnect()
