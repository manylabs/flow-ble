# Test of Manylabs BLE Multi-sensor Device 

## Intro

Test application for testing Manylabs BLE service via Web bluetooth.

Status: For now will work with any standard Heart rate monitor device and bluez example gatt-server running on Manylabs RasPi.

Note: This test app is based on https://github.com/WebBluetoothCG/demos/tree/gh-pages/heart-rate-sensor

## Test Service Setup on RasPi

### Download and Build bluez

Download bluez-5.44.

Build:

```bash
cd ~/download/bluez-5.44
./configure --prefix=/usr --mandir=/usr/share/man --sysconfdir=/etc --localstatedir=/var --disable-systemd --enable-experimental --enable-maintainer-mode
make
```

### Start Advertising and test GATT server

```bash
cd ~/download/bluez-5.44
sudo tools/btmgmt -i hci0 power off
sudo tools/btmgmt -i hci0 le on
sudo tools/btmgmt -i hci0 connectable on
sudo tools/btmgmt -i hci0 name "Manylabs BLE"
sudo tools/btmgmt -i hci0 advertising on
sudo tools/btmgmt -i hci0 power on
```

### Start Advertising and test GATT server

```bash
cd ~/download/bluez-5.44
tools/btgatt-server -i hci0 -s low -t public -r -v
```


## Info About This Web App

To run locally, start serving from app directory, e.g. like this:

```bash
python -m SimpleHTTPServer 8888
```

Then navigate to http://localhost:8888/.

TODO: Make webapp available at https://manylabs.github.io/flow-ble/ml-ble-test/

<img src="https://raw.githubusercontent.com/manylabs/flow-ble/ml-ble-test/ml-raspi.jpg">

This web app tests the use of the Web Bluetooth API for getting sensor data from Manylabs multi-sensor RasPi device
supporting the custom Manylabs multi-sensor service.

