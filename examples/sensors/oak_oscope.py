#!/usr/bin/env python

"""
Chart the output of a Toradex Oak accelerometer.

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

__author__ = 'Sarah Mount <s.mount@wlv.ac.uk>'
__date__ = 'November 2009'
__version__ = '0.2'

from oscilloscope import Oscilloscope

def chart_accel():
    """Requires a Toradex Oak G to be attached to a USB port."""
    import dsp
    from toradex_csp import Accelerometer
    channels = [Channel() for i in range(7)]
    par = Par(Accelerometer(channels[0]),
              dsp.Unzip(channels[0], (channels[0:3])),
              Blackhole(channels[1]),
              Blackhole(channels[2]),
              dsp.Difference(channels[1], channels[2]),
              dsp.Square(channels[2], channels[3]),
              Oscilloscope(channels[3]))
    par.start()
    return


if __name__ == '__main__':
    chart_accel()
