# Python client for Otii TCP-server

The otii_tcp_client is a Python package for controlling the [Otii Automation Toolbox](https://www.qoitech.com/automation-toolbox/).

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
