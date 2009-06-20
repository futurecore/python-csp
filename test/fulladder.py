from csp.cspprocess import *

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

@process
def BOOL1(cout, _process=None):
    while True:
        cout.write(1)
        cout.write(1)
        cout.write(0)
        cout.write(0)
    return
        
@process
def BOOL2(cout, _process=None):
    while True:
        cout.write(1)
        cout.write(0)
        cout.write(1)
        cout.write(0)
    return

def fulladder(Ain, Bin, Cin, Sum, Carry):
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

    return PAR(DELTA2(Ain, Aa, Ab),
               DELTA2(Bin, Ba, Bb),
               DELTA2(Cin, Ca, Cb),
               DELTA2(i1, i1a, i1b),
               XOR(Aa, Ba, i1),
               XOR(i1a, Ca, Sum),
               AND(Ab, Bb, i2),
               AND(i1b, Cb, i3),
               OR(i2, i3, Carry))

if __name__ == '__main__':
    print '\nFull adder implemented in Python CSP\n'
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
    adder = PAR(BOOL1(A),
                BOOL2(B),
                ZEROES(Cin),
                fulladder(A, B, Cin, Sum, Carry),
                SIGN(Carry, PCarry, 'Carry: '),
                PRINTER(PCarry),
                SIGN(Sum, PSum, 'Sum: '),
                PRINTER(PSum))
    adder.start()

    
