#!/usr/bin/env python3
'''
Otii 3 DC/DC efficiency

If you want the script to login and reserve a license automatically
add a configuration file called credentials.json in the current folder
using the following format:

    {
        "username": "YOUR USERNAME",
        "password": "YOUR PASSWORD"
    }

'''
import time
import matplotlib.pyplot as plt
import numpy as np
from otii_tcp_client import arc, otii_client

# Configure DC/DC sweep settings
MEASUREMENT_DURATION = 1 # s, how long measurement to take average for
STABILIZATION_TIME = 0.25 # s, time to wait to let the DC/DC stabilize
START_VOLTAGE = 3.1 # V, start with the highest voltage
STOP_VOLTAGE = 1.0 # V
NUMBER_OF_VOLTAGE_STEPS = 5 # number of steps for the linear voltage sweep
START_CURRENT = 100e-6 # A, start with the lowest current
STOP_CURRENT = 200e-3 # A
NUMBER_OF_CURRENT_STEP = 20 # number of steps for the logarithmic current sweep
SOURCING_DEVICE_NAME = 'Ace_source' # Change this to the name of your sourcing device
SINKING_DEVICE_NAME = 'Ace_sink' # Change this to the name of your sinking device
SAMPLE_RATE = 1000 # Samples per second

class AppException(Exception):
    '''Application Exception'''

def setup(otii: otii_client.Connect) -> tuple[arc.Arc, arc.Arc]:
    ''' Setup Otii device '''
    source_device = None
    sink_device = None

    # Get a reference to a Arc or Ace device
    devices = otii.get_devices()
    if len(devices) != 2:
        raise AppException('Two Arc/Aces must be connected!')
    for device in devices:
        if device.name == SOURCING_DEVICE_NAME:
            source_device = device
        elif device.name == SINKING_DEVICE_NAME:
            sink_device = device
    if source_device is None or sink_device is None:
        raise AppException('The chosen Arc/Ace devices are not connected!')

    # Configure the devices
    source_device.set_power_regulation('voltage')
    source_device.set_main_voltage(START_VOLTAGE)
    source_device.set_max_current(5)
    sink_device.set_power_regulation('current')
    sink_device.set_max_current(START_CURRENT)

    # Enable channels and set sample rates
    for device in [source_device, sink_device]:
        for channel in ['mc', 'mv','mp']:
            device.enable_channel(channel, True)
            if device.type == 'Ace':
                device.set_channel_samplerate(channel, SAMPLE_RATE)
        if device.type == 'Arc':
            device.set_src_cur_limit_enabled(True)

    return source_device, sink_device

def measure_efficiency(otii: otii_client.Connect) -> list[list[list[float]]]:
    ''' Measure efficiency '''
    # Setup the devices
    source_device, sink_device = setup(otii)

    # Turn on the main output of the devices
    for device in [source_device, sink_device]:
        device.set_main(True)

    # Get the active project
    project = otii.get_active_project()

    # Start the sweep
    data = []
    for voltage in np.linspace(START_VOLTAGE, STOP_VOLTAGE, num=NUMBER_OF_VOLTAGE_STEPS):
        source_device.set_main_voltage(voltage)
        project.start_recording()
        recording = project.get_last_recording()
        assert(recording is not None)
        current_statistics = []
        for current in np.logspace(np.log10(START_CURRENT), np.log10(STOP_CURRENT), num=NUMBER_OF_CURRENT_STEP):
            sink_device.set_main_current(-current)
            time.sleep(MEASUREMENT_DURATION+STABILIZATION_TIME)
            info = recording.get_channel_info(source_device.id, 'mc')
            device_statistics = [voltage, current] # [0] = set voltage, [1] = set current, [2] = input statistics, [3] = output statistics, [4] = efficiency
            for device in [source_device, sink_device]: # [0] = input [1] = output
                channel_statistics = []
                for channel in ['mc', 'mv', 'mp']: # [0] = measured current, [1] = measured voltage, [2] = measured power
                    channel_statistics.append(recording.get_channel_statistics(device.id, channel, info['to']-MEASUREMENT_DURATION, info['to'])["average"])
                device_statistics.append(channel_statistics)
            device_statistics.append(device_statistics[3][2] / -device_statistics[2][2] * 100) # Efficiency = Pout / Pin * 100%
            current_statistics.append(device_statistics)
        data.append(current_statistics)

    # Stop the recording
    project.stop_recording()

    # Turn off the main output of the devices
    for device in [source_device, sink_device]:
        device.set_main(False)

    return data

def plot_efficiency(data: list[list[list[float]]]) -> None:
    ''' Plot the efficiency '''
    # Find the lowest efficiency value
    lowest_efficiency = min(
        device_statistics[4]
        for voltage_data in data
        for device_statistics in voltage_data
    )
    plt.figure()
    plt.title('DC/DC Converter Efficiency')
    plt.xlabel('Output current (A)')
    plt.ylabel('Efficiency (%)')
    plt.grid()
    plt.xscale('log')
    for voltage_data in data:
        voltage = voltage_data[0][0]
        current = [data[1] for data in voltage_data]
        efficiency = [data[4] for data in voltage_data]
        plt.plot(current, efficiency, label=f'Vin = {voltage:.2f} V')
    plt.legend()
    plt.xlim(START_CURRENT, STOP_CURRENT)
    plt.ylim(lowest_efficiency*0.95, 105)
    plt.show()

def main() -> None:
    '''Connect to the Otii 3 application and run the measurement'''
    client = otii_client.OtiiClient()
    with client.connect() as otii:
        data = measure_efficiency(otii)
        plot_efficiency(data)

if __name__ == '__main__':
    main()
