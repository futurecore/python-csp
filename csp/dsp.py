#!/bin/env python

"""
Digital signal processing for python-csp.

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

from __future__ import absolute_import 

from .csp import *

import math

# TODO: Use numpy for more sophisticated processes.

ACCEL_DUE_TO_GRAVITY = 9.80665


@forever
def Zip(outchan, inchannels):
    """Take data from a number of input channels, and write that
    data as a single list to L{outchan}.
    """
    while True:
        outchan.write([chan.read() for chan in inchannels])
        yield


@forever
def Unzip(inchan, outchans):
    """Continuously read tuples of data from a single input channel and send
    each datum out down its own output channel.
    """
    while True:
        data = inchan.read()
        for i in range(data):
            outchans[i].write(data[i])
        yield


@forever
def Sin(inchan, outchan):
    while True:
        outchan.write(math.sin(inchan.read()))
        yield


@forever
def Cos(inchan, outchan):
    while True:
        outchan.write(math.cos(inchan.read()))
        yield


@forever
def Tan(inchan, outchan):
    while True:
        outchan.write(math.tan(inchan.read()))
        yield


@forever
def GenerateFloats(outchan):
    counter = 0
    increment = 0.1
    while True:
        outchan.write(counter * increment)
        counter += 1
        yield


@forever
def Magnitude(inchan, outchan):
    while True:
        acceldata = inchan.read()
        mag = 0.0
        for axis in acceldata: mag += axis ** 2
        outchan.write(math.sqrt(mag))
        yield


@forever
def Difference(inchan, outchan, window=1):
    cache = 0.0
    while True:
        acceldata = inchan.read()
        try:
            outchan.write(acceldata - cache)
            cache = acceldata
        except IndexError:
            pass
        yield


@forever
def Square(inchan, outchan):
    while True:
        data = inchan.read()
        outchan.write(data ** 2)
        yield


@forever
def Normalise(inchan, outchan, start=0.0, end=100.0):
    scale = end - start
    while True:
        outchan.write(inchan.read() / scale)
        yield    


@forever
def Threshold(thresh, inchan, outchan):
    while True:
        mag = inchan.read()
        if mag >= thresh:
            outchan.write(mag)
        yield

