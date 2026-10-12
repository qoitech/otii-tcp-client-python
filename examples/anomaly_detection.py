#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "otii_tcp_client",
# ]
# ///
'''
Otii 3 Long term anomality detection

Records the device cycle by cycle, one recording = sleep + active, and compares
every cycle with a reference cycle using five numbers:

    sleep_avg        average current during sleep
    sleep_max        highest current during sleep (catches unexpected peaks)
    active_charge    charge used by the active period
    active_duration  length of the active period
    active_max       highest current during the active period

A cycle where any number differs from the reference by more than
its limit in LIMITS is kept and renamed, all other cycles are deleted.

Timeline (each recording is split when the active period ends):

    Initialisation : power-up until the first sleep entry
    Reference      : sleep + active, everything is compared against this
    0001, 0002 ... : sleep + active, analysed while the next cycle records
'''
import csv
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal, Optional

from otii_tcp_client import otii_client

# Device settings
SUPPLY_VOLTAGE = 3.6
OVERCURRENT = 1
BAUDRATE = 115200
DIGITAL_VOLTAGE = 3.3
SAMPLE_RATE = 10000

# Detection of sleep / active
ConditionType = Literal['message', 'current', 'gpio']
CONDITION_TYPE: ConditionType = 'message'

POLLING_TIME = 0.2          # s, how often the live recording is checked
CYCLE_TIMEOUT = 600         # s, max length of one sleep + active cycle (0 = none)

# 'message': both texts are needed to find the active period
WAKE_TEXT = 'Firmware version: 1.02b'
SLEEP_TEXT = 'Entering sleep mode'

# 'current': active = current above this level. Must be above any sleep peak.
ACTIVE_THRESHOLD = 1e-3     # A

# 'gpio': GPI1 level while the device is active
GPI_ACTIVE_LEVEL = True

START_GUARD_S = 0.05        # s, skipped at the start of each recording
PRE_WAKE_S = 0.1            # s, time before the detected wake-up that belongs to the active period.
MIN_SLEEP_S = 1.0           # s, a shorter sleep period is treated as an error

# Limits: maximum allowed relative change from the reference (0.10 = 10 %)
LIMITS = {
    'sleep_avg':       0.10,
    'sleep_max':       0.50,
    'active_charge':   0.10,
    'active_duration': 0.15,
    'active_max':      0.25,
}

MAX_CYCLES = 0              # 0 = run until Ctrl+C
RESULTS_CSV = Path('anomaly_results_simple.csv')

class AppException(Exception):
    '''Application exception'''

@dataclass
class Edges:
    '''Wake and sleep edges of one cycle, as time windows in seconds.'''
    wake_from: Optional[float]
    wake_to: Optional[float]
    sleep_from: float
    sleep_to: float

# Live detection: wait for the end of the active period

def timed_out(start: float) -> bool:
    return CYCLE_TIMEOUT > 0 and time.monotonic() - start > CYCLE_TIMEOUT

def wait_for_cycle(recording, device) -> Optional[Edges]:
    '''Block until the active period in `recording` has ended.
    Returns the wake and sleep edges, or None on timeout.'''
    if CONDITION_TYPE == 'message':
        return wait_for_message(recording, device)
    if CONDITION_TYPE == 'current':
        return wait_for_current(recording, device)
    if CONDITION_TYPE == 'gpio':
        return wait_for_gpi(recording, device)
    raise AppException(f'Unknown condition type {CONDITION_TYPE}')

def message_contains(text: str, pattern: str) -> bool:
    '''True if `pattern` appears in `text`. Characters at the start of the line
    that are not printable ASCII (e.g. ÿ or � when the UART wakes up) are
    removed first. The rest of the text is left untouched.'''
    i = 0
    while i < len(text) and not ' ' < text[i] <= '~':
        i += 1
    return pattern in text[i:]

def wait_for_message(recording, device) -> Optional[Edges]:
    start, seen, wake = time.monotonic(), 0, None
    while not timed_out(start):
        time.sleep(POLLING_TIME)
        count = recording.get_channel_data_count(device.id, 'rx')
        if count > seen:
            data = recording.get_channel_data(device.id, 'rx', seen, count - seen)
            seen = count
            for entry in data['values']:
                text = entry['value']
                if wake is None and message_contains(text, WAKE_TEXT):
                    wake = entry['timestamp']
                elif message_contains(text, SLEEP_TEXT):
                    t = entry['timestamp']
                    return Edges(wake, wake, t, t)
    return None

def wait_for_gpi(recording, device) -> Optional[Edges]:
    start, seen, wake = time.monotonic(), 0, None
    while not timed_out(start):
        time.sleep(POLLING_TIME)
        count = recording.get_channel_data_count(device.id, 'gpi1')
        if count > seen:
            data = recording.get_channel_data(device.id, 'gpi1', seen, count - seen)
            seen = count
            for entry in data['values']:
                t = entry['timestamp']
                if bool(entry['value']) == GPI_ACTIVE_LEVEL:
                    wake = t
                elif wake is not None:
                    return Edges(wake, wake, t, t)
    return None

def wait_for_current(recording, device) -> Optional[Edges]:
    '''Checks the max current of each new polling window. The active period has
    ended at the first window without any sample above ACTIVE_THRESHOLD after
    one or more windows with samples above it.'''
    start = time.monotonic()
    t_prev = None
    first_active = last_active = None
    while not timed_out(start):
        time.sleep(POLLING_TIME)
        info = recording.get_channel_info(device.id, 'mc')
        if t_prev is None:
            t_prev = info['from']
            continue
        t_now = info['to']
        if t_now <= t_prev:
            continue
        window_max = recording.get_channel_statistics(device.id, 'mc', t_prev, t_now)['max']
        if window_max > ACTIVE_THRESHOLD:
            first_active = first_active or (t_prev, t_now)
            last_active = (t_prev, t_now)
        elif last_active is not None:
            return Edges(first_active[0], first_active[1], last_active[0], last_active[1])
        t_prev = t_now
    return None

# Analysis
def refine_edge(recording, device, t_from: float, t_to: float, rising: bool) -> float:
    '''Exact time of a threshold crossing inside [t_from, t_to].
    Downloads only the samples of that window (one polling interval).'''
    if t_to <= t_from:
        return t_from
    i0 = recording.get_channel_data_index(device.id, 'mc', t_from)
    i1 = recording.get_channel_data_index(device.id, 'mc', t_to)
    data = recording.get_channel_data(device.id, 'mc', i0, max(1, i1 - i0))
    above = [i for i, v in enumerate(data['values']) if v > ACTIVE_THRESHOLD]
    if not above:
        return t_from if rising else t_to
    k = above[0] if rising else above[-1] + 1
    return data['timestamp'] + k * data['interval']

def measure(recording, device, edges: Edges) -> dict:
    '''The five comparison numbers for one finished recording.'''
    if edges.wake_from is None:
        raise ValueError('no wake-up found')
    wake = refine_edge(recording, device, edges.wake_from, edges.wake_to, rising=True)
    sleep = refine_edge(recording, device, edges.sleep_from, edges.sleep_to, rising=False)

    if sleep <= wake:
        raise ValueError('empty active period')
    active_start = wake - PRE_WAKE_S      # sleep ends where the active period starts

    t_start = recording.get_channel_info(device.id, 'mc')['from'] + START_GUARD_S
    if active_start - t_start < MIN_SLEEP_S:
        raise ValueError(f'sleep period too short ({active_start - t_start:.2f} s)')

    s = recording.get_channel_statistics(device.id, 'mc', t_start, active_start)
    a = recording.get_channel_statistics(device.id, 'mc', active_start, sleep)
    return {
        'sleep_avg':       s['average'],
        'sleep_max':       s['max'],
        'active_charge':   a['charge'],      # C (As)
        'active_duration': sleep - active_start,
        'active_max':      a['max'],
    }

def compare(ref: dict, new: dict) -> tuple[dict, list[str]]:
    '''Relative change per metric, and the metrics outside their limit.'''
    changes, failed = {}, []
    for metric, limit in LIMITS.items():
        change = new[metric] / ref[metric] - 1 if ref[metric] else float('inf')
        changes[metric] = change
        if abs(change) > limit:
            failed.append(f'{metric}{change * 100:+.0f}%')
    return changes, failed

# Reporting
UNITS = {'sleep_avg': 'A', 'sleep_max': 'A', 'active_charge': 'C',
         'active_duration': 's', 'active_max': 'A'}

def si(v: float, unit: str) -> str:
    for f, p in ((1, ''), (1e-3, 'm'), (1e-6, 'µ'), (1e-9, 'n')):
        if abs(v) >= f:
            return f'{v / f:.4g} {p}{unit}'
    return f'{v:.3g} {unit}'

def log_csv(cycle: int, name: str, kept: bool, values: dict, changes: dict) -> None:
    fields = ['time', 'cycle', 'name', 'kept'] + \
        [f'{m}{s}' for m in LIMITS for s in ('', '_change')]
    row = dict(time=datetime.now().isoformat(timespec='seconds'),
               cycle=cycle, name=name, kept=kept)
    for m in LIMITS:
        row[m] = values.get(m, '')
        row[f'{m}_change'] = changes.get(m, '')
    new_file = not RESULTS_CSV.exists()
    with RESULTS_CSV.open('a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        if new_file:
            writer.writeheader()
        writer.writerow(row)

def evaluate(recording, device, edges: Optional[Edges], ref: dict, cycle: int) -> None:
    '''Measure and compare one finished recording, then keep or delete it.'''
    values, changes = {}, {}
    if edges is None:
        failed = ['TIMEOUT']
    else:
        try:
            values = measure(recording, device, edges)
            changes, failed = compare(ref, values)
        except Exception as e:  # keep the recording for inspection
            failed = ['ERROR']
            print(f'Cycle {cycle:04d}: {e}')

    summary = '  '.join(f'{m} {c * 100:+.1f}%' for m, c in changes.items())
    if failed:
        name = f'{cycle:04d} {" ".join(failed)}'[:60]
        recording.rename(name)
        print(f'Cycle {cycle:04d}  FAIL  {summary}  -> kept as "{name}"')
    else:
        name = f'{cycle:04d}'
        recording.delete()
        print(f'Cycle {cycle:04d}  OK    {summary}')
    log_csv(cycle, name, bool(failed), values, changes)

def shutdown(project, device, last_rec) -> None:
    '''Always runs when the script exits, whatever the reason'''
    steps = [('turn off power', lambda: device.set_main(False))]
    if last_rec is not None:
        steps = [('stop recording', project.stop_recording)] + steps + \
                [('rename last recording', lambda: last_rec.rename('Partial (stopped)'))]
    for what, action in steps:
        try:
            action()
        except Exception as e:
            print(f'Could not {what}: {e}')
    print('Recording stopped and power off. Results in', RESULTS_CSV.resolve())

# Main loop
def run(otii) -> None:
    devices = otii.get_devices()
    devices = devices if isinstance(devices, list) else [devices]
    if len(devices) != 1:
        raise AppException(f'Exactly 1 device expected, found {len(devices)}')
    device = devices[0]
    project = otii.get_active_project()
    last_rec = None     # most recently started recording, for shutdown()

    def start_new_recording():
        nonlocal last_rec
        project.start_recording()
        last_rec = project.get_last_recording()
        return last_rec

    try:
        for channel in ['mc', 'mv', 'mp', 'rx', 'gpi1']:
            device.enable_channel(channel, True)
        if device.type == "Ace":  # If Ace hardware, set sample rate to SAMPLE_RATE sps. Arc is kept as default 4000/1000 sps.
            for channel in ['mc', 'mv', 'mp']:
                device.set_channel_samplerate(channel, SAMPLE_RATE)
        device.set_main_voltage(SUPPLY_VOLTAGE)
        device.set_max_current(OVERCURRENT)
        device.set_uart_baudrate(BAUDRATE)
        device.set_exp_voltage(DIGITAL_VOLTAGE)

        # Initialisation: power-up until the first sleep entry
        print('Initialisation: waiting for first sleep entry')
        init_rec = start_new_recording()
        device.set_main(True)
        if wait_for_cycle(init_rec, device) is None:
            raise AppException('Initialisation: no sleep entry detected')

        # Reference: sleep + active
        ref_rec = start_new_recording()
        init_rec.rename('Initialisation')
        print('Recording reference cycle')
        ref_edges = wait_for_cycle(ref_rec, device)
        if ref_edges is None:
            raise AppException('Reference: no sleep entry detected')

        current_rec = start_new_recording()     # cycle 0001 is now recording
        ref_rec.rename('Reference')
        try:
            ref = measure(ref_rec, device, ref_edges)
        except ValueError as e:
            raise AppException(f'Reference: {e}') from e
        print('Reference  ' + '  '.join(f'{m} {si(v, UNITS[m])}' for m, v in ref.items()))

        cycle = 1
        while MAX_CYCLES == 0 or cycle <= MAX_CYCLES:
            rec = current_rec
            edges = wait_for_cycle(rec, device)
            current_rec = start_new_recording()
            evaluate(rec, device, edges, ref, cycle)
            cycle += 1

    except KeyboardInterrupt:
        print('\nStopped by user')
    except AppException as e:
        print(f'\nStopped: {e}')
    finally:
        shutdown(project, device, last_rec)

def main() -> None:
    client = otii_client.OtiiClient()
    with client.connect() as otii:
        run(otii)

if __name__ == '__main__':
    main()