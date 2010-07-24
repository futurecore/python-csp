#!/usr/bin/env python

"""
python-csp process for Toradex Oak sensors.

Copyright (C) Sarah Mount, 2009.

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

from csp.csp import *

from toradex import ToradexCurrent, ToradexMagR, ToradexMotion, ToradexDist
from toradex import ToradexTilt, ToradexLux, ToradexG, ToradexRH, ToradexP
from toradex import Toradex8ChannelA2D


@forever
def Current(outchan, debugchan=None, blink=True, _process=None):
    """python-csp interface to the Toradex Oak current sensor.
    """
    debugstring = 'Toradex current sensor'
    sensor = ToradexCurrent()
    senbsor.open()
    while True:
        if blink: sensor.led_on()
        current = sensor.get_data()[1]
        if blink: sensor.led_off()
        outchan.write(current)
        if debugchan is not None: debugchan.write(current)
        yield
    return


@forever
def MagR(outchan, debugchan=None, blink=True, _process=None):
    """python-csp interface to the Toradex Oak Magnetometer.
    """
    debugstring = 'Toradex Magnetometer'
    sensor = ToradexMagR()
    sensor.open()
    while True:
        if blink: sensor.led_on()
        mag, angle = sensor.get_data()[1:]
        if blink: sensor.led_off()
        outchan.write((mag, angle))
        if debugchan is not None: debugchan.write((mag, angle))
        yield
    return


@forever
def Motion(outchan, debugchan=None, blink=True, _process=None):
    """python-csp interface to the Toradex Oak motion sensor.
    """
    debugstring = 'Toradex Motion Sensor'
    sensor = ToradexMotion()
    sensor.open()
    while True:
        if blink: sensor.led_on()
        motion = sensor.get_data()[1]
        if blink: sensor.led_off()
        outchan.write(motion)
        if debugchan is not None: debugchan.write(motion)
        yield
    return


@forever
def Dist(outchan, debugchan=None, blink=True, _process=None):
    """python-csp interface to the Toradex Oak distance sensor.
    """
    debugstring = 'Toradex Oak Distance Sensor'
    sensor = ToradexDist()
    sensor.open()
    while True:
        if blink: sensor.led_on()
        dist = sensor.get_data()[1]
        if blink: sensor.led_off()
        outchan.write(dist)
        if debugchan is not None: debugchan.write(dist)
        yield
    return


@forever
def Tilt(outchan, debugchan=None, blink=True, _process=None):
    """python-csp interface to the Toradex Oak tilt sensor.
    """
    debugstring = 'Toradex Tilt Sensor'
    sensor = ToradexTilt()
    sensor.open()
    while True:
        if blink: sensor.led_on()
        accel, zen, azi = sensor.get_data()[1:]
        if blink: sensor.led_off()
        outchan.write((accel, zen, azi))
        if debugchan is not None: debugchan.write((accel, zen, azi))
        yield
    return


@forever
def Lux(outchan, debugchan=None, blink=True, _process=None):
    """python-csp interface to the Toradex Oak lux sensor.
    """
    debugstring = 'Toradex Lux Sensor'
    sensor = ToradexLux()
    sensor.open()
    while True:
        if blink: sensor.led_on()
        lux = sensor.get_data()[1]
        if blink: sensor.led_off()
        outchan.write(lux)
        if debugchan is not None: debugchan.write(lux)
        yield
    return


@forever
def Accelerometer(outchan, debugchan=None, blink=True, _process=None):
    """python-csp interface to the Toradex Oak 3-axis accelerometer.
    """
    debugstring = 'Toradex G 3-axis Accelerometer'
    sensor = ToradexG()
    sensor.open()
    while True:
        if blink: sensor.led_on()
        x, y, z = sensor.get_data()[1:]
        if blink: sensor.led_off()
        outchan.write((x, y, z))
        if debugchan is not None: debugchan.write((x, y, z))
        yield
    return


@forever
def RelativeHumidity(outchan, debugchan=None, blink=True, _process=None):
    """python-csp interface to the Toradex Oak RH sensor.
    """
    debugstring = 'Toradex RH Sensor'
    sensor = ToradexRH()
    sensor.open()
    while True:
        if blink: sensor.led_on()
        rh, temp = sensor.get_data()[1:]
        if blink: sensor.led_off()
        outchan.write((rh, temp))
        if debugchan is not None: debugchan.write((rh, temp))
        yield
    return


@forever
def Pressure(outchan, debugchan=None, blink=True, _process=None):
    """python-csp interface to the Toradex Oak pressure sensor.
    """
    debugstring = 'Toradex Pressure Sensor'
    sensor = ToradexP()
    sensor.open()
    while True:
        if blink: sensor.led_on()
        press, temp = sensor.get_data()[1:]
        if blink: sensor.led_off()
        outchan.write((press, temp))
        if debugchan is not None: debugchan.write((press, temp))
        yield
    return


@forever
def A2D8Channel(outchan, debugchan=None, blink=True, _process=None):
    """python-csp interface to the Toradex Oak 8 channel A2D.
    """
    debugstring = 'Toradex 8 Channel A2D'
    sensor = ToradexG()
    sensor.open()
    while True:
        if blink: sensor.led_on()
        data = sensor.get_data()[1:]
        if blink: sensor.led_off()
        outchan.write(data)
        if debugchan is not None: debugchan.write(data)
        yield
    return


if __name__ == '__main__':
    # Print data from a ToradexG accelerometer.
    channel = Channel()
    Par(Accelerometer(channel),
        Printer(channel)).start()
