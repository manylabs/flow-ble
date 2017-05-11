# Flow BLE Module 

* Design: [BLE-design](BLE-design.md)
* GATT Custom Profile Specification: Work in progress

## Pre-Requisites

On Raspian, the functionality as described below required an upgrade to the latest kernel kernel 1.20170427
and may only partially work with older Raspian version.

Also, BLE functionality was developed and tested on Ubuntu  16.04.1 with kernel as shown below
and should work.

```bash
uname -a
Linux peter-u16 4.4.0-75-generic #96-Ubuntu SMP Thu Apr 20 09:56:33 UTC 2017 x86_64 x86_64 x86_64 GNU/Linux
peter@peter-u16:~$ cat /etc/issue
Ubuntu 16.04.1 LTS \n \l
```

## Setting Up Bluetooth

Assuming an older stock version of Bluetooth is already installed on your system,
you'll build a more recent version (bluez-5.44) and since it's experimental,
modify the service settings to start the new version instead of the old one.

Alternatively, you could perform "sudo make install" after building to replace
the old bluez.


### Download bluez and Build

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
```  

* Modify service startup settings:

```bash
sudo vi /etc/systemd/system/bluetooth.target.wants/bluetooth.service

# modify the line below to point the the newly build bluetoothd
#  and use -E (experimental options) to start it

#ExecStart=/usr/lib/bluetooth/bluetoothd
ExecStart=/home/pi/download/bluez-5.44/src/bluetoothd -E
```

* Verify bluetooth still works and experimental mode is working properly

### Verify bluetooth still works 


#### Initializing BLE

Note: the "Disables BR/EDR" command below is not necessary on RasPi
but is needed if developing and testing on other platforms, such as Ubuntu x86_64

```bash
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


## Install Manylabs BLE Service (flow-ble)

Aassuming flow-ble source has been installed in /home/pi/flow-ble via

```bash
git clone https://github.com/manylabs/flow-ble
```

you will execute these commands to copy ble and advertisement service to service location and 
to enable the service:

```bash
sudo cp -i /home/pi/flow-ble/gattserver/flowble.service /etc/systemd/system/
sudo cp -i /home/pi/flow-ble/gattserver/flowbleadv.service /etc/systemd/system/
sudo systemctl enable flowbleadv.service 
sudo systemctl enable flowble.service 
```

This will allow flowble to start on boot. You can skip the "systemctl enable" if
you don't want the service to be started automatically at boot time.

## Verify flow-ble Service Works

To verify/test using Web Bluetooth, navigate to local or public flowble test URL.
For local, you must have setup and started a local server via:


```bash

```



## Starting and Stopping the Service

We can use stardard Linux commands (running as root):

```bash
systemctl start flowble.service
systemctl status flowble.service
systemctl stop flowble.service
```

or

```bash
service flowble start
service flowble status
service flowble stop
```

Here are some examples of starting and stopping flowble service and querying the status.

```bash
systemctl status flowble.service
● flowble.service - Manylabs Flow BLE Service
   Loaded: loaded (/etc/systemd/system/flowble.service; disabled)
   Active: inactive (dead)
$ sudo systemctl start flowble.service
$ systemctl status flowble.service
● flowble.service - Manylabs Flow BLE Service
   Loaded: loaded (/etc/systemd/system/flowble.service; disabled)
   Active: active (running) since Sat 2017-05-06 09:18:45 PDT; 1s ago
 Main PID: 12619 (python3)
   CGroup: /system.slice/flowble.service
           └─12619 python3 /home/pi/download/bluez-5.44/test/ml-gatt-server
$ sudo systemctl stop flowble.service
$ systemctl status flowble.service
● flowble.service - Manylabs Flow BLE Service
   Loaded: loaded (/etc/systemd/system/flowble.service; disabled)
   Active: inactive (dead)
```


## Troubleshooting


### Enable Verbose

You can enable verbose in hpserver.py and bluetoothd like this:

* in bluetoothd, enable option -d via
  * edit configuration to contain this line
  * .../bluetoothd -dE
  * vi /etc/systemd/system/bluetooth.target.wants/bluetooth.service 
* in hpserver.py
 #verboseLevel = 0
 verboseLevel = 2

daemon.log when running as a service and stdout if running in dev mode
will give information about what's failing

### Logs

If there is a problem, daemon.log can give clues.
The trace below shows normal operation of the bluetooth daemon and flowble and flowbleadv daemons.

Sample daemon.log after starting Bluetooth service.

```bash
pi@raspberrypi:~ $ sudo systemctl start bluetooth
pi@raspberrypi:~ $ tail /var/log/daemon.log
May  7 10:22:44 raspberrypi systemd[1]: Started Bluetooth service.
May  7 10:22:44 raspberrypi dbus[442]: [system] Activating via systemd: service name='org.freedesktop.hostname1' unit='dbus-org.freedesktop.hostname1.service'
May  7 10:22:44 raspberrypi bluetoothd[2231]: Bluetooth management interface 1.14 initialized
May  7 10:22:44 raspberrypi systemd[1]: Starting Hostname Service...
May  7 10:22:44 raspberrypi systemd[1]: Failed to reset devices.list on /system.slice: Invalid argument
May  7 10:22:44 raspberrypi bluetoothd[2231]: Endpoint registered: sender=:1.17 path=/MediaEndpoint/A2DPSource
May  7 10:22:44 raspberrypi bluetoothd[2231]: Endpoint registered: sender=:1.17 path=/MediaEndpoint/A2DPSink
May  7 10:22:44 raspberrypi systemd-hostnamed[2235]: Warning: nss-myhostname is not installed. Changing the local hostname might make it unresolveable. Please install nss-myhostname!
May  7 10:22:44 raspberrypi dbus[442]: [system] Successfully activated service 'org.freedesktop.hostname1'
May  7 10:22:44 raspberrypi systemd[1]: Started Hostname Service.
```

Sample daemon.log after starting flowble service.

```bash
pi@raspberrypi:~ $ sudo systemctl start flowble
pi@raspberrypi:~ $ tail /var/log/daemon.log
...
May  7 10:25:38 raspberrypi systemd[1]: [/etc/systemd/system/flowbleadv.service:4] Failed to add dependency on flowbleadv, ignoring: Invalid argument
May  7 10:25:38 raspberrypi systemd[1]: Starting Manylabs Flow BLE Service Advertisement...
May  7 10:25:38 raspberrypi systemd[1]: Started Manylabs Flow BLE Service Advertisement.
May  7 10:25:38 raspberrypi systemd[1]: Starting Manylabs Flow BLE Service...
May  7 10:25:38 raspberrypi systemd[1]: Started Manylabs Flow BLE Service.
```

Verify the required processes are running.
After services have been started properly, you should see the 3 lines below
in "ps" command output.

```bash
ps aux  |egrep "bash|gatt|blue|example"
root       433  0.2  1.2  18580 11744 ?        Ss   11:17   0:00 /usr/bin/python /home/pi/download/bluez-5.44/test/ml-advertisement
root       435  0.4  1.4  30116 14180 ?        Ssl  11:17   0:00 python3 /home/pi/download/bluez-5.44/test/ml-gatt-server
root       788  0.0  0.3   4856  3108 ?        Ss   11:17   0:00 /home/pi/download/bluez-5.44/src/bluetoothd -E
```

## Performance

This trace on the client using manylabsble.js library shows the following:

* Initial delay between GET request and "data ready notification" via http_status is about 300ms
* For websocket push, turn-around time is about 340ms between receiving "new data available" and completing data retrieval.
  Plus there is some delay for each turn-around since notify transport probably takes 100-200ms, so 
  the total is about 500ms

This could be improved by pushing data directly in websocket mode instead of sending http_status notify first.
That would reduce latency from when data becomes available on raspi and the time the client recieves it by
about 20-30%.

Trace of JavaScript (Chrome dev tool): Initial GET request to "notification received" trace (about 500ms)

```
18:16:59.075 manylabsble.js:179 requestGet
18:16:59.345 app.js:45 handleHttpStatus.event characteristicvaluechanged
18:16:59.354 app.js:58 handleHttpStatus.event: Retrieving body...
```

Trace of JavaScript (Chrome dev tool): Websocket pushing data via write http_status notification and body retrieval completion (about 340ms)

```
18:18:39.521 app.js:45 handleHttpStatus.event characteristicvaluechanged
18:18:39.532 app.js:58 handleHttpStatus.event: Retrieving body...
18:18:40.055 app.js:60 getHttpBody.body: {"timestamp":"2017-05-04T01:38:00.336090Z","type":"sensor_update","parameters":{"values":[12.0],"name":"light"}}
18:18:41.472 app.js:45 handleHttpStatus.event characteristicvaluechanged
18:18:41.473 app.js:58 handleHttpStatus.event: Retrieving body...
18:18:41.810 app.js:60 getHttpBody.body: {"timestamp":"2017-05-04T01:38:00.336090Z","type":"sensor_update","parameters":{"values":[12.0],"name":"light"}}
18:18:44.006 app.js:45 handleHttpStatus.event characteristicvaluechanged
18:18:44.008 app.js:58 handleHttpStatus.event: Retrieving body...
18:18:44.308 app.js:60 getHttpBody.body: {"timestamp":"2017-05-04T01:38:00.336090Z","type":"sensor_update","parameters":{"values":[12.0],"name":"light"}}
```

