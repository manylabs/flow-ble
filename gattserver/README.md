# Raspberry PI Manylabs BLE GATT Server

## yaglib

yaglib (Yet Another Gatt LIBrary) provide peripheral server side support
based on bluez dbus API.
It is based on examples from bluez-5.44 source distributions: bluez/test/example-get-server

yaglib has been tested with Python3 only

Currently, examples directory contains one server example that simulates heart rate service:

See:
```
./examples/hrserver.py
./examples/hrservice.py
./examples/testservice.py
```

## Requirements

python3-dbus installed via apt-get

apt-get install python3-dbus


### Running flow ble server and Testing 

See top level README flow-ble/README.md
