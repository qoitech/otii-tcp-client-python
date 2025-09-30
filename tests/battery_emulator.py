#!/usr/bin/env python3
'''
Otii 3 Battery Emulator

To control the battery emulation from a script you need an Battery Toolbox
license in addition to the Automation Toolbox license

If you want the script to login and reserve a license autmatically
Add a configuration file called credentials.json in the current folder
using the following format:

    {
        "username": "YOUR USERNAME",
        "password": "YOUR PASSWORD"
    }

'''
import unittest
from otii_tcp_client import arc, otii_client, otii_exception

MODEL = 'LM17500'
MODEL2 = 'CR2450'

class TestBatteryEmulator(unittest.TestCase):
    otii: otii_client.Connect
    devices: list[arc.Arc]
    device: arc.Arc
    battery_profiles: dict

    @classmethod
    def setUpClass(cls) -> None:
        # Connect to the Otii 3 application
        client = otii_client.OtiiClient()
        cls.otii = client.connect(licenses = [ 'Automation', 'Battery' ])

        # Get a reference to a Arc or Ace device
        cls.devices = cls.otii.get_devices()
        if len(cls.devices) == 0:
            raise Exception('No Arc or Ace connected!')
        cls.device = cls.devices[0]
        cls.device.add_to_project()

        # Get battery profiles
        profiles = cls.otii.get_battery_profiles()

        cls.battery_profiles = {}
        for profile in profiles:
            if 'model' in profile:
                cls.battery_profiles[profile['model']] = profile

    @classmethod
    def tearDownClass(cls) -> None:
        # Disconnect from the Otii 3 application
        cls.otii.disconnect()

    def test_set_supply_to_battery_emulator_used_capacity(self) -> None:
        device = TestBatteryEmulator.device
        battery_profiles = TestBatteryEmulator.battery_profiles

        # Reset power supply
        device.set_supply_power_box()

        # Select a profile
        profile = battery_profiles[MODEL]
        battery_profile_id = profile['battery_profile_id']

        # Select the profile for emulation
        battery_emulator = device.set_supply_battery_emulator(battery_profile_id,
                                                              series = 2,
                                                              parallel = 3,
                                                              used_capacity = 0.123,
                                                              soc_tracking = False
                                                              )

        device.set_main(True)

        # Verify
        supply_mode = device.get_supply_mode()
        self.assertEqual(supply_mode, 'battery-emulator')

        series = battery_emulator.get_series()
        self.assertEqual(series, 2)

        parallel = battery_emulator.get_parallel()
        self.assertEqual(parallel, 3)

        used_capacity = battery_emulator.get_used_capacity()
        self.assertEqual(used_capacity, 0.123)

        soc = battery_emulator.get_soc()
        self.assertGreater(soc, 0)
        self.assertLess(soc, 100)

        soc_tracking = battery_emulator.get_soc_tracking()
        self.assertFalse(soc_tracking)

    def test_set_supply_to_battery_emulator_soc(self) -> None:
        device = TestBatteryEmulator.device
        battery_profiles = TestBatteryEmulator.battery_profiles

        # Reset power supply
        device.set_supply_power_box()

        # Select a profile
        profile = battery_profiles[MODEL]
        battery_profile_id = profile['battery_profile_id']

        # Select the profile for emulation
        battery_emulator = device.set_supply_battery_emulator(battery_profile_id,
                                                              series = 3,
                                                              parallel = 2,
                                                              soc = 23,
                                                              soc_tracking = True
                                                              )

        device.set_main(True)

        # Verify
        supply_mode = device.get_supply_mode()
        self.assertEqual(supply_mode, 'battery-emulator')

        series = battery_emulator.get_series()
        self.assertEqual(series, 3)

        parallel = battery_emulator.get_parallel()
        self.assertEqual(parallel, 2)

        #used_capacity = battery_emulator.get_used_capacity()
        #self.assertEqual(used_capacity, 0.123)

        soc = battery_emulator.get_soc()
        self.assertEqual(soc, 23)

        soc_tracking = battery_emulator.get_soc_tracking()
        self.assertTrue(soc_tracking)

    def test_set_supply_with_default_values(self) -> None:
        device = TestBatteryEmulator.device
        battery_profiles = TestBatteryEmulator.battery_profiles

        # Reset power supply
        device.set_supply_power_box()

        # Select a profile
        profile = battery_profiles[MODEL]
        battery_profile_id = profile['battery_profile_id']

        # Select the profile for emulation using default values and soc
        battery_emulator = device.set_supply_battery_emulator(battery_profile_id,)

        # Verify
        series = battery_emulator.get_series()
        self.assertEqual(series, 1)

        parallel = battery_emulator.get_parallel()
        self.assertEqual(parallel, 1)

        used_capacity = battery_emulator.get_used_capacity()
        self.assertAlmostEqual(used_capacity, 0)

        soc = battery_emulator.get_soc()
        self.assertEqual(soc, 100)

        soc_tracking = battery_emulator.get_soc_tracking()
        self.assertTrue(soc_tracking)

    def test_setting_both_soc_and_used_capacity_should_fail(self) -> None:
        device = TestBatteryEmulator.device
        battery_profiles = TestBatteryEmulator.battery_profiles

        # Reset power supply
        device.set_supply_power_box()

        # Select the profile for emulation
        profile = battery_profiles[MODEL]
        battery_profile_id = profile['battery_profile_id']

        with self.assertRaises(otii_exception.Otii_Exception) as cm:
            device.set_supply_battery_emulator(battery_profile_id,
                                               soc = 50,
                                               used_capacity = 333,
                                               )
        self.assertEqual(cm.exception.type, 'Invalid key value')

    def test_setting_supply_should_open_relay(self) -> None:
        device = TestBatteryEmulator.device
        battery_profiles = TestBatteryEmulator.battery_profiles

        # Reset power supply
        device.set_supply_power_box()
        self.assertEqual(device.get_supply_mode(), 'power-box')

        # Select the profile for emulation
        profile = battery_profiles[MODEL]
        battery_profile_id = profile['battery_profile_id']

        device.set_main(True)
        device.set_supply_battery_emulator(battery_profile_id,
                                           used_capacity = 333,
                                           )
        self.assertFalse(device.get_main())

    def test_update_battery_profile_keeping_soc(self) -> None:
        device = TestBatteryEmulator.device
        battery_profiles = TestBatteryEmulator.battery_profiles

        # Select the profile for emulation
        profile = battery_profiles[MODEL]
        battery_profile_id = profile['battery_profile_id']

        battery_emulator = device.set_supply_battery_emulator(battery_profile_id,
                                                              soc = 33,
                                                              )

        last_soc = battery_emulator.get_soc()

        # Update the profile for the active battery emulator
        profile = battery_profiles[MODEL2]
        battery_profile_id = profile['battery_profile_id']

        battery_emulator.update_profile(battery_profile_id, 'keep_soc')

        # Verify
        supply_mode = device.get_supply_mode()
        self.assertEqual(supply_mode, 'battery-emulator')

        soc = battery_emulator.get_soc()
        self.assertAlmostEqual(soc, last_soc, 3)

    def test_update_battery_profile_resetting(self) -> None:
        device = TestBatteryEmulator.device
        battery_profiles = TestBatteryEmulator.battery_profiles

        # Select the profile for emulation
        profile = battery_profiles[MODEL]
        battery_profile_id = profile['battery_profile_id']

        battery_emulator = device.set_supply_battery_emulator(battery_profile_id,
                                                              soc = 33,
                                                              )

        soc = battery_emulator.get_soc()
        self.assertAlmostEqual(soc, 33)

        # Update the profile for the active battery emulator
        profile = battery_profiles[MODEL2]
        battery_profile_id = profile['battery_profile_id']

        battery_emulator.update_profile(battery_profile_id, 'reset')

        # Verify
        supply_mode = device.get_supply_mode()
        self.assertEqual(supply_mode, 'battery-emulator')

        soc = battery_emulator.get_soc()
        self.assertAlmostEqual(soc, 100)

    def test_change_used_capacity(self) -> None:
        device = TestBatteryEmulator.device
        battery_profiles = TestBatteryEmulator.battery_profiles

        # Reset power supply
        device.set_supply_power_box()
        self.assertEqual(device.get_supply_mode(), 'power-box')

        # Select the profile for emulation
        profile = battery_profiles[MODEL]
        battery_profile_id = profile['battery_profile_id']

        battery_emulator = device.set_supply_battery_emulator(battery_profile_id)

        # Change series
        battery_emulator.set_used_capacity(52)
        self.assertAlmostEqual(battery_emulator.get_used_capacity(), 52)

    def test_change_soc(self) -> None:
        device = TestBatteryEmulator.device
        battery_profiles = TestBatteryEmulator.battery_profiles

        # Reset power supply
        device.set_supply_power_box()
        self.assertEqual(device.get_supply_mode(), 'power-box')

        # Select the profile for emulation
        profile = battery_profiles[MODEL]
        battery_profile_id = profile['battery_profile_id']

        battery_emulator = device.set_supply_battery_emulator(battery_profile_id)

        # Change series
        battery_emulator.set_soc(17)
        self.assertAlmostEqual(battery_emulator.get_soc(), 17)

if __name__ == '__main__':
    unittest.main()
