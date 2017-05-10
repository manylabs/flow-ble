#!/usr/bin/env python3
"""Example gatt server for heart_rate, battery and other services as defined in hrservice.py

"""
import sys
import time
#import threading, thread
import threading
#import gobject, gtk
# python3
import _thread as thread
from gi.repository import GObject as gobject
from gi.repository import Gdk




#from gi.repository import GObject
from yaglib import Application, GattManager
from hpservice import HttpProxyService, HttpStatusCodeChrc, HttpControlPointChrc, HttpEntityBodyChrc, log


#gtk.gdk.threads_init()
# python3
Gdk.threads_init()

service = None

class GeneratorTask(object):

   def __init__(self, generator, loop_callback, complete_callback=None):
       self.generator = generator
       self.loop_callback = loop_callback
       self.complete_callback = complete_callback

   def _start(self, *args, **kwargs):
       self._stopped = False
       for ret in self.generator(*args, **kwargs):
           if self._stopped:
               thread.exit()
           gobject.idle_add(self._loop, ret)
       if self.complete_callback is not None:
           gobject.idle_add(self.complete_callback)

   def _loop(self, ret):
       if ret is None:
           ret = ()
       if not isinstance(ret, tuple):
           ret = (ret,)
       self.loop_callback(*ret)

   def start(self, *args, **kwargs):
       threading.Thread(target=self._start, args=args, kwargs=kwargs).start()

   def stop(self):
       self._stopped = True





def get_next_payload():
    """Retrieves next payload to be sent via websocket."""
    body = '{"timestamp":"2017-05-04T01:38:00.336090Z","type":"sensor_update","parameters":{"values":[12.0],"name":"light"}}'
    return body

def charc_rw_cb(charc, read_or_write, options, value):
    """Control point write callback.
    Called before Read or Write completes and returns from
    Characteristics processing.
    Args: 
    	charc: Characteristic instance calling back.
    	read_or_write: 'read' or 'write'
    	options: options in ReadValue or WriteValue invocation
    	value: write or read value

    """
    global service
    log("charc_rw_cb")

    if charc.CHRC_UUID == HttpControlPointChrc.CHRC_UUID:
        """
     * the service calls server implementation via the custom callback
     * the server implementation provides the data, it could be any data retrieval:
       in classical "proxy" sense it can perform an HTTP request to get the data,
       or it can retrieve data from a queue that is serviing the URI specified via
       uri characteristic
     * the server places the acquired data into http_entity_body characteristic
       for later retrieval by the client
     * now that data is ready, a notification is triggered on http_status_code characteristic

        """
        log("charc_rw_cb: HttpControlPointChrc")
        if read_or_write == 'write':
            # TODO: implement cancel
            # CONTROL_POINT_CANCEL_CMD
            #if value == HttpControlPointChrc.CANCEL_CMD:
            #elif value == HttpControlPointChrc.GET_CMD or HttpControlPointChrc.GETS_CMD:
            #else ...
            body = get_next_payload()
            charc.service.http_entity_body_chrc.set_http_entity_body(body)
            charc.service.http_status_code_chrc.set_http_status_code(HttpStatusCodeChrc.STATUS_BIT_BODY_RECEIVED)
            charc.service.http_status_code_chrc.do_notify()
            if not service:
                service = charc.service
    elif charc.CHRC_UUID == HttpEntityBodyChrc.CHRC_UUID:
        log("charc_rw_cb: HttpEntityBodyChrc CHRC_UUID=%s" % charc.CHRC_UUID)
    else:
        log("charc_rw_cb: Unknown: CHRC_UUID=%s" % charc.CHRC_UUID)

def send_next_payload(service):
    #if not service:
    #    return
    if service.http_control_point_chrc.value not in [HttpControlPointChrc.GET, HttpControlPointChrc.GETS]:
        log("send_next_payload skipped since service.http_control_point_chrc.value is %d" \
          % service.http_control_point_chrc.value)
        return
    else:
        log("send_next_payload - sending")
        body = get_next_payload()
        service.http_entity_body_chrc.set_http_entity_body(body)
        service.http_status_code_chrc.do_notify() 

def send_next_payload_generator_thread(service):
    count = 0
    while True:
        count += 1
        time.sleep(2)
        log("count: %d" % count)
        yield service

def main():
    man = GattManager()
    service = HttpProxyService(man, 0, charc_rw_cb)
    man.add_service(service)
    # start send next payload thread
    GeneratorTask(send_next_payload_generator_thread, send_next_payload).start(service)
    man.run()

if __name__ == '__main__':
    main()
