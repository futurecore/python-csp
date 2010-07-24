#!/usr/bin/env python

"""Design pattern support for python-csp.

Copyright (C) Sarah Mount, 2010.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A ParTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have rceeived a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
"""


__author__ = 'Sarah Mount <s.mount@wlv.ac.uk>'
__date__ = 'May 2010'


from csp.csp import Par

from CChannel import CChannel as Channel

__all__ = ['TokenRing']

class TokenRing(Par):
    def __init__(self, func, size, numtoks=1):
        self.chans = [Channel() for channel in xrange(size)]
        self.procs = [func(index=i,
                           tokens=numtoks,
                           numnodes=size,
                           inchan=self.chans[i-1],
                           outchan=self.chans[i]) for i in xrange(size)]
        super(TokenRing, self).__init__(*self.procs) 
        return

