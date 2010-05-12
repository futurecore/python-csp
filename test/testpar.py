#!/usr/bin/env python

from csp.cspprocess import * 
from csp.builtins import Generate, Plus, Printer

in1, in2, out = Channel(), Channel(), Channel()  

@forever
def Msg(m):
    while True:
        print m
    return


def foo():
    # Previously deadlocked
    Unit //= Generate(in1), Generate(in2), Plus(in1, in2, out), Printer(out)

#(Msg('aaaaa') & Msg('b') & Msg('***'))

# Infinite stream of ints (OK)
#p //= [Generate(out), Printer(out)]

# Infinite stream of even ints (OK)
#Par(Generate(in1), Generate(in2), Plus(in1, in2, out), Printer(out)).start()


#PAR //= [Generate(in1), Generate(in2), Plus(in1, in2, out), Printer(out)]

if __name__ == '__main__':
    foo()
