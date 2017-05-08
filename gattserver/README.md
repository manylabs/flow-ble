# Raspberry PI Manylabs BLE GATT Server

## Implementation Plan

In first iteration of GATT server will be implemented in Python, 
using a new library for peripheral support.


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


### Testing

To run the example and other tests, setup bluez as described in top level README for flow-ble project and then run:

```
./examples/hrserver.py
```

On the browser, load this page that tests a BLE heart rate emulator via Web Bluetooth.

https://webbluetoothcg.github.io/demos/heart-rate-sensor/


Or access via manylabs.github.io page with similar functionality
TODO: update this URL once github.io is configured for manylabs.

### Running flow ble server


NOTE: this will work once hpserver fully implemented:

```
./hpserver.py
```

TODO: profile support for the below.

On the browser, load this page that tests http proxy server:

TODO: implement and publish page on manylabs.github.io



