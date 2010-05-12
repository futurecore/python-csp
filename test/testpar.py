#!/usr/bin/env python

from csp.cspprocess import * 
from csp.builtins import Generate, Plus, Printer

in1, in2, out = Channel(), Channel(), Channel()  

def foo():
    # Previously deadlocked
    Unit = Skip()
    Unit //= Generate(in1), Generate(in2), Plus(in1, in2, out), Printer(out)


# Infinite stream of ints (OK)
#p = Skip()
#p //= [Generate(out), Printer(out)]

@process
def bar():
    # Infinite stream of even ints (OK)
    Par(Generate(in1), Generate(in2), Plus(in1, in2, out), Printer(out)).start()


#PAR //= [Generate(in1), Generate(in2), Plus(in1, in2, out), Printer(out)]

if __name__ == '__main__':
#    Unit = Skip()
#    Unit //= Generate(in1), Generate(in2), Plus(in1, in2, out), Printer(out)
#
#    bar().start()
    foo().start()
