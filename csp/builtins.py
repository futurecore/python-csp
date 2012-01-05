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

from __future__ import absolute_import 

import math
import operator
import os
import sys

from .guards import Timer

from .csp import *

__author__ = 'Sarah Mount <s.mount@wlv.ac.uk>'
__date__ = 'May 2010'


# Names exported by this module.

__all__ = ['Sin', 'Cos', 'GenerateFloats',
           'Zeroes', 'Id', 'Succ', 'Pred', 'Prefix', 'Delta2', 'Splitter',
           'Mux2', 'Multiply', 'Clock', 'Printer', 'Pairs',
           'Mult', 'Generate', 'FixedDelay', 'Fibonacci',
           'Blackhole', 'Sign',
           # Processes based on Python operators
           'Plus', 'Sub', 'Mul', 'Div', 'FloorDiv', 'Mod',
           'Pow', 'LShift', 'RShift', 'Neg', 'Not', 'And',
           'Or', 'Nand', 'Nor', 'Xor', 'Land', 'Lor', 'Lnot',
           'Lnand', 'Lnor', 'Lxor', 'Eq', 'Ne', 'Geq', 'Leq',
           'Gt', 'Lt', 'Is', 'Is_Not']


@forever
def GenerateFloats(outchan, increment=0.1):
    """
    readset =
    writeset =    
    """
    counter = 0
    while True:
        outchan.write(counter * increment)
        counter += 1
        yield


@forever
def Zeroes(cout):
    """Writes out a stream of zeros.

    readset =
    writeset = cout
    """
    while True:
        cout.write(0)
        yield


@forever
def Id(cin, cout):
    """Id is the CSP equivalent of lambda x: x.

    readset = cin
    writeset = cout
    """
    while True:
        cout.write(cin.read())
        yield


@forever
def Succ(cin, cout):
    """Succ is the successor process, which writes out 1 + its input
    event.

    readset = cin
    writeset = cout
    """
    while True:
        cout.write(cin.read() + 1)
        yield


@forever
def Pred(cin, cout):
    """Pred is the predecessor process, which writes out 1 - its input
    event.

    readset = cin
    writeset = cout
    """
    while True:
        cout.write(cin.read() - 1)
        yield


@forever
def Prefix(cin, cout, prefix_item=None):
    """Prefix a write on L{cout} with the value read from L{cin}.

    readset = cin
    writeset = cout
    
    @type prefix_item: object
    @param prefix_item: prefix value to use before first item read from L{cin}.
    """
    pre = prefix_item
    while True:
        cout.write(pre)
        pre = cin.read()
        yield


@forever
def Splitter(cin, cout1, cout2):
    """Splitter sends input values down two output channels.

    readset = cin
    writeset = cout1, cout2
    """
    while True:
        val = cin.read()
        cout1.write(val)
        cout2.write(val)
        yield

Delta2 = Splitter


@forever
def Mux2(cin1, cin2, cout):
    """Mux2 provides a fair multiplex between two input channels.

    readset = cin1, cin2
    writeset = cout
    """
    while True:
        cout.write(cin1.read())
        cout.write(cin2.read())
        yield


@forever
def Clock(cout, resolution=1):
    """Send None object down output channel every C{resolution}
    seconds.

    readset =
    writeset = cout
    """
    timer = Timer()
    while True:
        timer.sleep(resolution)
        cout.write(None)
        yield


@forever
def Printer(cin, out=sys.stdout):
    """Print all values read from L{cin} to standard out or L{out}.

    readset = cin
    writeset =
    """
    while True:
        msg = str(cin.read()) + '\n'
        out.write(msg)
        yield


@forever
def Mult(cin, cout, scale):
    """Scale values read on L{cin} and write to L{cout}.

    readset = cin
    writeset = cout
    """
    while True:
        cout.write(cin.read() * scale)
        yield


@forever
def Generate(cout):
    """Generate successive (+ve) ints and write to L{cout}.

    readset = 
    writeset = cout
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

    readset = cin
    writeset = cout
    """
    timer = Timer()
    while True:
        in1 = cin.read()
        timer.sleep(delay)
        cout.write(in1)
        yield


@forever
def Fibonacci(cout):
    """Write successive Fibonacci numbers to L{cout}.

    readset =
    writeset = cout
    """
    a_int = b_int = 1
    while True:
        cout.write(a_int)
        a_int, b_int = b_int, a_int + b_int
        yield


@forever
def Blackhole(cin):
    """Read values from L{cin} and do nothing with them.

    readset = cin
    writeset = 
    """
    while True:
        cin.read()
        yield


@forever
def Sign(cin, cout, prefix):
    """Read values from L{cin} and write to L{cout}, prefixed by L{prefix}.

    readset = cin
    writeset = cout
    """
    while True:
        val = cin.read()
        cout.write(prefix + str(val))
        yield


### Magic for processes built on Python operators

def _applyunop(unaryop, docstring):
    """Create a process whose output is C{unaryop(cin.read())}.
    """

    chandoc = """
    readset = cin
    writeset = cout
    """

    @forever
    def _myproc(cin, cout):
        while True:
            in1 = cin.read()
            cout.write(unaryop(in1))
            yield
    _myproc.__doc__ = docstring + chandoc
    return _myproc


def _applybinop(binop, docstring):
    """Create a process whose output is C{binop(cin1.read(), cin2.read())}.
    """

    chandoc = """
    readset = cin1, cin2
    writeset = cout
    """

    @forever
    def _myproc(cin1, cin2, cout):
        while True:
            in1 = cin1.read()
            in2 = cin2.read()
            cout.write(binop(in1, in2))
            yield
    _myproc.__doc__ = docstring + chandoc
    return _myproc


# Use some abbreviations to shorten definitions.
unop = _applyunop
binop = _applybinop
op = operator

# Numeric operators

Plus = binop(op.add, "Emits the sum of two input events.")
Sub = binop(op.sub, "Emits the difference of two input events.")
Mul = binop(op.mul, "Emits the product of two input events.")
Div = binop(op.truediv, "Emits the division of two input events.")
FloorDiv = binop(op.floordiv, "Emits the floor div of two input events.")
Mod = binop(op.mod, "Emits the modulo of two input events.")
Pow = binop(op.pow, "Emits the power of two input events.")
Neg = unop(op.neg, "Emits the negation of input events.")
Sin = unop(math.sin, "Emit the sine of input events.")
Cos = unop(math.cos, "Emit the cosine of input events.")

Pairs = Plus
Multiply = Mul

# Bitwise operators

Not = unop(op.invert, "Emits the inverse of input events.")
And = binop(op.and_, "Emits the bitwise and of two input events.")
Or = binop(op.or_, "Emits the bitwise or of two input events.")
Nand = binop(lambda x, y: ~(x & y),
             "Emits the bitwise nand of two input events.")
Nor = binop(lambda x, y: ~(x | y), "Emits the bitwise nor of two input events.")
Xor = binop(op.xor, "Emits the bitwise xor of two input events.")
LShift = binop(op.lshift, "Emits the left shift of two input events.")
RShift = binop(op.rshift, "Emits the right shift of two input events.")

# Logical operators

Land = binop(lambda x, y: x and y, "Emits the logical and of two input events.")
Lor = binop(lambda x, y: x or y, "Emits the logical or of two input events.")
Lnot = unop(op.not_, "Emits the logical not of input events.")
Lnand = binop(lambda x, y: not (x and y),
              "Emits the logical nand of two input events.")
Lnor = binop(lambda x, y: not (x or y),
             "Emits the logical nor of two input events.")
Lxor = binop(lambda x, y: (x or y) and (not x and y),
             "Emits the logical xor of two input events.")

# Comparison operators

Eq = binop(op.eq,"Emits True if two input events are equal (==).")
Ne = binop(op.ne, "Emits True if two input events are not equal (not ==).")
Geq = binop(op.ge, "Emits True if first input event is >= second.")
Leq = binop(op.le, "Emits True if first input event is <= second.")
Gt = binop(op.gt, "Emits True if first input event is > second.")
Lt = binop(op.lt, "Emits True if first input event is < second.")
Is = binop(op.is_, "Emits True if two input events are identical.")
Is_Not = binop(op.is_not, "Emits True if two input events are not identical.")

del unop, binop, op

