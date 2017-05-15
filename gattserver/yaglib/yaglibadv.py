"""Advertisement support for yaglib

"""
import sys
import dbus
import dbus.mainloop.glib
import dbus.service

from gi.repository import GObject

from .yaglib import *

LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
LE_ADVERTISEMENT_IFACE = 'org.bluez.LEAdvertisement1'
BLUEZ_ADAPTER_IFACE = 'org.bluez.Adapter1'
AD_PATH_BASE = '/org/bluez/yaglib/advertisement'


class AdvertisementManager(object):
    """GATT Manager - responsible for initiating and running GATT server.
    """

    def __init__(self):
        """Initialie dbus system bus
           acquire adapter/interface for org.bluez.LEAdvertisingManager1
           register advertising manager for 'org.bluez.LEAdvertisement1'

        """
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.bus = dbus.SystemBus()
        self.adapter = self._find_adapter()
        if not self.adapter:
            IFaceNotFoundException('%s interface not found' % LE_ADVERTISING_MANAGER_IFACE)

        adapter_props = dbus.Interface(self.bus.get_object(BLUEZ_SERVICE_NAME, self.adapter),
                                   "org.freedesktop.DBus.Properties");

        # Set adater to Powered on
        adapter_props.Set(BLUEZ_ADAPTER_IFACE, "Powered", dbus.Boolean(1))

        self.ad_manager = dbus.Interface(self.bus.get_object(BLUEZ_SERVICE_NAME, self.adapter),
                                LE_ADVERTISING_MANAGER_IFACE)


        self.mainloop = GObject.MainLoop()
        #print('Registering GATT application...')


    def _find_adapter(self):
        remote_om = dbus.Interface(self.bus.get_object(BLUEZ_SERVICE_NAME, '/'),
                                   DBUS_OM_IFACE)
        objects = remote_om.GetManagedObjects()

        for o, props in objects.items():
            #print("_find_adapter: o=%s, props=%s" % (o, props))
            if LE_ADVERTISING_MANAGER_IFACE in props:
                #print("_find_adapter: return: %s" % o)
                return o

        return None

    """
    def find_adapter(bus):
        remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'),
                                   DBUS_OM_IFACE)
        objects = remote_om.GetManagedObjects()

        # python 3
        #for o, props in objects.iteritems():
        # python 2.7
        for o, props in objects.iteritems():
            if LE_ADVERTISING_MANAGER_IFACE in props:
                return o

        return None
    """

    def add_advertisement(self, advertisement):
        """Adds advertisement.
        """
        self.advertisement = advertisement
        self.ad_manager.RegisterAdvertisement(self.advertisement.get_path(), {},
                                        reply_handler=register_ad_cb,
                                        error_handler=register_ad_error_cb)




    def run(self):
        self.mainloop.run()


class Advertisement(dbus.service.Object):

    def __init__(self, ctx, index, advertising_type):
        self.path = AD_PATH_BASE + str(index)
        self.bus = ctx.bus
        self.ad_type = advertising_type
        self.service_uuids = None
        self.manufacturer_data = None
        self.solicit_uuids = None
        self.service_data = None
        self.include_tx_power = None
        dbus.service.Object.__init__(self, ctx.bus, self.path)

    def get_properties(self):
        properties = dict()
        properties['Type'] = self.ad_type
        if self.service_uuids is not None:
            properties['ServiceUUIDs'] = dbus.Array(self.service_uuids,
                                                    signature='s')
        if self.solicit_uuids is not None:
            properties['SolicitUUIDs'] = dbus.Array(self.solicit_uuids,
                                                    signature='s')
        if self.manufacturer_data is not None:
            properties['ManufacturerData'] = dbus.Dictionary(
                self.manufacturer_data, signature='qv')
        if self.service_data is not None:
            properties['ServiceData'] = dbus.Dictionary(self.service_data,
                                                        signature='sv')
        if self.include_tx_power is not None:
            properties['IncludeTxPower'] = dbus.Boolean(self.include_tx_power)
        return {LE_ADVERTISEMENT_IFACE: properties}

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service_uuid(self, uuid):
        if not self.service_uuids:
            self.service_uuids = []
        self.service_uuids.append(uuid)

    def add_solicit_uuid(self, uuid):
        if not self.solicit_uuids:
            self.solicit_uuids = []
        self.solicit_uuids.append(uuid)

    def add_manufacturer_data(self, manuf_code, data):
        if not self.manufacturer_data:
            self.manufacturer_data = dbus.Dictionary({}, signature='qv')
        self.manufacturer_data[manuf_code] = dbus.Array(data, signature='y')

    def add_service_data(self, uuid, data):
        if not self.service_data:
            self.service_data = dbus.Dictionary({}, signature='sv')
        self.service_data[uuid] = dbus.Array(data, signature='y')

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != LE_ADVERTISEMENT_IFACE:
            raise InvalidArgsException()
        return self.get_properties()[LE_ADVERTISEMENT_IFACE]

    @dbus.service.method(LE_ADVERTISEMENT_IFACE,
                         in_signature='',
                         out_signature='')
    def Release(self):
        print('%s: Released!' % self.path)

def register_ad_cb():
    print('yaglib: Advertisement registered') 

def register_ad_error_cb(error):
    print('yaglib: Failed to register advertisement: ' + str(error))
    mainloop.quit()


