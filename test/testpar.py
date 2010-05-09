#!/usr/bin/env python

from csp.cspprocess import Channel
from csp.builtins import Generate, Plus, Printer

in1, in2, out = Channel(), Channel(), Channel()  
Generate(in1) & Generate(in2) & CSPServer(Plus, in1, in2, out) & Printer(out)  
