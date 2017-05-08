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


## Building bluez and testing bluez functionality

### Download and Build

Run the commands below as "pi" (regular) user.

* download a recent bluez. We used bluez v5.44
  http://www.kernel.org/pub/linux/bluetooth/bluez-5.44.tar.xz

* untar and build with --enable-experimental

```bash
mkdir -p ~/download
cd ~/download
tar zxvf bluez-5.44.tar.xz
cd bluez-5.44
./configure --prefix=/usr --mandir=/usr/share/man --sysconfdir=/etc --localstatedir=/var --disable-systemd --enable-experimental --enable-maintainer-mode
make
sudo make install
```  

### Initializing BLE

Note: the "Disables BR/EDR" command below is not necessary on RasPi
but is needed if developing and testing on other platforms, such as Ubuntu x86_64

```bash 
cd ~/download/bluez-5.44/tools
# run as root
sudo -s
btmgmt -i hci0 power off 
btmgmt -i hci0 le on
btmgmt -i hci0 connectable on
# Set alias. This only needs to be done once
btmgmt -i hci0 name "Manylabs BLE"

# this line is necessary for some BT chipsets, otherwise gatt server will not
# receive connections
# see http://stackoverflow.com/questions/27552644/bluetooth-low-energy-android-gatt-client-connect-to-linux-gatt-server
btmgmt -i hci0 bredr off        # Disables BR/EDR !
btmgmt -i hci0 advertising on
btmgmt -i hci0 power on
```

### Testing

After initialization above, run this program which is a heart rate emulator.

```bash
btgatt-server -i hci0 -s low -t public -r -v
```

On the browser, load this page that tests a BLE heart rate emulator via Web Bluetooth.

https://webbluetoothcg.github.io/demos/heart-rate-sensor/


Or access via manylabs.github.io page with similar functionality
TODO: update this URL once github.io is configured for manylabs.


