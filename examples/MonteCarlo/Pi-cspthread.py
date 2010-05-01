#!/usr/bin/env python

from csp.cspthread import *
from math import sqrt
from decimal import Decimal

def genPair():
    return random.random(),random.random()

g = lambda x:  sqrt(1-(x*x))


perProcess = 100000

workers = 320

@process
def worker(c):
    count = 0
    i = 0
    while i < perProcess:
        x,y = genPair()
        if y<= g(x) :
            count = count + 1
        i += 1
    c.write((Decimal(count)))
    return

@process
def consumer(cins):     
    alt = Alt(*cins)
    total = Decimal(0)
    for i in range(len(cins)):
        t = alt.select()
        total += t
        
    print "Pi aproximation: " , Decimal((total/(perProcess*workers))*4)
        
def main():
    Chnls, procs = [],[]
    for i in range(workers):
        Chnls.append(Channel())
        procs.append(worker(Chnls[i]))
        
    procs.append(consumer(Chnls))
    p = Par(*procs)
    p.start()
    return 

if __name__ == '__main__':
    getcontext().prec = 19
    t0 = time.time()
    main()
    t1 = time.time()
    print "Time Taken: " , (t1-t0)
