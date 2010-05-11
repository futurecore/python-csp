#!/usr/bin/env python

from csp.cspprocess import Channel, Par, forever
from csp.builtins import Generate, Plus, Printer

in1, in2, out = Channel(), Channel(), Channel()  

@forever
def Msg(m):
    while True:
        print m
    return

Msg('a') & Msg('b') & Msg('c')

# Infinite stream of ints (OK)
#Generate(out) & Printer(out)

# Infinite stream of even ints (OK)
#Par(Generate(in1), Generate(in2), Plus(in1, in2, out), Printer(out)).start()

# Deadlock
#Generate(in1) & Generate(in2) & Plus(in1, in2, out) & Printer(out)  
