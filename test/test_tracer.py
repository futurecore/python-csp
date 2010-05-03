#!/bin/env python

"""
Test the new python-csp tracer.
"""

from csp.cspprocess import *
from csp.guards import Skip

ch = Channel()


@process
def client(inchan):
    print inchan.read()


@process
def foo(outchan, msg):
    outchan.write(msg)


@process
def alt3(inchan1, inchan2, inchan3):
    alt = Alt(inchan1, inchan2, inchan3, Skip())
    selects = 0
    while selects < 3:
        val = alt.select()
        if val != 'Skip':
            selects += 1
        print val


@process
def simple():
    print 'SIMPLES'


@forever
def server():
    while True:
        print 'server process'
        yield


@forever
def server_write(outchan):
    while True:
        outchan.write('Hello server')
        yield


@forever
def server_read(inchan):
    while True:
        print inchan.read()
        yield


if __name__ == '__main__':
    import csp.tracer.tracer as tracer
    tracer.start_trace()
    chan = Channel()
    foo(chan, 'hello world!') & client(chan)
    Par(foo(chan, 1243), client(chan)).start()
    chan1, chan2, chan3 = Channel(), Channel(), Channel()
    Par(foo(chan1, 1),
        foo(chan2, 2),
        foo(chan3, 3),
        alt3(chan1, chan2, chan3)).start()
    simple().start()
    server().start()
    chan_s = Channel()
    server_read(chan_s) & server_write(chan_s)
    tracer.stop_trace()    
    
