# Raspberry PI Manylabs BLE GATT Server

## Implementation Plan

In first iteration of GATT server will be implemented in C, based on
heart rate examples from bluez: gatt-server.
This will run as a separate daemon.

See bluez-5.44/tools/btgatt-server.c

We may later develop wrapper libraries in Python.

The following libraries may be used at some point for ML GATT server implementation
and for testing ble server. Currently none of the libraries work in a way that would
assist in GATT server implementation, but they may be useful without modifications
on the client side as a test tool and later they may be extended to support GATT
server functionality.

* gattlib/pygattlib: This is a Python library to use the GATT Protocol for Bluetooth LE devices. It is a wrapper around the implementation used by gatttool in bluez package. It does not call other binaries to do its job :)
 https://bitbucket.org/OscarAcena/pygattlib
* pybluez: https://github.com/karulis/pybluez
* pygatt: https://github.com/peplin/pygatt


