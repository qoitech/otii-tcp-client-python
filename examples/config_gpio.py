#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "otii-tcp-client",
# ]
# ///
from otii_tcp_client import otii_client

def test_gpio(otii: otii_client.Connect) -> None:
    devices = otii.get_devices()
    assert len(devices) > 0
    device = devices[0]
    device.config_gpio(1, 'input')
    device.config_gpio(2, 'output')
    device.enable_channel("gpio1", True)
    device.enable_channel("gpio2", True)

def main() -> None:
    client = otii_client.OtiiClient()
    with client.connect() as otii:
        test_gpio(otii)

if __name__ == '__main__':
    main()
