# Otii TCP Client for Python

The otii_tcp_client is a Python package for controlling the [Otii Automation Toolbox](https://www.qoitech.com/automation-toolbox/).

Client v1.0.8 breaks compatibility with Otii 2, we recommend you to upgrade to Otii 3.

New functionality in client v1.0.11 requiring [Otii software v3.5.5 or later](https://www.qoitech.com/download):

- `otii.connect` now waits for both a valid connection and for a license to be available.
- Added `otii.is_logged_in` and `otii.has_license`.

New functionality in client v1.0.10:

- Fixed a problem with not recognising some license types.

New functionality in client v1.0.9:

- Added `otii_client`, that makes it easier to connect to to the Otii server, and to login and reserve licenses.
  All the examples have been updated to use `otii_client`.
  Note, this replaces `otii.connect` that was introduced in v1.0.8.

New functionality in client v1.0.8 requiring [Otii software v3.5.2 or later](https://www.qoitech.com/download):

- Added a new API for battery emulation
- Added a simpler way to connect to the Otii server using `otii.connect`
- Added `arc.add_to_project` that explicitly adds the Arc/Ace device to the project

New functionality in client v1.0.7 requiring [Otii software v3.1.0 or later](https://www.qoitech.com/download):

- Added `otii_control.py` script for [user management](https://www.qoitech.com/docs/user-manual/automation-toolbox/user-management)

New functionality in client v1.0.6 requiring [Otii software v3.1.0 or later](https://www.qoitech.com/download):

- User management API (`otii.login`, `otii.logout`, `otii.get_licenses`, `otii.reserve_license` and `otii.return_license`)
- `arc.get_channel_samplerate` command for Arc and Ace devices
- `arc.set_channel_samplerate` command for Ace devices

New functionality in client v1.0.5:

- `get_devices` can now accept an optional `device_filter`

New functionality in client v1.0.5 requiring [Otii software v3.0.0 or later](https://www.qoitech.com/download):

- Statistics API (`get_channel_info`and `get_channel_statistics`)
- `firmware_upgrade` command for Arc and Ace devices

New functionality in client v1.0.4 requiring [Otii software v2.8.4 or later](https://www.qoitech.com/download):

- New optional `timeout` parameter added to `otii.get_devices`, that specifies the time in seconds to wait for an avaliable device
- Improved handling of TCP requests
- Added `arc.get_main` command

New functionality in client v1.0.3 requiring [Otii software v2.7.2 or later](https://www.qoitech.com/download):

- `Recording` object now exposes the start time as `start_time`

New functionality in client v1.0.2 requiring [Otii software v2.7.1 or later](https://www.qoitech.com/download):

- `arc.[gs]et_src_cur_limit_enabled` commands
- `arc.[gs]et_4wire` commands
- `arc.enable_battery_profiling`, `arc.set_battery_profile` and `arc.wait_for_battery_data` commands
