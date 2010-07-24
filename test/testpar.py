#!/usr/bin/env python

import sys

sys.path.insert(0, "..")

from csp.csp import * 
from csp.builtins import Generate, Plus, Printer

in1, in2, out = Channel(), Channel(), Channel()  

@process
def foo():
    # Previously deadlocked
    Skip() // (Generate(in1), Generate(in2), Plus(in1, in2, out), Printer(out))


# Infinite stream of ints (OK)
#p = Skip()
#p //= [Generate(out), Printer(out)]

@process
def bar():
    # Infinite stream of even ints (OK)
    Par(Generate(in1), Generate(in2), Plus(in1, in2, out), Printer(out)).start()


#PAR //= [Generate(in1), Generate(in2), Plus(in1, in2, out), Printer(out)]

if __name__ == '__main__':
    Generate(out) // (Printer(out),)
#
#    bar().start()
#    foo().start()
