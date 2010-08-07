#!/usr/bin/env python

"""
Generic interface to all Toradex OAK sensors.

Copyright (C) Sarah Mount, 2008.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have rceeived a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import struct
from hidsensor import *


__author__ = 'Sarah Mount <s.mount@wlv.ac.uk>'
__credits__ = 'Mat Murray'
__date__ = 'November 2008'
__version__ = '0.1'


#DEBUG = True
DEBUG = False


def _debug(*args):
    """Customised debug logging.

    FIXME: Replace this with the builtin logging module.
    """
    smap = list(map(str, args))
    if DEBUG:
        print('DEBUG: ' + ' '.join(smap))


class ToradexSensor(HIDSensor):
    """Generic interface to a single Toradex sensor."""
    VID = 0x1b67         # Vendor ID. PID *MUST* be set in subclasses.
    EP = 0x82            # Endpoint address for interrupt reads.
    # Get or set a datum.
    SET = 0x00
    GET = 0x01
    # Store data in flash or RAM.
    RAM = 0x0
    FLASH = 0x01
    # Sampling rates.
    AFTER_SAMPLING = 0x0 # Factory default.
    AFTER_CHANGE = 0x1
    FIXED_RATE = 0x2
    # LED modes.
    OFF = 0x0            # Factory default.
    ON = 0x1
    BLINK_SLOW = 0x2
    BLINK_FAST = 0x3
    BLINK_PULSE = 0x4

    def __init__(self):
        HIDSensor.__init__(self)

    def feature_report(self, path, buff):
        size = 32 # For all Toradex sensors
        while True:
            reply = self.get_feature_report(path, size)
            if reply[0] == hid.HID_RET_FAIL_GET_REPORT:
                _debug('Did not get report.')
                break
            else:
                report = struct.unpack('32B', reply[1])
                _debug('Report length:', len(report))
                _debug(report)
                if report[0] == 0xff:
                    break
        reply = hid.hid_set_feature_report(self._interface, path, buff)
        if reply == hid.HID_RET_FAIL_SET_REPORT:
            _debug('Did not set report.')
        else:
            _debug('Response:', reply)
        # Get reply
        while True:
            reply = hid.hid_get_feature_report(self._interface, path, size)
            if reply[0] == hid.HID_RET_FAIL_GET_REPORT:
                _debug('Did not get report.')
                break
            else:
                _debug('Error message:', reply[0])
                report = struct.unpack('32B', reply[1])
                _debug(report)
                if report[0] == 0xff:
                    break
 
    def blink_led(self, rate='slow'):
        if rate == 'fast': self.blink_led_fast()
        elif rate == 'pulse': self.blink_led_pulse()
        else: self.blink_led_slow()
        return

    def blink_led_slow(self):
        buff = struct.pack('6b27x',
                           ToradexSensor.SET, ToradexSensor.FLASH,
                           0x01, 0x01, 0x00,
                           ToradexSensor.BLINK_SLOW)
        self.feature_report((), buff)
        return
        
    def blink_led_fast(self):
        buff = struct.pack('6b27x',
                           ToradexSensor.SET, ToradexSensor.FLASH,
                           0x01, 0x01, 0x00,
                           ToradexSensor.BLINK_FAST)
        self.feature_report((), buff)
        return

    def blink_led_pulse(self):
        buff = struct.pack('6b27x',
                           ToradexSensor.SET, ToradexSensor.FLASH,
                           0x01, 0x01, 0x00,
                           ToradexSensor.BLINK_PULSE)
        self.feature_report((), buff)
        return

    def led_on(self):
        buff = struct.pack('6b27x',
                           ToradexSensor.SET, ToradexSensor.FLASH,
                           0x01, 0x01, 0x00,
                           ToradexSensor.ON)
        self.feature_report((), buff)
        return

    def led_off(self):
        buff = struct.pack('6b27x',
                           ToradexSensor.SET, ToradexSensor.FLASH,
                           0x01, 0x01, 0x00,
                           ToradexSensor.OFF)
        self.feature_report((), buff)
        return

    def set_sample_rate(self, rate):
        """Set the sample rate of the sensor.
        N.B. This is distinct from the "data rate", which is the rate at
        which the sensor provides data for interrupt reads.
        """
        raise NotImplementedError('Need report paths!')

    def set_data_rate(self, rate):
        """Set the data rate of the sensor.
        N.B This is not the rate at which data is sampled from the
        transducer, but the rate at which the sensor makes data
        available for an interrupt read.
        """
        raise NotImplementedError('Need report paths!')

    def _unpack(self, bytes, size=2):
        """Unpack data from an interrupt read into a sequence of bytes.
        Intended to be used in conjunction with __parse and read_data:
        __parse(_unpack(_read_data()))
        """
        try:
            data = struct.unpack('<%gH' % size, bytes) # FIXME: OK for Python3? 
        except struct.error:
            return None
        return data

    def _parse(self, bytes):
        """Parse bytes from an interrupt read into Python types.
        Intended to be used in conjunction with _unpack and _read_data:
        _parse(_unpack(_read_data()))
        """
        raise NotImplemented('Must be overridden by subclasses')

    def _read_data(self, size=4):
        """Perform an interrupt read on the sensor.
        Intended to be used in conjunction with _unpack and _parse:
        _parse(_unpack(_read_data()))
        """
        bytes = self.interrupt_read(ToradexSensor.EP, size, 1000)
        if bytes: return bytes
        else: return None

    def __str__(self):
        return 'Generic Python interface to Toradex OAK sensors'


class ToradexCurrent(ToradexSensor):
    """Interface to a single Toradex current sensor."""
    PID = 0x0009

    def _parse(self, bytes):
        return bytes[0]/100.0, bytes[1]/100000.0

    def get_current(self):
        data = self._parse(self._unpack(self._read_data()))
        if data: return data[1]
        else: return None

    def get_data(self):
        return self._parse(self._unpack(self._read_data()))

    def __str__(self):
        return 'Python interface to the Toradex current sensor'

    def _debug_str(self):
        return 'Frame: {0}s Current: {1}A'


class ToradexMagR(ToradexSensor):
    """Interface to a single Toradex magnetic rotation sensor."""
    PID = 0x000b

    def _parse(self, data):
        return data[0]/1000.0, data[1]/1000.0, data[2], data[3]

    def get_angle(self):
      	data = self._parse(self._unpack(self._read_data(size=8), size=4))
        if data: return data[1]
        else: return None

    def get_magnitute(self):
      	data = self._parse(self._unpack(self._read_data(size=8), size=4))
        if data: return data[2]
        else: return None

    def get_status(self): # blah.
      	data = self._parse(self._unpack(self._read_data(size=8), size=4))
        if data: return data[3]
        else: return None

    def get_data(self):
      	data = self._parse(self._unpack(self._read_data(size=8), size=4))
        if data: return data[:-1]
        else: return None

    def __str__(self):
        return 'Python interface to the Toradex magnetic rotation sensor'

    def _debug_str(self):
        return 'Frame: {0}s Angle: {1}rad Magnitude: {2}'


class ToradexMotion(ToradexSensor):
    """Interface to a single Toradex IR motion sensor."""
    PID = 0x0006

    def _parse(self, data):
        return data[0]/1000.0, data[1]

    def get_motion(self):
      	data = self._parse(self._unpack(self._read_data()))
        if data: return data[1]
        else: return None

    def get_data(self):
      	data = self._parse(self._unpack(self._read_data()))
        if data: return data
        else: return None

    def __str__(self):
        return 'Python interface to the Toradex IR motion sensor'

    def _debug_str(self):
        return 'Frame: {0}s Motion: {1} # motion events'


class ToradexDist(ToradexSensor):
    """Interface to a single Toradex distance sensor."""
    PID = 0x0005

    def _parse(self, data):
        return data[0]/1000.0, data[1]/1000.0

    def get_dist(self):
      	data = self._parse(self._unpack(self._read_data()))
        if data: return data[1]
        else: return None

    def get_data(self):
      	data = self._parse(self._unpack(self._read_data()))
        if data: return data
        else: return None

    def __str__(self):
        return 'Python interface to the Toradex distance sensor'

    def _debug_str(self):
        return 'Frame: {0}s Dist: {1}m'


class ToradexTilt(ToradexSensor):
    """Interface to a single Toradex tilt sensor."""
    PID = 0x0004

    def _parse(self, data):
        return data[0]/1000.0, data[1]/100.0, data[2]/1000.0, data[3]/1000.0

    def get_accel(self):
      	data = self._parse(self._unpack(self._read_data(size=8), size=4))
        if data: return data[1]
        else: return None

    def get_zenith(self):
      	data = self._parse(self._unpack(self._read_data(size=8), size=4))
        if data: return data[2]
        else: return None

    def get_azimuth(self):
      	data = self._parse(self._unpack(self._read_data(size=8), size=4))
        if data: return data[3]
        else: return None

    def get_data(self):
      	data = self._parse(self._unpack(self._read_data(size=8), size=4))
        if data: return data
        else: return None

    def __str__(self):
        return 'Python interface to the Toradex tilt sensor'

    def _debug_str(self):
        return 'Frame: {0}s accel: {1}ms^-2 zen: {2}rad ax:{3}rad'


class ToradexLux(ToradexSensor):
    """Interface to a single Toradex lux sensor."""
    PID = 0x0003

    def _parse(self, data):
        return data[0]/1000.0, data[1]

    def get_lux(self):
       	data = self._parse(self._unpack(self._read_data(size=4)))
        if data: return data[1]
        else: return None

    def get_data(self):
      	data = self._parse(self._unpack(self._read_data(size=4)))
        if data: return data
        else: return None

    def __str__(self):
        return 'Python interface to the Toradex lux sensor'

    def _debug_str(self):
        return 'Frame: {0}s lux: {1}Lux'

    
class ToradexG(ToradexSensor):
    """Interface to a single ToradexG sensor."""
    PID = 0x000a

    def _parse(self, data):
        return data[0]/1000.0, data[1]/1000.0, data[2]/1000.0, data[3]/1000.0

    def get_x(self):
      	data = self._parse(self._unpack(self._read_data(size=8), size=4))
        if data: return data[1]
        else: return None

    def get_y(self):
      	data = self._parse(self._unpack(self._read_data(size=8), size=4))
        if data: return data[2]
        else: return None

    def get_z(self):
      	data = self._parse(self._unpack(self._read_data(size=8), size=4))
        if data: return data[3]
        else: return None

    def get_data(self):
      	data = self._parse(self._unpack(self._read_data(size=8), size=4))
        if data: return data
        else: return None

    def __str__(self):
        return 'Python interface to the Toradex G (3-axis accel)  sensor'

    def _debug_str(self):
        return 'Frame: {0}s x: {1}ms^-2 y: {2}ms^-2 z:{3}ms^-2'


class ToradexRH(ToradexSensor):
    """Interface to a single ToradexRH sensor."""
    PID = 0x0001

    def _parse(self, data):
        return data[0]/1000.0, data[1]/100.0, data[2]/100.0-273.0

    def get_temp(self):
      	data = self._parse(self._unpack(self._read_data(size=6), size=3))
        if data: return data[2]
        else: return None

    def get_humidity(self):
      	data = self._parse(self._unpack(self._read_data(size=6), size=3))
        if data: return data[1]
        else: return None

    def get_data(self):
      	data = self._parse(self._unpack(self._read_data(size=6), size=3))
        if data: return data
        else: return None

    def __str__(self):
        return 'Python interface to the Toradex RH sensor'

    def _debug_str(self):
        return 'Frame: {0}s Humidity: {1}% Temperature: {2}C'


class ToradexP(ToradexSensor):
    """Interface to a single ToradexP sensor."""
    PID = 0x0002

    def _parse(self, data):
        # Note that the Toradex / Oak data sheet is incorrect here
        return data[0]/1000.0, data[1]*10.0, data[2]/10.0-273.0

    def get_temp(self):
      	data = self._parse(self._unpack(self._read_data(size=6), size=3))
        if data: return data[2]
        else: return None

    def get_pressure(self):
      	data = self._parse(self._unpack(self._read_data(size=6), size=3))
        if data: return data[1]
        else: return None

    def get_data(self):
      	data = self._parse(self._unpack(self._read_data(size=6), size=3))
        if data: return data
        else: return None

    def __str__(self):
        return 'Python interface to the ToradexP sensor'

    def _debug_str(self):
        return 'Frame: {0}s Pressure: {1}Pa Temperature: {2}C'


class Toradex8ChannelA2D(ToradexSensor):
    """Interface to a single Toradex +/-10V 8 Channel ADC"""
    PID = 0x000e
    MODE_SINGLE_ENDED = 0x0 # Factory default.
    MODE_PSEUDO_DIFFERENTIAL = 0x01

    def __init__(self):
        ToradexSensor.__init__(self)
        # Start with the factory default.
        self.mode = Toradex8ChannelA2D.MODE_SINGLE_ENDED
        return

    def set_channel_name(self, channel, name):
        """Set user channel name."""
        raise NotImplementedError('Need report paths!')

    def get_channel_name(self, channel):
        """Get user channel name."""        
        raise NotImplementedError('Need report paths!')

    def set_offset_channel(self, channel, offset):
        """Set absolute offset of a given channel (mV)."""
        raise NotImplementedError('Need report paths!')

    def get_offset_channel(self, channel):
        """Get absolute offset of a given channel (mV)."""
        raise NotImplementedError('Need report paths!')

    def set_input_mode(self, mode):
        """Set input mode.
        mode must be one of:
            Toradex8ChannelA2D.MODE_SINGLE_ENDED
                Toradex8ChannelA2D.MODE_PSEUDO_DIFFERENTIAL
        """
        if not mode in (Toradex8ChannelA2D.MODE_SINGLE_ENDED,
                        Toradex8ChannelA2D.MODE_PSEUDO_DIFFERENTIAL):
            raise HIDError('Toradex8ChannelA2D in undefined input mode!')
        raise NotImplementedError('Need report paths!')

    def get_input_mode(self):
        """Get input mode.
        return value will be one of:
            Toradex8ChannelA2D.MODE_SINGLE_ENDED
                Toradex8ChannelA2D.MODE_PSEUDO_DIFFERENTIAL
        """
        raise NotImplementedError('Need report paths!')

    def _parse(self, data):
        return (data[0]/1000.0, data[1]/1000.0, data[2]/1000.0,
                data[3]/1000.0, data[4]/1000.0, data[5]/1000.0,
                data[6]/1000.0, data[7]/1000.0, data[8]/1000.0)

    def get_data(self):
        data = self._parse(self._unpack(self._read_data(size=18), size=9))
        if data: return data
        else: return None

    def get_channel(self, channel):
        data = self.get_data()
        if not data: return None
        else: return data[channel+1]

    def __str__(self):
        return 'Python interface to the Toradex +/-10V 8 Channel ADC'

    def _debug_str(self):
        if self.mode == Toradex8ChannelA2D.MODE_SINGLE_ENDED:        
            return ('Frame no: {0}s, CH0-GNDi: {1}V, CH1-GNDi: {2}V, ' +
                    'CH2-GNDi: {3}V, CH3-GNDi: {4}V, CH4-GNDi: {5}V, ' +
                    'CH5-GNDi: {6}V, CH6-GNDi: {7}V, CH7-GNDi: {8}V')
        elif self.mode == Toradex8ChannelA2D.MODE_PSEUDO_DIFFERENTIAL:
            return ('Frame no: {0}s, CH0-1: {1}V, CH1-0: {2}V, CH2-3: {3}V, ' +
                    'CH3-2: {4}V, CH4-5: {5}V, CH5-4: {6}V, CH6-7: {7}V, ' +
                    'CH7-6: {8}V,')
        else: raise HIDError('Toradex8ChannelA2D in undefined input mode!')


# Define a collection of Toradex sensors. Use this when you
# have more than one sensor connected to the USB bus(ses).
ToradexSensorCollection = HIDSensorCollection([Toradex8ChannelA2D,
                                               ToradexCurrent,
                                               ToradexMagR,
                                               ToradexMotion,
                                               ToradexDist,
                                               ToradexTilt,
                                               ToradexLux,
                                               ToradexG,
                                               ToradexRH,
                                               ToradexP])

### Test interfaces
def __test(sensorclass):
    sensor = sensorclass()
    print(sensor.open())
    while True:
        sensor.blink_led()
        print(sensor._debug_str().format(&sensor.get_data()))

def __test_rh(): __test(ToradexRH)
def __test_g(): __test(ToradexG)
def __test_tilt(): __test(ToradexTilt)
def __test_lux(): __test(ToradexLux)
def __test_dist(): __test(ToradexDist)
def __test_motion(): __test(ToradexMotion)
def __test_magr(): __test(ToradexMagR)
def __test_current(): __test(ToradexCurrent)     
def __test_pressure(): __test(ToradexP)
def __test_A2D(): __test(Toradex8ChannelA2D)

def __test_collection(n=10):
    import time
    collection = ToradexSensorCollection
    print(collection.open())
    while n>0:
        time.sleep(0.1)
        collection._debug()
        n -= 1
    del collection

if __name__ == '__main__':
    # Test sensor collection
#    __test_collection()

# Test individual sensors
#    __test_rh()
#    __test_g()
#    __test_tilt()
#    __test_lux()
#    __test_dist()
#    __test_motion()
    __test_magr()
#    __test_current()
#    __test_pressure()
#    __test_A2D()
    # def __test2():
    #     sensor1 = Toradex8ChannelA2D()
    #     sensor2 = Toradex8ChannelA2D()
    #     print sensor1.open()
    #     print sensor2.open()
    #     while True:
    #         print sensor1._debug_str().format(*sensor1.get_data())
    #         print sensor2._debug_str().format(*sensor2.get_data())
    # __test2()
    
