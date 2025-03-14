# maxscale
MariaDB MaxScale

Build scripts for MaxScale versions that have expired from BSL and become GPL. Currently 21.06.18.

You will need to have nodejs 22 dnf module enabled.
If building in mock, include the following in your config template:
```
config_opts['module_setup_commands'] = [
    ('enable', 'nodejs:22'),
    ('install', 'nodejs:22/common'),
]
```
