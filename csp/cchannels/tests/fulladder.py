#!/usr/bin/env python

"""Python CSP full adder.

Based on code from PyCSP - Communicating Sequential Processes for
Python.  John Markus Bjorndalen, Brian Vinter, Otto Anshus.  CPA 2007,
Surrey, UK, July 8-11, 2007.  IOS Press 2007, ISBN 978-1-58603-767-3,
Concurrent Systems Engineering Series (ISSN 1383-7575).

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
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
"""

__author__ = 'Sarah Mount <s.mount@wlv.ac.uk>'
__date__ = 'December 2008'


from csp.csp import Par, process

import sys
sys.path.append('../')
from CChannel import CChannel as Channel
del sys

from csp.builtins import *


@process
def Bool1(cout):
    """
    readset =
    writeset = cout
    """
    while True:
        cout.write(1)
        cout.write(1)
        cout.write(0)
        cout.write(0)
    return

@process
def Bool2(cout):
    """
    readset =
    writeset = cout
    """
    while True:
        cout.write(1)
        cout.write(0)
        cout.write(1)
        cout.write(0)
    return

def fulladder(A_in, B_in, C_in, Sum_in, Carry_in):
    """Full adder implementation.

    Based on Bjorndalen, Vinter & Anshus (2007).
    """
    Aa = Channel()
    Ab = Channel()
    Ba = Channel()
    Bb = Channel()
    Ca = Channel()
    Cb = Channel()
    i1 = Channel()
    i1a = Channel()
    i1b = Channel()
    i2 = Channel()
    i3 = Channel()

    return Par(Delta2(A_in, Aa, Ab),
               Delta2(B_in, Ba, Bb),
               Delta2(C_in, Ca, Cb),
               Delta2(i1, i1a, i1b),
               Xor(Aa, Ba, i1),
               Xor(i1a, Ca, Sum_in),
               And(Ab, Bb, i2),
               And(i1b, Cb, i3),
               Or(i2, i3, Carry_in))

if __name__ == '__main__':
    print('\nFull adder implemented in Python CSP\n')
    # Inputs to full adder
    A = Channel()
    B = Channel()
    Cin = Channel()
    # Outputs of full adder
    Carry = Channel()
    Sum = Channel()
    # Channels for printing to STDOUT
    PCarry = Channel()
    PSum = Channel()
    # Create and start adder
    adder = Par(Bool1(A),
                Bool2(B),
                Zeroes(Cin),
                fulladder(A, B, Cin, Sum, Carry),
                Sign(Carry, PCarry, 'Carry: '),
                Printer(PCarry),
                Sign(Sum, PSum, 'Sum: '),
                Printer(PSum))
    adder.start()

