"""Manylabs http_proxy service (HPS).

Uses standard HTTP profile as defined here:

https://www.bluetooth.org/docman/handlers/downloaddoc.ashx?doc_id=308344&_ga=1.265226703.1726630355.1492634329
https://www.bluetooth.com/specifications/gatt/viewer?attributeXmlFile=org.bluetooth.service.http_proxy.xml

Individual Characteristics:
https://www.bluetooth.com/specifications/gatt/viewer?attributeXmlFile=org.bluetooth.characteristic.uri.xml
https://www.bluetooth.com/specifications/gatt/viewer?attributeXmlFile=org.bluetooth.characteristic.http_headers.xml
https://www.bluetooth.com/specifications/gatt/viewer?attributeXmlFile=org.bluetooth.characteristic.uri.xml
etc.

Services:
UUID: 1823

Characteristics:

Name                Format  UUID    Mandatory Properties
----------------------------------------
URI                 utf8s   2ab6    Write, Write Long
HTTP Headers        utf8s   2ab7    Read, Write, Read Long, Write Long
HTTP Entity Body    utf8s   2ab8    Read, Write, Read Long, Write Long
HTTP Control Point  uint8   2ab9    Write
HTTP Status Code    uint8   2aba    Notify
HTTPS Security              2abb    Read

Characteristics class names/property nanes used in the implementation below:

class                   attribute
---------------------------------------
UriChrc                 uri
HttpHeadersChrc         http_headers
HttpEntityBodyChrc      http_entity_body
HttpControlPointChrc    http_control_point
HttpStatusCodeChrc      http_status_code
HttpSecurityChrc        https_security

Here is the full execution sequence on the client:

* write uri
* (optional) write http headers
* (optional) write http_entity_body
* write http_control_point
* on notify http_status_code:
 * read http_entity_body

Here is a more limited the sequence flow-ble service will need:

* write uri
* write http_control_point
* on notify http_status_code:
 * if success: read http_entity_body


"""


from random import randint
import dbus
"""Implements http_proxy service
"""
# needed for timer scheduling
#try:
#  from gi.repository import GObject
#except ImportError:
#  import gobject as GObject
from gi.repository import GObject
from yaglib import Service, Characteristic, Descriptor 


verbose = True 

def log(message):
    if verbose:
        print(message)

def log_error(message):
    print(message)

# http status code info
# https://www.bluetooth.com/specifications/gatt/viewer?attributeXmlFile=org.bluetooth.characteristic.http_status_code.xml
STATUS_BIT_HEADERS_RECEIVED = 1
STATUS_BIT_HEADERS_TRUNCATED = 2
STATUS_BIT_BODY_RECEIVED = 4
STATUS_BIT_BODY_TRUNCATED = 8

class HttpProxyService(Service):
    """http_proxy standard GATT profile/service. 

    """
    # HPS service UUID as per spec
    SERVICE_UUID = '00001823-0000-1000-8000-00805f9b34fb'

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.SERVICE_UUID, True)
        self.add_characteristic(UriChrc(bus, 0, self))
        self.add_characteristic(HttpHeadersChrc(bus, 1, self))
        self.http_entity_body_chrc = HttpEntityBodyChrc(bus, 2, self)
        self.add_characteristic(self.http_entity_body_chrc)
        self.add_characteristic(HttpControlPointChrc(bus, 3, self))
        self.http_status_code_chrc = HttpStatusCodeChrc(bus, 4, self)
        self.add_characteristic(self.http_status_code_chrc)
        self.https_security_chrc = HttpSecurityChrc(bus, 5, self)
        self.add_characteristic(self.https_security_chrc)
        self.energy_expended = 0

    def cancel_request(self):
        # TODO: adjust state
        pass 

    def do_request(self, method):
        """Perform a synchronous request, 
        using current values for uri, method etc.
        Fill http_entity_body that can be retrieved by client.
        Then initiate notification.

        """
        if method != "GET":
            log_error("Unsupported method: %s" % method)
            raise FailedException("0x80")
        self.http_entity_body_chrc.http_entity_body = '{"timestamp": "2017-05-04T01:38:00.336090Z", "type": "sensor_update", "parameters": {"values": [12.0], "name": "light"}}'
        # assume no header and body not truncated
        status_code = STATUS_BIT_BODY_RECEIVED
        self.set_http_status_code(status_code)
         

class UriChrc(Characteristic):
    # https://www.bluetooth.com/specifications/gatt/viewer?attributeXmlFile=org.bluetooth.characteristic.uri.xml
    CHRC_UUID = '00002ab6-0000-1000-8000-00805f9b34fb'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.CHRC_UUID,
                ['notify'],
                service)
        self.notifying = False
        self.uri = ""

    def WriteValue(self, value, options):
        """Save uri locally.

        """
        log('UriChrc.WriteValue')
        self.uri = self.decode_to_string(value)


class HttpHeadersChrc(Characteristic):
    # https://www.bluetooth.com/specifications/gatt/viewer?attributeXmlFile=org.bluetooth.characteristic.http_headers.xml
    CHRC_UUID = '00002ab7-0000-1000-8000-00805f9b34fb'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.CHRC_UUID,
                ['notify'],
                service)
        self.notifying = False
        self.http_headers = ""


class HttpEntityBodyChrc(Characteristic):
    CHRC_UUID = '00002ab8-0000-1000-8000-00805f9b34fb'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.CHRC_UUID,
                ['read'],
                service)
        self.http_entity_body = ""

    def ReadValue(self, options):
        # 
        # return [ 0x01 ]
        return self.http_entity_body


CONTROL_POINT_MAP = {
    1: ("GET",     "http"),
    2: ("HEAD",    "http"),
    3: ("POST",    "http"),
    4: ("PUT",     "http"),
    5: ("DELETE",  "https"),
    6: ("GET",     "https"),
    7: ("HEAD",    "https"),
    8: ("POST",    "https"),
    9: ("PUT",     "https"),
    10: ("DELETE", "https"),
}
CONTROL_POINT_CANCEL_CMD = 11

class HttpControlPointChrc(Characteristic):
    """HTTP Status Code :
        UUID    Property
        2ab9    Write

        See https://www.bluetooth.com/specifications/gatt/viewer?attributeXmlFile=org.bluetooth.characteristic.http_control_point.xml

        Value mapping:

                <Enumeration key="1" value="HTTP GET Request" requires="N/A" description="Initiates an HTTP GET Request." />
                <Enumeration key="2" value="HTTP HEAD Request" requires="N/A" description="Initiates an HTTP HEAD Request." />
                <Enumeration key="3" value="HTTP POST Request" requires="N/A" description="Initiates an HTTP POST Request." />
                <Enumeration key="4" value="HTTP PUT Request" requires="N/A" description="Initiates an HTTP PUT Request." />
                <Enumeration key="5" value="HTTP DELETE Request" requires="N/A" description="Initiates an HTTP DELETE Request." />
                <Enumeration key="6" value="HTTPS GET Request" requires="N/A" description="Initiates an HTTPS GET Reques.t" />
                <Enumeration key="7" value="HTTPS HEAD Request" requires="N/A" description="Initiates an HTTPS HEAD Request." />
                <Enumeration key="8" value="HTTPS POST Request" requires="N/A" description="Initiates an HTTPS POST Request." />
                <Enumeration key="9" value="HTTPS PUT Request" requires="N/A" description="Initiates an HTTPS PUT Request." />
                <Enumeration key="10" value="HTTPS DELETE Request" requires="N/A" description="Initiates an HTTPS DELETE Request." />
                <Enumeration key="11" value="HTTP Request Cancel" requires="N/A" description="Terminates any executing HTTP Request from the HPS Client." />

    """

    CHRC_UUID = '00002ab9-0000-1000-8000-00805f9b34fb'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.CHRC_UUID,
                ['write'],
                service)
        # uninitialized. Valid production values are 1 to 11
        self.value = 0

    def WriteValue(self, value, options):
        """When write control point is invoked by the system,

        """
        log('Heart Rate Control Point WriteValue called')

        if len(value) != 1:
            raise InvalidValueLengthException()

        byte = value[0]
        log('Control Point value: ' + repr(byte))

        self.value = int(byte)
        if self.value < 1 or self.value > 11:
            raise FailedException("0x80")
        elif self.value == CONTROL_POINT_CANCEL_CMD:
            # cancel 
            self.service.cancel_request()
        else:
            method = CONTROL_POINT_MAP[self.value]
            log('HttpControlPointChrc: WriteValue: invoking do_request')
            self.service.do_request(method)



class HttpStatusCodeChrc(Characteristic):
    """HTTP Status Code :           
        2aba    Notify

    see https://www.bluetooth.com/specifications/gatt/viewer?attributeXmlFile=org.bluetooth.characteristic.http_status_code.xml        


    """
    CHRC_UUID = '00002aba-0000-1000-8000-00805f9b34fb'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.CHRC_UUID,
                ['notify'],
                service)
        self.notifying = False
        self.http_status_code = 0

    def set_http_status_code(self, value):
        self.http_status_code = value 
        self.do_notify()

    def do_notify(self):
        """Notify/Send status code to dbus"""
        if self.notifying:
            value = []
            value.append(dbus.Byte(http_status_code))
            log('do_notify: sending ' % repr(value))
            self.PropertiesChanged(Characteristic.IFACE, 
                { 'Value': value }, [])

    def StartNotify(self):
        if self.notifying:
            #log('Already notifying, nothing to do')
            return

        self.notifying = True

    def StopNotify(self):
        if not self.notifying:
            log('StopNotify: Not notifying, nothing to do')
            return

        self.notifying = False



class HttpSecurityChrc(Characteristic):
    """HTTP Status Code :           
        2abb    Read
    """
    CHRC_UUID = '00002abb-0000-1000-8000-00805f9b34fb'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.CHRC_UUID,
                ['read'],
                service)
        self.https_security = False
        self.assign_read_value()

    def assign_read_value(self):
        """Can be called from ctor or by client service to change default
        value."""
        byte_value = dbus.Byte(0x01 if self.https_security else 0x00)
        self.value = [byte_value]

    def ReadValue(self, options):
        return value

