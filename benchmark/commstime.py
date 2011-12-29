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

# pylint: disable-msg=W0401
# pylint: disable-msg=W0614

import sys
import time

sys.path.insert(0, "..")

#from csp.csp import *
from csp.os_process import *
#from csp.os_posix import *
#from csp.os_thread import *

from csp.builtins import Prefix, Delta2, Succ

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
    for _ in range(N):
        cin.read()
    t2 = ts()
    dt = t2-t1
    tchan = dt / (4 * N)
    print("DT = {0}.\nTime per ch : {1}/(4*{2}) = {3} s = {4} us".format(dt, dt, N, tchan, tchan * 1000000))
    print("consumer done, posioning channel")
    cin.poison()

def CommsTimeBM():
    print('Creating channels now...')
    # Create channels
    a = Channel()
    b = Channel()
    c = Channel()
    d = Channel()
    print("Running commstime test")
    Par(Prefix(c, a, prefix_item = 0),  	# Initiator
		Delta2(a, b, d),         	# Forwarding to two
		Succ(b, c),                    	# Feeding back to prefix
		Consumer(d)).start()      	# Timing process
    print('Finished run...')
    

if __name__ == '__main__':
    N_BM = 10
    for i in range(N_BM):
        print("----------- run {0}/{1} -------------".format(i+1, N_BM))
        CommsTimeBM()
    print("------- Commstime finished ---------")
