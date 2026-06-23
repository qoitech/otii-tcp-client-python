# pylint: disable=missing-module-docstring
import json
import os
from enum import Enum
from typing_extensions import Self
from otii_tcp_client import otii, otii_connection, otii_exception

class LicensingMode(Enum):
    # pylint: disable=missing-class-docstring
    AUTO = 'auto'
    MANUAL = 'manual'

class OtiiClientException(Exception):
    # pylint: disable=missing-class-docstring
    pass

DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 1905
DEFAULT_CONNECTION_TIMEOUT = 10
DEFAULT_LICENSING_MODE = LicensingMode.AUTO
DEFAULT_CREDENTIALS = './credentials.json'
DEFAULT_LICENSES = None

OTII_USERNAME = 'OTII_USERNAME'
OTII_PASSWORD = 'OTII_PASSWORD'

LICENSE_MAP: dict[str, list[otii.LicenseType]] = {
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
    auto_logged_in: bool
    auto_reserved_licenses: list[int]
    setup_data: otii.SetupData | None

    def __init__(self,
                 host: str,
                 port: int,
                 try_for_seconds: int,
                 licensing: LicensingMode,
                 credentials_path: str,
                 licenses: list[otii.LicenseType] | None,
                 ) -> None:
        self.auto_logged_in = False
        self.auto_reserved_licenses = []
        self.setup_data = None

        connection = otii_connection.OtiiConnection(host, port)
        connect_response = connection.connect_to_server(try_for_seconds = try_for_seconds)
        if connect_response['type'] == 'error':
            raise otii_exception.Otii_Exception(connect_response)
        super().__init__(connection)

        if licensing == LicensingMode.AUTO:
            credentials = self._get_credentials(credentials_path)
            wanted_licenses: list[otii.LicenseType] = [ 'Automation' ] if licenses is None else licenses
            self.setup_data = self.setup(wanted_licenses, try_for_seconds, credentials)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: object, exc_value: object, exc_tb: object) -> None:
        self.disconnect()

    def _get_credentials(self, credentials_path: str) -> otii.Credentials | None:
        # pylint: disable=missing-function-docstring
        def creds(username: str | None, password: str | None) -> otii.Credentials | None:
            if username is not None and password is not None:
                credentials: otii.Credentials = {
                    'username': username,
                    'password': password,
                }
                return credentials
            return None

        if os.path.isfile(credentials_path):
            with open(credentials_path, encoding='utf-8') as file:
                credentials = json.load(file)
                return creds(credentials['username'], credentials['password'])
        elif OTII_USERNAME in os.environ and OTII_PASSWORD in os.environ:
            return creds(os.environ[OTII_USERNAME], os.environ[OTII_PASSWORD])

        return None

    def disconnect(self) -> None:
        # pylint: disable=missing-function-docstring
        if self.setup_data is not None:
            self.cleanup(self.setup_data)
        self.connection.close_connection()

class OtiiClient:
    """ Use this class to easily create a connected Otii object."""
    otii_client: Connect | None

    def __init__(self) -> None:
        self.otii_client = None

    def connect(self, *,
                host: str = DEFAULT_HOST,
                port: int = DEFAULT_PORT,
                try_for_seconds: int = DEFAULT_CONNECTION_TIMEOUT,
                licensing: LicensingMode = DEFAULT_LICENSING_MODE,
                credentials: str = DEFAULT_CREDENTIALS,
                licenses: list[otii.LicenseType] | None = DEFAULT_LICENSES,
                ) -> Connect:
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
            host (str, optional): Server address.
            port (int, optional): Connection port number.
            try_for_seconds (int, optional): Seconds to try to connect.
            licensing (str, optional): 'auto' or 'manual'.
            credentials (str, optional): Path to a file containing credentials.
            licenses (str[], optional): Array of license types ('Automation', 'Battery') needed.

        """
        self.otii_client = Connect(host, port, try_for_seconds, licensing, credentials, licenses)
        return self.otii_client

    def disconnect(self) -> None:
        """ Disconnect from Otii. """
        if self.otii_client is not None:
            self.otii_client.disconnect()
            self.otii_client = None
