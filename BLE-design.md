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

rpi	 -> Browser/laptop/tablet 	->	Server

rpi serves as BLE Peripheral. It's a server node that provide GATT services. It also advertises that the BLE peripheral device is available.
Browser hosting a page accesses BLEserves as BLE Central, it's the client node, consumer of GATT services
Browser hosting a page that accesses BLE will need to load using https protocol.

### Additional Design Notes

Similar/related projects:

We need to serve multiple sensor values periodically

* This shows how Nuimo service offers 13-byte "LED Characteristic". (python using Adafruit_BluefruitLE library)
https://github.com/AravinthPanch/nuimo-bluetooth-low-energy-python

* Experimental Bluez GATT service
 shows how to advertise custom profile and implement gatt server in Python
https://github.com/MostTornBrain/Waterrower

* bluez for Linux contains C code example of a gatt server and tools that allow to advertise services 

## Changes Required in the Deployment

* Server has to serve via https, since that's a requirement for Web BTE
 e.g. dataflow.manylabs.org production server, or local dev server normally running on non-secure port localhost:5000) 

## Manylabs sensors GATT profile

### Manylabs Realtime Service

The realtime services will provide reporting of current value of one or more sensors.

This service will use some of the patterns used in existing standard GATT profiles, such as Heart Rate Profile

See 
https://www.bluetooth.com/specifications/gatt/viewer?attributeXmlFile=org.bluetooth.service.heart_rate.xml
https://www.bluetooth.com/specifications/gatt/viewer?attributeXmlFile=org.bluetooth.characteristic.heart_rate_measurement.xml

Manylabs Realtime Service will offer the following characteristics:

* sensor_measurement
 access: Notify
 Description: This characteristic is used to send a sensor values measurements

* sensor_list
 access: Read
 Description: This characteristic allows to query which sensors are configured and available on RasPi 

* sensor_ctrl
 access: Write
 Description: The sensor Control Point characteristic is used to enable a Client to write control points to a Server to control behavior.
 For example the following will be specified:
  * data reporting interval
  * sensors selected for reporting (a subset of all available sensors in sensor_list)
 
* sensor_status
 access: Read, Notify
 Description: Allow to query sensor status such as error condition on the sensor and 
  is also used to notify the client about change in sensor status


TODO:

* finalize need for homogeneous timestamps accross sensors
  - for now, the design assumes timestamps are identical accross sensors to 
    increase data throughput/efficiency for multipe sensors (e.g. all sensors report at 1 second interval or 1 minute interval)

### Manylabs History Service

The history service will provide reporting of history of values. This is useful if the webapp wants to pull past history
date in order to display a chart for the last hour/day/week.

This assumes that a local storage is provided on RasPi.

Manylabs Realtime Service will offer the following characteristics:

* sensor_list
 access: Read
 Description: This characteristic allows to query which sensors are configured and available on RasPi 

* sensor_history
 access: Read
 Description: This characteristic is used to send a sensor values measurements

* sensor_history_ctrl
 access: Write
 Description: The sensor Control Point characteristic is used to enable a Client to write control points to a Server to control behavior.
 For example the following will be specified:
  * data reporting interval
  * sensors selected for reporting

TODO: 

* finalize local storage of sensor data on RasPI in order to decide on ML history service approach
* then design details of services, probably based on reporting several points in blocks of characteristics

### GATT BLE Flow Integration

Flow daemon currently provides upload data to the server.

How do we implement communication between flow daemon and flow-ble which may run in another process?

Although there are other approaches possible, one way to providing a clean and de-coupled communication between flow daemon and 
flow-ble module would be to add the following features to flow daemon:

* posting of real time sensor data to a queue, such as MQTT service 
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


