#!/usr/bin/env python

from csp.cspprocess import Channel, Par
from csp.builtins import Generate, Plus, Printer

in1, in2, out = Channel(), Channel(), Channel()  

# Infinite stream of even ints
# Par(Generate(in1), Generate(in2), Plus(in1, in2, out), Printer(out)).start()

# Deadlock
Generate(in1) & Generate(in2) & Plus(in1, in2, out) & Printer(out)  
