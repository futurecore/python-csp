#!/usr/bin/env python
"""CSP Commstime benchmark.

See F.R.M. Barnes (2006) Compiling CSP. In Proceedings of
Communicating Process Architectures 2006.

Code adapted from PyCSP by John Markus Bjorndalen, available:
http://www.cs.uit.no/~johnm/code/PyCSP/

PyCSP - Communicating Sequential Processes for Python.  John Markus
Bjorndalen, Brian Vinter, Otto Anshus.  CPA 2007, Surrey, UK, July
8-11, 2007.  IOS Press 2007, ISBN 978-1-58603-767-3, Concurrent
Systems Engineering Series (ISSN 1383-7575).
"""

from csp.csp import Par, process #, Channel
from csp.builtins import Prefix, Delta2, Succ

import sys
sys.path.append('../')
from CChannel import CChannel as Channel
del sys

import time


@process
def Consumer(cin):
    """Commstime consumer process

    readset = cin
    writeset =
    """
    N = 5000
    ts = time.time
    t1 = ts()
    cin.read()
    t1 = ts()
    for i in range(N):
        cin.read()
    t2 = ts()
    dt = t2-t1
    tchan = dt / (4 * N)
    print("DT = {0}\nTime per ch : {1}/(4*{2}) = {3} s = {4} us".format(dt, dt, N, tchan, tchan * 1000000))
    print("consumer done, poisoning channel")
    cin.poison()

def CommsTimeBM():
    print('Creating channels now...')
    # Create channels
    a = Channel()
    b = Channel()
    c = Channel()
    d = Channel()
    print("Running commstime test")
    Par(Prefix(c, a, prefix_item=0),  # Initiator
        Delta2(a, b, d),              # Forwarding to two
        Succ(b, c),                   # Feeding back to prefix
        Consumer(d)).start()          # Timing process
    print('Finished run...')


if __name__ == '__main__':
    N_BM = 10
    for i in xrange(N_BM):
        print("----------- run {0}/{1} -------------".format(i+1, N_BM))
        CommsTimeBM()
    print("------- Commstime finished ---------")
