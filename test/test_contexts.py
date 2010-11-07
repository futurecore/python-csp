#!/usr/bin/python

"""
Test the CSP class, found in csp.csp and its context managers.

TODO: Replace this with proper unit testing.

Copyright (C) Sarah Mount, 2010.

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

import sys

sys.path.insert(0, "..")

from csp.csp import CSP


def printme(*args):
    print ' '.join(map(lambda x: str(x), args))


def testme1():
    p = CSP()
    with p.par():
        p.process(printme, 1, 2, 3, 4, 5)
        p.process(printme, 6, 7, 7, 8, 9)
        p.process(printme, 2, 3, 6, 3, 2)
    p.start()


def testme2():
    p = CSP()
    with p.seq():
        p.process(printme, 1, 2, 3)
        with p.par():
            p.process(printme, 1)
            p.process(printme, 2)
            p.process(printme, 3)
        p.process(printme, 5, 6, 7)
    p.start()


if __name__ == '__main__':
    print 'Test 1'
    testme1()
    print 'Test 2'
    testme2()
    
