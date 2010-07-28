#! /bin/env python2.6

"""
Benchmark based on variable sized ring buffer.
See also PyCSP papers in CPA2009 proceedings.

Usage: tokenring-processes.py [options]

Options:
  -h, --help            show this help message and exit
  -t TOKENS, --tokens=TOKENS
                        Number of tokens in token ring
  -n NODES, --nodes=NODES
                        Number of nodes in token ring
  -x, --experiment      Experimental mode. Run 10 token rings with nodes 2^1
                        to 2^10 and print results

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

from csp.csp import process, Par
from patterns import TokenRing

import sys
sys.path.append('../')
from CChannel import CChannel as Channel
del sys

import time

TRIALS = 10000


@process
def ringproc(index=0, numnodes=64, tokens=1, inchan=None, outchan=None):
    """
    readset = inchan
    writeset = outchan
    """
    if tokens == 1 and index == 0:
        token = 1
        outchan.write(token)
    for i in xrange(TRIALS):
        outchan.write(inchan.read())
    # Avoid deadlock.
    if index == 1:
        inchan.read()


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
    parser.add_option('-x', '--experiment', dest='exp',
                      action='store_true', default=False,
                      help=('Experimental mode. Run 10 token rings with nodes '
                            + '2^1 to 2^10 and print results'))

    (options, args) = parser.parse_args()

    if options.exp:
        print('All times measured in microseconds.')
        for size in xrange(2, 50):
            try:
                print('Token ring with {0} nodes.'.format(2 ** size))
                starttime = time.time()
                TokenRing(ringproc, 2 ** size, numtoks=options.tokens).start()
                elapsed = time.time() - starttime
                mu = elapsed * 1000000 / float((TRIALS * (2 ** size)))
                print('{0}ms'.format(mu))
            except:
                continue
    else:
        TokenRing(ringproc, options.nodes, numtoks=options.tokens).start()
