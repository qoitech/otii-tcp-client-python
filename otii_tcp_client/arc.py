#!/usr/bin/env python3
#coding: utf-8
# pylint: disable=missing-module-docstring

from otii_tcp_client import otii_exception, battery_emulator

class Arc:
    """ Class to define an Arc or Ace device.
        Includes operations that can be run on the Arc or Ace.

    Attributes:
        type (str): Device type, "Arc" for Arc devices.
        id (str): ID of the Arc device.
        name (str): Name of the Arc device.
        connection (:obj:OtiiConnection): Object to handle connection to the Otii server.

    """
    def __init__(self, device_dict, connection):
        """
        Args:
            device_dict (dict): Dictionary with Arc parameters.
            connection (:obj:OtiiConnection): Object to handle connection to the Otii server.

        """
        self.type = device_dict["type"]
        self.id = device_dict["device_id"]
        self.name = device_dict["name"]
        self.connection = connection

    def add_to_project(self):
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

    def calibrate(self):
        """ Perform internal calibration of an Arc device.

        """
        data = {"device_id": self.id}
        request = {"type": "request", "cmd": "arc_calibrate", "data": data}
        response = self.connection.send_and_receive(request, 10)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def enable_5v(self, enable):
        """ Enable or disable 5V pin.

        Args:
            enable (bool): True to enable 5V, False to disable.

        """
        data = {"device_id": self.id, "enable": enable}
        request = {"type": "request", "cmd": "arc_enable_5v", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def enable_battery_profiling(self, enable):
        """ This will start the discharge profiling of a connected battery.

        Args:
            enable (bool): True to start battery profiling, False to stop.

        """
        data = {"device_id": self.id, "enable": enable}
        request = {"type": "request", "cmd": "arc_enable_battery_profiling", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def enable_channel(self, channel, enable):
        """ Enable or disable measurement channel.

        Args:
            channel (str): Name of the channel to enable or disable.
            enable (bool): True to enable channel, False to disable.

        """
        data = {"device_id": self.id, "channel": channel, "enable": enable}
        request = {"type": "request", "cmd": "arc_enable_channel", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def enable_exp_port(self, enable):
        """ Enable expansion port.

        Args:
            enable (bool): True to enable expansion port, False to disable.

        """
        data = {"device_id": self.id, "enable": enable}
        request = {"type": "request", "cmd": "arc_enable_exp_port", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def enable_uart(self, enable):
        """ Enable UART.

        Args:
            enable (bool): True to enable UART, False to disable.

        """
        data = {"device_id": self.id, "enable": enable}
        request = {"type": "request", "cmd": "arc_enable_uart", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def get_4wire(self):
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

    def get_adc_resistor(self):
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

    def get_channel_samplerate(self, channel):
        """ Get channel sample rate.

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

    def get_exp_voltage(self):
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

    def get_gpi(self, pin):
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

    def get_main(self):
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

    def get_main_voltage(self):
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

    def get_max_current(self):
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

    def get_range(self):
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

    def get_rx(self):
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

    def get_src_cur_limit_enabled(self):
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

    def get_supply_mode(self):
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

    def get_uart_baudrate(self):
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

    def get_value(self, channel):
        """ Get value from specified channel.
        This is not available for the rx channel.

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

    def get_version(self):
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

    def is_connected(self):
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

    def set_4wire(self, enable):
        """ Enable/disable 4-wire measurements using Sense+/-.

        Args:
            enable (bool): True to enable 4-wire, false to disable

        """
        data = {"device_id": self.id, "enable": enable}
        request = {"type": "request", "cmd": "arc_set_4wire", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def set_adc_resistor(self, value):
        """ Set the value of the shunt resistor for the ADC.

        Args:
            value (float): Value to set ADC resistor to, value should be between 0.001-22 (Ohm).

        """
        data = {"device_id": self.id, "value": value}
        request = {"type": "request", "cmd": "arc_set_adc_resistor", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def set_battery_profile(self, value):
        """ Set the battery profile.

        Args:
            value (list): The list of battery profile step dicts (max 10).
            Each dict is of the { "current|resistance|power" : SI value, "duration" : seconds } form.

        """
        data = {"device_id": self.id, "value": value}
        request = {"type": "request", "cmd": "arc_set_battery_profile", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def set_channel_samplerate(self, channel, value):
        """ Set the sample rate of a channel

        Args:
            channel (str): Name of the channel to set the sample rate for.
            value (int): The sample rate to set

        """
        data = {"device_id": self.id, "channel": channel, "value": value}
        request = {"type": "request", "cmd": "arc_set_channel_samplerate", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def set_exp_voltage(self, value):
        """ Set the voltage of the expansion port.

        Args:
            value (float): Value to set expansion port voltage to, value should be between 1.2-5 (V).

        """
        data = {"device_id": self.id, "value": value}
        request = {"type": "request", "cmd": "arc_set_exp_voltage", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def set_gpo(self, pin, value):
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

    def set_main(self, enable):
        """ Turn on or off main power on a device.

        Args:
            enable (bool): True to turn on main power, False to turn off.

        """
        data = {"device_id": self.id, "enable": enable}
        request = {"type": "request", "cmd": "arc_set_main", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def set_main_current(self, value):
        """ Set the main current on Arc. Used when the Otii device is set in constant current mode.

        Args:
            value (float): Current to set in (A).

        """
        data = {"device_id": self.id, "value": value}
        request = {"type": "request", "cmd": "arc_set_main_current", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def set_main_voltage(self, value):
        """ Get data entries from a specified channel of a specific recording.

        Args:
            value (float): Value to set main voltage to (V).

        """
        data = {"device_id": self.id, "value": value}
        request = {"type": "request", "cmd": "arc_set_main_voltage", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def set_max_current(self, value):
        """ When the current exceeds this value, the main power will cut off.

        Args:
            value (float): Value to set max current to, value should be between 0.001-5 (A).

        """
        data = {"device_id": self.id, "value": value}
        request = {"type": "request", "cmd": "arc_set_max_current", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def set_power_regulation(self, mode):
        """ Set power regulation mode.

        Args:
            mode (float): One of the following: "voltage", "current", "off".

        """
        data = {"device_id": self.id, "mode": mode}
        request = {"type": "request", "cmd": "arc_set_power_regulation", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def set_range(self, range):
        """ Set the main outputs measurement range.

        Args:
            range (str): Current measurement range mode to set on main. "low" enables auto-range, "high" force high-range.

        """
        data = {"device_id": self.id, "range": range}
        request = {"type": "request", "cmd": "arc_set_range", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def set_src_cur_limit_enabled(self, enable):
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
        battery_profile_id,
        *,
        series = 1,
        parallel = 1,
        used_capacity = None,
        soc = None,
        soc_tracking = True,
    ):
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
            battery_emulator(:obj:BatteryEmulator): Battery emulator

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

    def set_supply_power_box(self):
        """ Set power supply to power box.
        """
        data = {"device_id": self.id}
        request = {"type": "request", "cmd": "arc_set_supply_power_box", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def set_tx(self, value):
        """ The TX pin can be used as a GPO when the UART is disabled.

        Args:
            value (bool): True to enable TX output, False to disable.

        """
        data = {"device_id": self.id, "value": value}
        request = {"type": "request", "cmd": "arc_set_tx", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def set_uart_baudrate(self, value):
        """ Set UART baud rate.

        Args:
            value (int): Value to set UART baud rate to.

        """
        data = {"device_id": self.id, "value": value}
        request = {"type": "request", "cmd": "arc_set_uart_baudrate", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def wait_for_battery_data(self, timeout):
        """ Wait for battery data.

        Args:
            timeout (int): Maximum timeout in ms. May time out earlier if another Arc is returning battery data.
        Returns:
            dict: Battery data dict or None if timeout. The dict will contain "timestamp" in seconds,
                           "iteration", "step", "voltage" at the end of the current step and "discharge" in coulombs accumulating
                           the total discharge of the battery since profiling start.

        """
        data = {"device_id": self.id, "timeout": timeout}
        request = {"type": "request", "cmd": "arc_wait_for_battery_data", "data": data}
        response = self.connection.send_and_receive(request, 60 + (timeout / 1000))
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return response["data"]["value"]

    def write_tx(self, value):
        """ Write data to TX.

        Args:
            value (str): Data to write to TX.

        """
        data = {"device_id": self.id, "value": value}
        request = {"type": "request", "cmd": "arc_write_tx", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def get_property(self, name):
        # pylint: disable=missing-function-docstring
        data = {"device_id": self.id, "name": name}
        request = {"type": "request", "cmd": "arc_get_property", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
        return response["data"].get("value", None)

    def set_property(self, name, value):
        # pylint: disable=missing-function-docstring
        data = {"device_id": self.id, "name": name, "value": value}
        request = {"type": "request", "cmd": "arc_set_property", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def commit(self):
        # pylint: disable=missing-function-docstring
        data = {"device_id": self.id}
        request = {"type": "request", "cmd": "arc_commit", "data": data}
        response = self.connection.send_and_receive(request)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)

    def firmware_upgrade(self, filename = None):
        """ Initiate device firmware update.

        Args:
            filename (str, optional): Firmware filename.

        """
        data = {"device_id": self.id, "filename": filename}
        request = {"type": "request", "cmd": "arc_firmware_upgrade", "data": data}
        response = self.connection.send_and_receive(request, 15)
        if response["type"] == "error":
            raise otii_exception.Otii_Exception(response)
