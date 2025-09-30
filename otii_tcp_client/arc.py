#!/usr/bin/env python3
#coding: utf-8
# pylint: disable=missing-module-docstring
from typing import Any, Literal, Optional, Union
from otii_tcp_client import otii_connection, otii_exception, battery_emulator

DeviceType = Literal["Arc", "Ace", "Simulator"]
PowerRegulation = Literal["voltage", "current", "inline", "off"]
Range = Literal["low", "high"]

class Arc:
    """ Class to define an Arc or Ace device.
        Includes operations that can be run on the Arc or Ace.

    Attributes:
        type (str): Device type, "Arc" for Arc devices.
        id (str): ID of the Arc device.
        name (str): Name of the Arc device.
        connection (:py:class:`.OtiiConnection`): Object to handle connection to the Otii server.

    """
    type: DeviceType
    id: str
    name: str
    connection: otii_connection.OtiiConnection

    def __init__(self, device_dict: dict, connection: otii_connection.OtiiConnection) -> None:
        """
        Args:
            device_dict (dict): Dictionary with Arc parameters.
            connection (:py:class:`.OtiiConnection`): Object to handle connection to the Otii server.

        """
        self.type = device_dict["type"]
        self.id = device_dict["device_id"]
        self.name = device_dict["name"]
        self.connection = connection

    def add_to_project(self) -> None:
        """ Add device to current project.

        """
        data = {
            "device_id": self.id,
        }
        request = {
            "type": "request",
            "cmd": "arc_add_to_project",
            "data": data,
        }
        response = self.connection.send_and_receive(request, 10)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def calibrate(self) -> None:
        """ Perform internal calibration of an Arc device.

        """
        data = {"device_id": self.id}
        request = {"type": "request", "cmd": "arc_calibrate", "data": data}
        response = self.connection.send_and_receive(request, 10)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def enable_5v(self, enable: Union[bool, int]) -> None:
        """ Enable or disable 5V pin.

        Args:
            enable (bool): True to enable 5V, False to disable.

        """
        data = {"device_id": self.id, "enable": enable}
        request = {"type": "request", "cmd": "arc_enable_5v", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def enable_battery_profiling(self, enable: bool) -> None:
        # pylint: disable=missing-function-docstring
        data = {"device_id": self.id, "enable": enable}
        request = {"type": "request", "cmd": "arc_enable_battery_profiling", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def enable_channel(self, channel: str, enable: bool) -> None:
        """ Enable or disable measurement channel.

        .. table:: Available channels

            ======= ============== =======
            Channel Description    Unit
            ======= ============== =======
            **mc**  Main Current   A
            **mp**  Main Power     W
            **mv**  Main Voltage   V
            **ac**  ADC Current    A
            **ac**  ADC Power      W
            **av**  ADC Voltage    V
            **sp**  Sense+ Voltage V
            **sn**  Sense- Voltage V
            **vb**  VBUS           V
            **vj**  DC Jack        V
            **tp**  Temperature    °C
            **rx**  UART logs      text
            **i1**  GPI1           Digital
            **i2**  GPI2           Digital
            ======= ============== =======

        Args:
            channel (str): Name of the channel to enable or disable.
            enable (bool): True to enable channel, False to disable.

        """
        data = {"device_id": self.id, "channel": channel, "enable": enable}
        request = {"type": "request", "cmd": "arc_enable_channel", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def enable_exp_port(self, enable: bool) -> None:
        """ Enable expansion port.

        Args:
            enable (bool): True to enable expansion port, False to disable.

        """
        data = {"device_id": self.id, "enable": enable}
        request = {"type": "request", "cmd": "arc_enable_exp_port", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def enable_legacy_sink(self, enable: bool) -> None:
        """ Enable or disable legacy sink mode.

        Args:
            enable (bool): True to enable legacy sink mode, False to disable.

        """
        data = {"device_id": self.id, "enable": enable}
        request = {"type": "request", "cmd": "arc_enable_legacy_sink", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def enable_uart(self, enable: bool) -> None:
        """ Enable UART.

        Args:
            enable (bool): True to enable UART, False to disable.

        """
        data = {"device_id": self.id, "enable": enable}
        request = {"type": "request", "cmd": "arc_enable_uart", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def get_4wire(self) -> str:
        """ Get the 4-wire measurement state.

        Returns:
            str: The current state, "cal_invalid", "disabled", "inactive" or "active".

        """
        data = {"device_id": self.id}
        request = {"type": "request", "cmd": "arc_get_4wire", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return response["data"]["value"]

    def get_adc_resistor(self) -> float:
        """ Get adc resistor value.

        Returns:
            float: ADC resistor value (Ohm).

        """
        data = {"device_id": self.id}
        request = {"type": "request", "cmd": "arc_get_adc_resistor", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return response["data"]["value"]

    def get_channel_samplerate(self, channel: str) -> int:
        """ Get channel sample rate.

        For available channels see :py:meth:`.Arc.enable_channel`

        Args:
            channel (str): Name of the channel to get the sample rate for.

        Returns:
            int: Sample rate for channel

        """
        data = {"device_id": self.id, "channel": channel}
        request = {"type": "request", "cmd": "arc_get_channel_samplerate", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return response["data"]["value"]

    def get_exp_voltage(self) -> float:
        """ Get the voltage of the expansion port.

        Returns:
            float: Voltage value on the expansion port (V).

        """
        data = {"device_id": self.id}
        request = {"type": "request", "cmd": "arc_get_exp_voltage", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return response["data"]["value"]

    def get_gpi(self, pin: int) -> bool:
        """ Get the state of one of the GPI pins.

        Args:
            pin (int): ID of the GPI pin to get state of, 1 or 2.

        Returns:
            bool: State of the GPI pin.

        """
        data = {"device_id": self.id, "pin": pin}
        request = {"type": "request", "cmd": "arc_get_gpi", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return response["data"]["value"]

    def get_main(self) -> bool:
        """ Get the state of the main power.

        Returns:
            bool: State of the main power.

        """
        data = {"device_id": self.id}
        request = {"type": "request", "cmd": "arc_get_main", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return response["data"]["value"]

    def get_main_voltage(self) -> float:
        """ Get main voltage value.

        Returns:
            float: Main voltage value (V).

        """
        data = {"device_id": self.id}
        request = {"type": "request", "cmd": "arc_get_main_voltage", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return response["data"]["value"]

    def get_max_current(self) -> float:
        """ Get the max allowed current.

        Returns:
            float: Value max current is set to (A).

        """
        data = {"device_id": self.id}
        request = {"type": "request", "cmd": "arc_get_max_current", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return response["data"]["value"]

    def get_range(self) -> str:
        """ Get the current measurement range on the main output.

        Returns:
            str: Current measurement range mode on main, "low" or "high".

        """
        data = {"device_id": self.id}
        request = {"type": "request", "cmd": "arc_get_range", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return response["data"]["range"]

    def get_rx(self) -> bool:
        """ The RX pin can be used as a GPI when the UART is disabled.

        Returns:
            bool: State of the RX pin.

        """
        data = {"device_id": self.id}
        request = {"type": "request", "cmd": "arc_get_rx", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return response["data"]["value"]

    def get_src_cur_limit_enabled(self) -> bool:
        """ Get current state of voltage source current limiting.

        Returns:
            bool: True if set to constant current, false if set to cut-off.

        """
        data = {"device_id": self.id}
        request = {"type": "request", "cmd": "arc_get_src_cur_limit_enabled", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return response["data"]["enabled"]

    def get_supply_mode(self) -> str:
        """ Get current supply mode

        Returns:
            string: "power-box" or "battery-emulator"

        """
        data = {"device_id": self.id}
        request = {
            "type": "request",
            "cmd": "arc_get_supply_mode",
            "data": data,
        }
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return response["data"]["supply_mode"]

    def get_uart_baudrate(self) -> int:
        """ Get the UART baud rate.

        Returns:
            int: Value UART baud rate is set to.

        """
        data = {"device_id": self.id}
        request = {"type": "request", "cmd": "arc_get_uart_baudrate", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return response["data"]["value"]

    def get_value(self, channel: str) -> float:
        """ Get value from specified channel.

        This is not available for the rx channel.

        For available channels see :py:meth:`.Arc.enable_channel`

        Args:
            channel (str): Name of the channel to get value from.

        Returns:
            float: Present value in the channel (A/V/°C/Digital).

        """
        data = {"device_id": self.id, "channel": channel}
        request = {"type": "request", "cmd": "arc_get_value", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return response["data"]["value"]

    def get_version(self) -> dict:
        """ Get hardware and firmware versions of device.

        Returns:
            dict: Dictionary including keys hw_version (str) and fw_version (str).

        """
        data = {"device_id": self.id}
        request = {"type": "request", "cmd": "arc_get_version", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return response["data"]

    def is_connected(self) -> bool:
        """ Check if a device is connected.

        Returns:
            bool: True if device is connected, False otherwise.

        """
        data = {"device_id": self.id}
        request = {"type": "request", "cmd": "arc_is_connected", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return response["data"]["connected"]

    def set_4wire(self, enable: bool) -> None:
        """ Enable/disable 4-wire measurements using Sense+/-.

        Args:
            enable (bool): True to enable 4-wire, false to disable

        """
        data = {"device_id": self.id, "enable": enable}
        request = {"type": "request", "cmd": "arc_set_4wire", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def set_adc_resistor(self, value: float) -> None:
        """ Set the value of the shunt resistor for the ADC.

        Args:
            value (float): Value to set ADC resistor to, value should be between 0.001-22 (Ohm).

        """
        data = {"device_id": self.id, "value": value}
        request = {"type": "request", "cmd": "arc_set_adc_resistor", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def set_battery_profile(self, value: str) -> None:
        # pylint: disable=missing-function-docstring
        data = {"device_id": self.id, "value": value}
        request = {"type": "request", "cmd": "arc_set_battery_profile", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def set_channel_samplerate(self, channel: str, value: int) -> None:
        """ Set the sample rate of a channel

        For available channels see :py:meth:`.Arc.enable_channel`

        Args:
            channel (str): Name of the channel to set the sample rate for.
            value (int): The sample rate to set

        """
        data = {"device_id": self.id, "channel": channel, "value": value}
        request = {"type": "request", "cmd": "arc_set_channel_samplerate", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def set_exp_voltage(self, value: float) -> None:
        """ Set the voltage of the expansion port.

        Args:
            value (float): Value to set expansion port voltage to, value should be between 1.2-5 (V).

        """
        data = {"device_id": self.id, "value": value}
        request = {"type": "request", "cmd": "arc_set_exp_voltage", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def set_gpo(self, pin: int, value: bool) -> None:
        """ Set the state of one of the GPO pins.

        Args:
            pin (int): ID of the GPO pin to set state of, 1 or 2.
            value (bool): True to enable GPO output, False to disable.

        """
        data = {"device_id": self.id, "pin": pin, "value": value}
        request = {"type": "request", "cmd": "arc_set_gpo", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def set_main(self, enable: bool) -> None:
        """ Turn on or off main power on a device.

        Args:
            enable (bool): True to turn on main power, False to turn off.

        """
        data = {"device_id": self.id, "enable": enable}
        request = {"type": "request", "cmd": "arc_set_main", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def set_main_current(self, value: float) -> None:
        """ Set the main current on Arc. Used when the Otii device is set in constant current mode.

        Args:
            value (float): Current to set in (A).

        """
        data = {"device_id": self.id, "value": value}
        request = {"type": "request", "cmd": "arc_set_main_current", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def set_main_voltage(self, value: float) -> None:
        """ Set the main voltage on Arc.

        Args:
            value (float): Value to set main voltage to (V).

        """
        data = {"device_id": self.id, "value": value}
        request = {"type": "request", "cmd": "arc_set_main_voltage", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def set_max_current(self, value: float) -> None:
        """ When the current exceeds this value, the main power will cut off.

        Args:
            value (float): Value to set max current to, value should be between 0.001-5 (A).

        """
        data = {"device_id": self.id, "value": value}
        request = {"type": "request", "cmd": "arc_set_max_current", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def set_power_regulation(self, mode: PowerRegulation) -> None:
        """ Set power regulation mode.

        Args:
            mode (str): One of the following: "voltage", "current", "inline", "off".

        """
        data = {"device_id": self.id, "mode": mode}
        request = {"type": "request", "cmd": "arc_set_power_regulation", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def set_range(self, arange: Range) -> None:
        """ Set the main outputs measurement range.

        Args:
            range (str): Current measurement range mode to set on main. "low" enables auto-range, "high" force high-range.

        """
        data = {"device_id": self.id, "range": arange}
        request = {"type": "request", "cmd": "arc_set_range", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def set_src_cur_limit_enabled(self, enable: bool) -> None:
        """ Enable voltage source current limit (CC) operation.

        Args:
            enable (bool): True means enable constant current, false means cut-off.

        """
        data = {"device_id": self.id, "enable": enable}
        request = {"type": "request", "cmd": "arc_set_src_cur_limit_enabled", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def set_supply_battery_emulator(
        self,
        battery_profile_id: str,
        *,
        series: int = 1,
        parallel: int = 1,
        used_capacity: Optional[float] = None,
        soc: Optional[float] = None,
        soc_tracking: bool = True,
    ) -> battery_emulator.BatteryEmulator:
        """ Set power supply to battery emulator.

        It is only possible to set one of **used_capacity** and **soc**. If neither is set,
        used_capacity is set to 0, and soc to 100.

        Args:
            battery_profile_id (string): Id of battery profile, as returned by otii.get_battery_profiles.
            series (int, optional): Number of batteries in series, defaults to 1.
            parallel (int, optional): Number of batteries in parallel, defaults to 1.
            used_capacity (int, optional): Used capacity, defaults to 0.
            soc (int, optional): State of Charge, defaults to 100.
            soc_tracking (bool, optional): State of Charge tracking, defaults to True.

        Returns:
            :py:class:`.BatteryEmulator`

        """
        data = {
            "device_id": self.id,
            "battery_profile_id": battery_profile_id,
            "series": series,
            "parallel": parallel,
            "used_capacity": used_capacity,
            "soc": soc,
            "soc_tracking": soc_tracking,
        }
        request = {
            "type": "request",
            "cmd": "arc_set_supply_battery_emulator",
            "data": data,
        }
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return battery_emulator.BatteryEmulator(response["data"]["battery_emulator_id"], self.connection)

    def set_supply_power_box(self) -> None:
        """ Set power supply to power box.
        """
        data = {"device_id": self.id}
        request = {"type": "request", "cmd": "arc_set_supply_power_box", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def set_tx(self, value: bool) -> None:
        """ The TX pin can be used as a GPO when the UART is disabled.

        Args:
            value (bool): True to enable TX output, False to disable.

        """
        data = {"device_id": self.id, "value": value}
        request = {"type": "request", "cmd": "arc_set_tx", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def set_uart_baudrate(self, value: int) -> None:
        """ Set UART baud rate.

        Args:
            value (int): Value to set UART baud rate to.

        """
        data = {"device_id": self.id, "value": value}
        request = {"type": "request", "cmd": "arc_set_uart_baudrate", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def wait_for_battery_data(self, timeout: float) -> float:
        # pylint: disable=missing-function-docstring
        data = {"device_id": self.id, "timeout": timeout}
        request = {"type": "request", "cmd": "arc_wait_for_battery_data", "data": data}
        response = self.connection.send_and_receive(request, 60 + (timeout / 1000))
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return response["data"]["value"]

    def write_tx(self, value: str) -> None:
        """ Write data to TX.

        Args:
            value (str): Data to write to TX.

        """
        data = {"device_id": self.id, "value": value}
        request = {"type": "request", "cmd": "arc_write_tx", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def get_property(self, name: str) -> Any:
        # pylint: disable=missing-function-docstring
        data = {"device_id": self.id, "name": name}
        request = {"type": "request", "cmd": "arc_get_property", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return response["data"].get("value", None)

    def set_property(self, name: str, value: Any) -> None:
        # pylint: disable=missing-function-docstring
        data = {"device_id": self.id, "name": name, "value": value}
        request = {"type": "request", "cmd": "arc_set_property", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def commit(self) -> None:
        # pylint: disable=missing-function-docstring
        data = {"device_id": self.id}
        request = {"type": "request", "cmd": "arc_commit", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def firmware_upgrade(self, filename: Optional[str] = None) -> None:
        """ Initiate device firmware update.

        Args:
            filename (str, optional): Firmware filename.

        """
        data = {"device_id": self.id, "filename": filename}
        request = {"type": "request", "cmd": "arc_firmware_upgrade", "data": data}
        response = self.connection.send_and_receive(request, 15)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
