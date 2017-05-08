# Manylabs Flow BLE Design and Implementation Notes

## Intro

This document describes the flow-ble design and will capture some of the experiments/implementation
notes and other information pertinent to design decisions.

## Initial Tests

### rfcomm Test

On rpi:

```bash
sdptool add --channel=22 SP
sudo rfcomm listen /dev/rfcomm0 22
```
You'll see something like this:

```
Waiting for connection on channel 22
```

On client (e.g. a Ubuntu laptop):

see 
https://unix.stackexchange.com/questions/92255/how-do-i-connect-and-send-data-to-a-bluetooth-serial-port-on-linux

### GATT BLE Tests

For test of RasPi BLE server, see (ml-ble-test/README)[ml-ble-test/README]

## Design

This is the configuration of BLE manylabs deployment:

Raspberry PI	 -> Browser/laptop/tablet 	->	Server

Raspberry PI serves as BLE Peripheral. It has the server role that provide GATT services. 
It also advertises that the BLE peripheral device with Manylabs flow service is available.
Browser hosting a page accesses Raspberry PI and is in Central role, it also has the client role since it's a consumer of GATT services.
Browser hosting a page that accesses BLE peripheral via Web Bluetooth has to load from the server using https protocol.

### Additional Design Notes

Similar/related projects:

We need to serve multiple block values periodically

* This shows how Nuimo service offers 13-byte "LED Characteristic". (python using Adafruit_BluefruitLE library)
https://github.com/AravinthPanch/nuimo-bluetooth-low-energy-python

* Experimental Bluez GATT service
 shows how to advertise custom profile and implement gatt server in Python
https://github.com/MostTornBrain/Waterrower

* pygatt - Python Module for Bluetooth LE Generic Attribute Profile (GATT).
 * https://github.com/stratosinc/pygatt
 * https://pypi.python.org/pypi/pygatt
 * doesn't use dbus
 * 
 * active since 2013, about 4500 lines of code
 * uses a c helper process - stardard tool gatttool which is part of bluez distribution
	which is accessed via pipe from Python be sending commands, such as
	the process is started once, so pipe communication should be fast

* Bluetooth GATT SDK for Python
 * python3 required
 * https://github.com/getsenic/gatt-python
 * uses dbus

```
- uses dbus for implementation, core code is about 1500 lines:
wc bluepy/*.py
       4      16     115 bluepy/__init__.py
     140     448    4698 bluepy/blescan.py
     734    2277   25754 bluepy/btle.py
     201     418    5760 bluepy/get_services.py
     498    1437   16504 bluepy/s
```

* bluepy Python interface to Bluetooth LE on Linux
 * python gatt library (doesn't include gatt peripheral support yet)
 * https://github.com/IanHarvey/bluepy
 * doesn't use dbus
 * uses a c helper process custom writte ./bluepy/bluepy-helper.c
	which is accessed via pipe from Python be sending commands, such as
	the process is started once, so pipe communication should be fast


```
- core code is about 500 lines:
wc ./gatt/gatt_linux.py
     594    1632   21977 ./gatt/gatt_linux.py
```

* bluez for Linux contains C and Python code example of a gatt server and tools that allow to advertise services 
 * ./tools/tools/btgatt-server.c (C)
 * ./test/example-gatt-server (Python)
 * ./test/example-advertisement (Python)

## Changes Required in the Deployment

* Server has to serve via https, since that's a requirement for Web BTE
 e.g. dataflow.manylabs.org production server, or local dev server normally running on non-secure port localhost:5000) 

## Manylabs flow/blocks GATT profile

### Manylabs Realtime Service

The realtime services will provide reporting of current value of one or more blocks.

This service will use some of the patterns used in existing standard GATT profiles, such as Heart Rate Profile

See 
https://www.bluetooth.com/specifications/gatt/viewer?attributeXmlFile=org.bluetooth.service.heart_rate.xml
https://www.bluetooth.com/specifications/gatt/viewer?attributeXmlFile=org.bluetooth.characteristic.heart_rate_measurement.xml

Manylabs Realtime Service will offer the following characteristics:

* block_value
 access: Notify
 Description: This characteristic is used to send a block values measurements

* block_list
 access: Read
 Description: This characteristic allows to query which blocks are configured and available on RasPi 

* block_ctrl
 access: Write
 Description: The block Control Point characteristic is used to enable a Client to write control points to a Server to control behavior.
 For example the following will be specified:
  * data reporting interval
  * blocks selected for reporting (a subset of all available blocks in block_list)
 
* block_status
 access: Read, Notify
 Description: Allow to query block status such as error condition on the block and 
  is also used to notify the client about change in block status

TODO:

* finalize need for homogeneous timestamps accross blocks
  - for now, the design assumes timestamps are identical accross blocks to 
    increase data throughput/efficiency for multipe blocks (e.g. all blocks report at 1 second interval or 1 minute interval)

### Manylabs History Service

The history service will provide reporting of history of values. This is useful if the webapp wants to pull past history
date in order to display a chart for the last hour/day/week.

This assumes that a local storage is provided on RasPi.

Manylabs Realtime Service will offer the following characteristics:

* block_list
 access: Read
 Description: This characteristic allows to query which blocks are configured and available on RasPi 

* block_history
 access: Read
 Description: This characteristic is used to send a block values measurements

* block_history_ctrl
 access: Write
 Description: The block Control Point characteristic is used to enable a Client to write control points to a Server to control behavior.
 For example the following will be specified:
  * data reporting interval
  * blocks selected for reporting

Because of GATT BLE spec constraints, history payloads will not be greater than BLE_GATTS_VAR_ATTR_LEN_MAX (which is 512)

TODO: 

* finalize local storage of block data on RasPI in order to decide on ML history service approach
* then design details of services, probably based on reporting several points in blocks of characteristics
* consider using standard GATT profile for this: HPS - HTTP Proxy Service
 * HTTP Proxy Service - Bluetooth SIG: https://www.bluetooth.org/docman/handlers/downloaddoc.ashx?doc_id=308344
 https://www.bluetooth.com/specifications/gatt/viewer?attributeXmlFile=org.bluetooth.service.http_proxy.xml

Speed performance note:
BLE supports 0.3Mbps, thus the speed of history transfer will be less than this value.

### GATT BLE Flow Integration

Flow daemon currently provides upload data to the server.

How do we implement communication between flow daemon and flow-ble which may run in another process?

Although there are other approaches possible, one way to providing a clean and de-coupled communication between flow daemon and 
flow-ble module would be to add the following features to flow daemon:

* posting of real time block data to a queue, such as MQTT service 
* flow-ble would serve the data to BLE client/Central/bluetooth-web app as it appears in MQTT

This would steer the implementation on RasPi towards a robust microservices architecture, and also:

* allow to have more flexibility in phased implementation of flow-ble, first in C (which is readily available with working samples in bluez),
and eventually in Python, if necessary
* allow for a robust communication bus of different components as they evolve
* allow elegant stora of history data and other data via a store layer workint off of MQTT

## Other Changes Recommended for the Deployment and Data Flow

Since Web BTE supports discovery, manylabs dataflow setup can be simplified by allowing
manylabs browser UI to perform the discovery of rpi, then saving it in the configuration.
Another feature could be to make manually inserting PIN on the server after running flow on rpi for the first time un-necessary.


