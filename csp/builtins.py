#!/usr/bin/env python

"""Builtin processes for python-csp. For guard types see csp.guards.

Based on the JCSP PlugNPlay package.

Copyright (C) Sarah Mount, 2009.

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


import operator
import os

if os.environ.has_key('CSP'):
    if os.environ['CSP'] == 'PROCESSES':
        from csp.cspprocess import *
    elif os.environ['CSP'] == 'THREADS':
        from csp.cspthread import *
    else:
        from csp.cspprocess import *   
else:
    from csp.cspprocess import *   

del os

# PlugNPlay guards and processes

@forever
def Zeroes(cout):
    """Writes out a stream of zeroes."""
    while True:
        cout.write(0)
        yield


@forever
def Id(cin, cout):
    """Id is the CSP equivalent of lambda x: x.
    """
    while True:
        cout.write(cin.read())
        yield


@forever
def Succ(cin, cout):
    """Succ is the successor process, which writes out 1 + its input event.
    """
    while True:
        cout.write(cin.read() + 1)
        yield


@forever
def Pred(cin, cout):
    """Pred is the predecessor process, which writes out 1 - its input event.
    """
    while True:
        cout.write(cin.read() - 1)
        yield


@forever
def Prefix(cin, cout, prefix_item=None):
    """Prefix a write on L{cout} with the value read from L{cin}.

    @type prefix_item: object
    @param prefix_item: prefix value to use before first item read from L{cin}.
    """
    pre = prefix_item
    while True:
        cout.write(pre)
        pre = cin.read()
        yield


@forever
def Delta2(cin, cout1, cout2):
    """Delta2 sends input values down two output channels.
    """
    while True:
        val = cin.read()
        cout1.write(val)
        cout2.write(val)
        yield


@forever
def Mux2(cin1, cin2, cout):
    """Mux2 provides a fair multiplex between two input channels.
    """
#    alt = Alt(cin1, cin2)
    while True:
        cout.write(cin1.read())
        cout.write(cin2.read())
#        cout.write(alt.pri_select())
        yield


@forever
def Multiply(cin0, cin1, cout0):
    
    while True:
        cout0.write(cin0.read() * cin1.read())
        yield


@forever
def Clock(cout, resolution=1):
    """Send None object down output channel every C{resolution} seconds.
    """
    from csp.guards import Timer
    timer = Timer()
    while True:
        timer.sleep(resolution)
        cout.write(None)
        yield


@forever
def Printer(cin, out=sys.stdout):
    """Print all values read from L{cin} to standard out or L{out}.
    """
    while True:
        msg = str(cin.read()) + '\n'
        out.write(msg)
        yield


@forever
def Pairs(cin1, cin2, cout):
    """Read values from L{cin1} and L{cin2} and write their addition
    to L{cout}.
    """
    while True:
        in1 = cin1.read()
        in2 = cin2.read()
        cout.write(in1 + in2)
        yield


@forever
def Mult(cin, cout, scale):
    """Scale values read on L{cin} and write to L{cout}.
    """
    while True:
        cout.write(cin.read() * scale)
        yield


@forever
def Generate(cout):
    """Generate successive (+ve) ints and write to L{cout}.
    """
    counter = 0
    while True:
        cout.write(counter)
        counter += 1
        yield


@forever
def FixedDelay(cin, cout, delay):
    """Read values from L{cin} and write to L{cout} after a delay of
    L{delay} seconds.
    """
    while True:
        in1 = cin.read()
        time.sleep(delay)
        cout.write(in1)
        yield


@forever
def Fibonacci(cout):
    """Write successive Fibonacci numbers to L{cout}.
    """
    a_int = b_int = 1
    while True:
        cout.write(a_int)
        a_int, b_int = b_int, a_int + b_int
        yield


@forever
def Blackhole(cin):
    """Read values from L{cin} and do nothing with them.
    """
    while True:
        cin.read()
        yield


@forever
def Sign(cin, cout, prefix):
    """Read values from L{cin} and write to L{cout}, prefixed by L{prefix}.
    """
    while True:
        val = cin.read()
        cout.write(prefix + str(val))
        yield


### Magic for processes built on Python operators

def _applyunop(unaryop, docstring):
    """Create a process whose output is C{unaryop(cin.read())}.
    """

    @forever
    def _myproc(cin, cout):
        while True:
            in1 = cin.read()
            cout.write(unaryop(in1))
            yield
    _myproc.__doc__ = docstring
    return _myproc


def _applybinop(binop, docstring):
    """Create a process whose output is C{binop(cin1.read(), cin2.read())}.
    """

    @forever
    def _myproc(cin1, cin2, cout):
        while True:
            in1 = cin1.read()
            in2 = cin2.read()
            cout.write(binop(in1, in2))
            yield
    _myproc.__doc__ = docstring
    return _myproc

# Numeric operators

Plus = _applybinop(operator.__add__,
                   """Writes out the addition of two input events.
""")

Sub = _applybinop(operator.__sub__,
                  """Writes out the subtraction of two input events.
""")

Mul = _applybinop(operator.__mul__,
                  """Writes out the multiplication of two input events.
""")

Div = _applybinop(operator.__div__,
                  """Writes out the division of two input events.
""")


FloorDiv = _applybinop(operator.__floordiv__,
                       """Writes out the floor div of two input events.
""")

Mod = _applybinop(operator.__mod__,
                  """Writes out the modulo of two input events.
""")

Pow = _applybinop(operator.__pow__,
                  """Writes out the power of two input events.
""")

LShift = _applybinop(operator.__lshift__,
                     """Writes out the left shift of two input events.
""")

RShift = _applybinop(operator.__rshift__,
                     """Writes out the right shift of two input events.
""")

Neg = _applyunop(operator.__neg__,
                 """Writes out the negation of input events.
""")

# Bitwise operators

Not = _applyunop(operator.__inv__,
                 """Writes out the inverse of input events.
""")

And = _applybinop(operator.__and__,
                  """Writes out the bitwise and of two input events.
""")

Or = _applybinop(operator.__or__,
                 """Writes out the bitwise or of two input events.
""")

Nand = _applybinop(lambda x, y: ~ (x & y),
                   """Writes out the bitwise nand of two input events.
""")

Nor = _applybinop(lambda x, y: ~ (x | y),
                  """Writes out the bitwise nor of two input events.
""")

Xor = _applybinop(operator.xor,
                  """Writes out the bitwise xor of two input events.
""")

# Logical operators

Land = _applybinop(lambda x, y: x and y,
                   """Writes out the logical and of two input events.
""")

Lor = _applybinop(lambda x, y: x or y,
                  """Writes out the logical or of two input events.
""")

Lnot = _applyunop(operator.__not__,
                  """Writes out the logical not of input events.
""")

Lnand = _applybinop(lambda x, y: not (x and y),
                    """Writes out the logical nand of two input events.
""")

Lnor = _applybinop(lambda x, y: not (x or y),
                   """Writes out the logical nor of two input events.
""")

Lxor = _applybinop(lambda x, y: (x or y) and (not x and y),
                   """Writes out the logical xor of two input events.
""")

# Comparison operators

Eq = _applybinop(operator.__eq__,
                 """Writes True if two input events are equal (==).
""")

Ne = _applybinop(operator.__ne__,
                   """Writes True if two input events are not equal (not ==).
""")

Geq = _applybinop(operator.__ge__,
                   """Writes True if 'right' input event is >= 'left'.
""")

Leq = _applybinop(operator.__le__,
                   """Writes True if 'right' input event is <= 'left'.
""")

Gt = _applybinop(operator.__gt__,
                   """Writes True if 'right' input event is > 'left'.
""")

Lt = _applybinop(operator.__lt__,
                   """Writes True if 'right' input event is < 'left'.
""")

Is = _applybinop(lambda x, y: x is y,
                 """Writes True if two input events are the same (is).
""")

Is_Not = _applybinop(lambda x, y: not (x is y),
                   """Writes True if two input events are not the same (is).
""")
