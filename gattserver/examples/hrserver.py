#!/usr/bin/env python3
"""Example gatt server for heart_rate, battery and other services as defined in hrservice.py

"""
import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service

import array
import sys

from yaglib import Application, GattManager
from hrservice import HeartRateService, BatteryService

def main():
    man = GattManager()
    man.add_service(HeartRateService(man, 0))
    man.add_service(BatteryService(man, 1))
    #man.add_service(TestService(man, 2))
    man.run()

if __name__ == '__main__':
    main()
