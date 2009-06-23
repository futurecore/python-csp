#!/usr/bin/env jython
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

from Jycspthread import *
import os

@process
def Consumer(cin, _process=None):
    "Commstime consumer process"
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
    print "DT = %f.\nTime per ch : %f/(4*%d) = %f s = %f us" % \
          (dt, dt, N, tchan, tchan * 1000000)
    print "consumer done, posioning channel"
    cin.poison()

def CommsTimeBM():
    print 'Creating channels now...'
    # Create channels
    a = Channel()
    b = Channel()
    c = Channel()
    d = Channel()
    print "Running commstime test"
    p = Par(Prefix(c, a, prefix_item = 0),  	# initiator
            Delta2(a, b, d),         		# forwarding to two
            Succ(b, c),                    	# feeding back to prefix
            Consumer(d))            		# timing process
    p.start()
    print 'Finished run...'
    
### PyCSP code:
#    PAR(PREFIX(c.read, a.write, prefixItem = 0),  # initiator
#        DELTA2(a.read, b.write, d.write),         # forwarding to two
#        SUCC(b.read, c.write),                    # feeding back to prefix
#        Consumer(d.read)).start()                 # timing process
    

if __name__ == '__main__':
    N_BM = 10
    for i in xrange(N_BM):
        print "----------- run %d/%d -------------" % (i+1, N_BM)
        CommsTimeBM()
        time.sleep(5) # Wait for each run to finish...
    print "------- Commstime finished ---------"

#    # A bit of a hack, but windows does not have uname()
#    try:
#        os.uname()
#    except:
#        print "Sleeping for a while to allow windows users to read benchmark results"
#        time.sleep(15)
