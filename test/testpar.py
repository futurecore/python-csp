#!/usr/bin/env python

from csp.cspprocess import * 
from csp.builtins import Generate, Plus, Printer

in1, in2, out = Channel(), Channel(), Channel()  

@forever
def Msg(m):
    while True:
        print m
    return

@process
def foo():
    # Previously deadlocked
    Par.Skip //= Generate(in1), Generate(in2), Plus(in1, in2, out), Printer(out)

#(Msg('aaaaa') & Msg('b') & Msg('***'))

# Infinite stream of ints (OK)
#p //= [Generate(out), Printer(out)]

@process
def bar():
    # Infinite stream of even ints (OK)
    Par(Generate(in1), Generate(in2), Plus(in1, in2, out), Printer(out)).start()


#PAR //= [Generate(in1), Generate(in2), Plus(in1, in2, out), Printer(out)]

if __name__ == '__main__':
    print globals()
    bar().start()
    foo().start()
