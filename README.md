# Flow BLE Module 

* Design: [BLE-design](BLE-design.md)
* GATT Custom Profile Specification: Work in progress

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



## Install Manylabs BLE Service (flow-ble)

Assuming flow-ble source has been installed in /user/pi/flow-ble via

git clone https://github.com/manylabs/flow-ble

You follow these steps:

* Copy ble and advertisement service to service location and enable service

```bash
sudo cp -i /user/pi/flow-ble/mlserver/flowble.service /etc/systemd/system/
sudo cp -i /user/pi/flow-ble/mlserver/flowbleadv.service /etc/systemd/system/
sudo systemctl enable flowbleadv.service 
sudo systemctl enable flowble.service 
```

This will allow flowble to start on boot. You can skip the "systemctl enable" if
you don't want the service to be started automatically at boot time.

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


If there is a problem, daemon.log can give clues.
The trace below shows normail operation of the bluetooth daemon and flowble and flowbleadv daemons.



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