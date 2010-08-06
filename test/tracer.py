#!/usr/bin/env python

"""
Test the new python-csp tracer.

Includes regular and server processes and ALTing.
"""

__author__ = 'Sarah Mount <s.mount@wlv.ac.uk>'
__date__ = 'May 2010'

import sys

sys.path.insert(0, "..")

from csp.csp import *
from csp.guards import Skip

ch = Channel()

@process
def client(inchan):
    """
    readset = inchan
    writeset =
    """
    print(inchan.read())
    return


@process
def foo(outchan, msg):
    """
    readset =
    writeset = outchan
    """
    outchan.write(msg)
    return


@process
def alt3(inchan1, inchan2, inchan3):
    """
    readset = inchan1, inchan2, inchan3
    writeset = 
    """
    alt = Alt(inchan1, inchan2, inchan3, Skip())
    selects = 0
    while selects < 3:
        val = alt.select()
        if val != 'Skip':
            selects += 1
        print(val)
    return


@process
def simple():
    print('SIMPLES')
    return


@forever
def server():
    while True:
        print('server process')
        yield
    return


@forever
def server_write(outchan):
    """
    readset =
    writeset = outchan
    """
    while True:
        outchan.write('Hello server')
        yield
    return


@forever
def server_read(inchan):
    """
    readset = inchan
    writeset =
    """
    while True:
        print(inchan.read())
        yield
    return


if __name__ == '__main__':
    from csp.tracer.tracer import csptrace
    with csptrace():
        chan, skip = Channel(), Skip()
        skip //= foo(chan, 'hello world!'), client(chan)
        Par(foo(chan, 1243), client(chan)).start()
        chan1, chan2, chan3 = Channel(), Channel(), Channel()
        Par(foo(chan1, 1),
            foo(chan2, 2),
            foo(chan3, 3),
            alt3(chan1, chan2, chan3)).start()
        simple().start()
        server().start()
        chan_s, skip = Channel(), Skip()
        skip //= server_read(chan_s), server_write(chan_s)
    
