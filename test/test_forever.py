#!/usr/bin/env python

"""
Test the @forever process decorator which creates server processes.

Copyright (C) Sarah Mount, 2010.

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

import operator
import os
import sys

from functools import reduce

sys.path.insert(0, "..")

from csp.csp import *
from csp.builtins import Generate, Printer


def test_builtins():
    channel, skip = Channel(), Skip()
    skip //= Generate(channel), Printer(channel)


@forever
def fact(outchan):
    """
    readset = flibble, foo
    writeset = outchan, foo
    """
    n = 1
    f = 1
    while True:
        if n == 1:
            outchan.write(1)
        else:
            f = reduce(operator.mul, list(range(1, n)))
            outchan.write(f)
        n += 1
        yield

def test_fact():
    channel, skip = Channel(), Skip()
    skip //= fact(channel), Printer(channel)

if __name__ == '__main__':
#    test_builtins()
    test_fact()
