#!/usr/bin/env python3
'''
Running Otii 3 tests in Jenkins

This is an example on how to create a test case for Otii measurements
that creates a JUnit compatible test result that is suitable for CI
integration tests in environments like Jenkins.

The test will connect to Otii and flash the latest firmware of the DUT before executing
the tests.

If you want the script to login and reserve a license automatically
add a configuration file called credentials.json in the current folder
using the following format:

    {
        "username": "YOUR USERNAME",
        "password": "YOUR PASSWORD"
    }

You also need to install the following dependencies:
    python3 -m pip install unittest-xml-reporting

'''
import subprocess
import time
import unittest
from otii_tcp_client import otii_client

TEST_DEVICE_NAME = 'Ace'
FIRMWARE_FLASH_CMD = 'cd firmware; make build; make flash'
MEASUREMENT_DURATION = 40 # Seconds

START_OF_CYCLE_MESSAGE = 'Connecting...'
MIN_ENERGY = 2 # Joule
MAX_ENERGY = 4 # Joule

class AppException(Exception):
    '''Application Exception'''

class OtiiTest(unittest.TestCase):
    '''Otii 3 test case example'''
    otii = None
    device = None

    @classmethod
    def setUpClass(cls):
        # Connect to Otii
        client = otii_client.OtiiClient()
        OtiiTest.otii = client.connect()

        # Configure device
        devices = [
            device
            for device in OtiiTest.otii.get_devices()
            if device.name == TEST_DEVICE_NAME
        ]
        if len(devices) != 1:
            raise AppException(f'Cannot find one device named "{TEST_DEVICE_NAME}"')
        device = devices[0]
        OtiiTest.device = devices[0]

        device.set_main_voltage(4.0)
        device.set_exp_voltage(3.3)
        device.set_max_current(0.5)
        device.set_uart_baudrate(115200)

        # Update FW

        # Make sure the main output of the Otii is turned off.
        device.set_main(False)

        # The switch board is powered by the Otii +5V pin.
        device.enable_5v(True)

        # Enable the USB, and give the DUT time to startup.
        device.set_gpo(1, True)
        time.sleep(3.0)

        try:
            # Upload new firmware
            result = subprocess.call(FIRMWARE_FLASH_CMD, shell=True)
            if result != 0:
                raise AppException('Failed to upload new firmware')
            time.sleep(3.0)
        except Exception as error:
            raise error
        finally:
            # Disable the USB, and turn off the main power
            device.set_gpo(1, False)
            time.sleep(1.0)

    @classmethod
    def tearDownClass(cls):
        if OtiiTest.otii is not None:
            OtiiTest.otii.disconnect()

    def test_energy_consumption_using_rx(self):
        '''Test the energy consumption of the latest firmware'''
        otii = OtiiTest.otii
        device = OtiiTest.device

        project = otii.get_active_project()

        device.enable_channel('mc', True)
        device.enable_channel('rx', True)

        project.start_recording()
        device.set_main(True)
        time.sleep(MEASUREMENT_DURATION)
        device.set_main(False)
        project.stop_recording()

        recording = project.get_last_recording()
        index = 0
        count = recording.get_channel_data_count(device.id, 'rx')
        data = recording.get_channel_data(device.id, 'rx', index, count)
        values = data['values']
        timestamps = [value['timestamp'] for value in values if value['value'] == START_OF_CYCLE_MESSAGE]
        self.assertGreaterEqual(len(timestamps), 2, f'Need at least two "{START_OF_CYCLE_MESSAGE}" timestamps')

        statistics = recording.get_channel_statistics(device.id, 'mc', timestamps[0], timestamps[1])
        self.assertLess(statistics['energy'], MAX_ENERGY, 'One interval consumes to much energy')
        self.assertGreater(statistics['energy'], MIN_ENERGY, 'One interval consumes to little energy, is everything up and running?')

    def test_energy_consumption_using_gpi(self):
        '''Test the energy consumption of the latest firmware'''
        otii = OtiiTest.otii
        device = OtiiTest.device

        project = otii.get_active_project()

        device.enable_channel('mc', True)
        device.enable_channel('i1', True)

        project.start_recording()
        device.set_main(True)
        time.sleep(MEASUREMENT_DURATION)
        device.set_main(False)
        project.stop_recording()

        recording = project.get_last_recording()
        index = 0
        count = recording.get_channel_data_count(device.id, 'i1')
        gpi1_data = recording.get_channel_data(device.id, 'i1', index, count)['values']
        timestamps = [gpi1_value['timestamp'] for gpi1_value in gpi1_data]
        self.assertGreaterEqual(len(timestamps), 4, 'Need at least four GPI1 pulses')

        statistics = recording.get_channel_statistics(device.id, 'mc', timestamps[0], timestamps[2])
        self.assertLess(statistics['energy'], MAX_ENERGY, 'One interval consumes to much energy')
        self.assertGreater(statistics['energy'], MIN_ENERGY, 'One interval consumes to little energy, is everything up and running?')

if __name__ == '__main__':
    import xmlrunner
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'))
