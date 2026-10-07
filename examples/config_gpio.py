#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "otii-tcp-client",
# ]
# ///
from typing import Literal
from otii_tcp_client import otii_client
from otii_tcp_client.arc import Arc

GpioMode = Literal['in', 'out']

def configure_gpio(device: Arc, pin: int, mode: GpioMode) -> None:
    cfg = 0b001 if mode == 'out' else 0b100
    shift = (pin - 1) * 3
    cfg = cfg << shift
    print(cfg)
    device.set_property('gpiocfg', cfg)

def test_gpio(otii: otii_client.Connect) -> None:
    devices = otii.get_devices()
    assert len(devices) > 0
    device = devices[0]
    device.config_gpio(1, 'input')
    device.config_gpio(2, 'output')

def main() -> None:
    client = otii_client.OtiiClient()
    with client.connect() as otii:
        test_gpio(otii)

if __name__ == '__main__':
    main()

