#! /bin/env python2.6

"""
Benchmark based on variable sized ring buffer.
See also PyCSP papers in CPA2009 proceedings.

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
along with this program; if not, write to the Free Software

"""

__author__ = 'Sarah Mount <s.mount@wlv.ac.uk>'
__date__ = 'November 2009'

from csp.cspthread import *

@process
def ringproc(index=0, numnodes=64, tokens=1, inchan=None, outchan=None, _process=None):
    trials = 1000
    if tokens == 1 and index == 0:
        token = 1
        outchan.write(token)
    elif tokens != 1 and index % tokens == 0:
        token = 0
        outchan.write(token)
    if index == 0:
        starttime = time.time()
        cumtime = starttime
    for i in xrange(trials):
        token = inchan.read()
        token += 1
        outchan.write(token)
        if index == 0: cumtime += time.time()
    # Avoid deadlock.
    if index == 1: inchan.read()
	# Calculate channel communication time.
    if index == 0:
        # 2 Channel communications each time the token is passed.
        # 1*10^6 micro second == 1 second
        micros = (cumtime - starttime) / float((trials * numnodes * 2000000))
        print 'Channel communication time: %f microseconds' %  micros
    return

if __name__ == '__main__':
    from optparse import OptionParser

    parser = OptionParser()

    parser.add_option('-t', '--tokens', dest='tokens', 
                      action='store', type="int",
                      default=1,
                      help='Number of tokens in token ring')
    parser.add_option('-n', '--nodes', dest='nodes', 
                      action='store', type="int",
                      default=64,
                      help='Number of nodes in token ring')

    (options, args) = parser.parse_args()

    TokenRing(ringproc, options.nodes, numtoks=options.tokens).start()

