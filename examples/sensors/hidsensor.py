#!/usr/bin/env python

"""
Generic interface to any USB HID sensor.

Copyright (C) Sarah Mount 2008.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import struct
import hid
import os
import sys 

__author__ = 'Sarah Mount <s.mount@wlv.ac.uk>'
__date__ = 'November 2008'
__version__ = '0.1'


#DEBUG = True
DEBUG = False


class HIDError(Exception):

    def __init__(self, value):
        """Wrapper for exceptions resulting from calls to libhid.
        value should be (<method-name>, <hid-retval>).
        """
        super(HIDError, self).__init__()
        self.value = value
        return

    def __str__(self):
        return 'Call to {0} failed with return code {1}'.format(*self.value)


class HIDMatcher(object):

    def __init__(self, vid, pid, errstream=sys.stderr):
        self.matcher = hid.HIDInterfaceMatcher()
        self.matcher.vendor_id = vid
        self.matcher.product_id = pid
        return

    @property
    def vendor(self):
        return self.matcher.vendor_id

    @property
    def product(self):
        return self.matcher.product_id


class HIDSensor(object):

    def __init__(self, id=None, errstream=sys.stderr):
        self._id = None
        self._error = errstream
        # Debugging
        if DEBUG:
            hid.hid_set_debug(hid.HID_DEBUG_ALL)
            hid.hid_set_debug_stream(self._error)
            hid.hid_set_usb_debug(0)
        # Initialisation
        if not hid.hid_is_initialised(): # Doesn't seem to work
            try: # Belt AND braces, Sir?
                hid.hid_init()
            except HIDError:
                pass
        self._interface = hid.hid_new_HIDInterface()
        # Ensure we only use one HIDMatcher class per
        # type of sensor, with some reflection-fu.
        #if not 'MATCHER' in self.__class__.__dict__:
        if not hasattr(self.__class__, 'MATCHER'):
            self.__class__.MATCHER = HIDMatcher(self.__class__.VID,
                                                self.__class__.PID)
        return
    
    def open(self):
        self._check(hid.hid_force_open(self._interface,
                                       0,
                                       self.__class__.MATCHER.matcher,
                                       3),
                 'hid_force_open')
        self._id = self._interface.id
        with os.tmpfile() as tmpfile:
            hid.hid_write_identification(tmpfile, self._interface)
            tmpfile.flush()
            tmpfile.seek(0)
            details = tmpfile.read() + '\n'
        return details

    def __del__(self): # Destructor
#    try:
        ### WHY IS THIS BROKE?
        if self._interface is None: return
    #        elif hid.hid_is_opened(self._interface):
    #            hid.hid_delete_HIDInterface(self._interface)
    #        else:
    #            print('Closing interface {1}'.format(self._id))
    #            self._check(hid.hid_close(self._interface), 'hid_close')
        return
#    finally:
#        super(HIDSensor, self).__del__()

    def interrupt_read(self, endpoint, size, timeout):
        ret, bytes = hid.hid_interrupt_read(self._interface,
                                            endpoint, size, timeout)
        self._check(ret, 'hid_interrupt_read')
        return bytes

    def _check(self, retval, method, success=hid.HID_RET_SUCCESS):
        if retval != success:
            raise HIDError((method, retval))

    @property
    def vendor(self):
          return self.__class__.MATCHER._vendor

    @property
    def product(self):
          return self.__class__.MATCHER._product

    @property
    def id(self):
      return self._id
  
    def set_feature_report(self, path, buffer):
            self._check(hid.hid_set_feature_report(self._interface, path, buffer),
                        'set_feature_report')
            
            return

    def get_feature_report(self, path, size):
            reply = hid.hid_get_feature_report(self._interface, path, size)
            #self._check(ret, 'get_feature_report')
            return reply


class HIDSensorCollection:
    """Interface to all attached sensors of known types."""
    MAX_HID_DEVS = 20 # Limited by libhid

    def __init__(self, hidclasses):
        self._hidtypes = {}
        for hidclass in hidclasses:
            print('Searching for {0} sensors...'.format(hidclass.__name__))
            self._hidtypes[hidclass] = HIDMatcher(hidclass.VID, hidclass.PID)
        self._interfaces = {}
        retval = hid.hid_init()
        if retval != hid.HID_RET_SUCCESS:
            raise HIDError(('hid_init', retval))
        return

    def __del__(self):
        return
       
    def open(self):
        for hidclass in self._hidtypes:
            for i in range(HIDSensorCollection.MAX_HID_DEVS):
                try:
                    hidif = hidclass()
                    details = hidif.open()
                    if details:
                        print('Found HID sensor: {0}'.format(hidif._id))
                        self._interfaces[hidif._id] = hidif
                except HIDError as e:
                    del hidif 
                #except Error, e:
                    #continue
        return

    def get_all_data(self):
        return [hidif.get_data() for hidif in list(self._interfaces.values())]

    def _debug(self):
        print(len(self._interfaces), 'HID sensors attached')
        for hidif in self._interfaces:
            print('Interface: {0},'.format(str(hidif)), end=' ')
            print(self._interfaces[hidif]._debug_str().format(self._interfaces[hidif].get_data()))

