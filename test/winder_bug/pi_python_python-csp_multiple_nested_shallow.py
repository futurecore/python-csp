#! /usr/bin/env python
# -*- mode:python; coding:utf-8; -*-

#  Calculation of Pi using quadrature.  Using the python-csp package by Sarah Mount.
#
#  Copyright © 2009-10 Russel Winder

import time
import multiprocessing

from csp.cspprocess import *

def execute ( processCount ) :
    n = 100000000 # 100 times fewer due to speed issues.
    delta = 1.0 / n
    startTime = time.time ( )
    sliceSize = n / processCount
    channels = [ ]
    @process
    def calculator ( channel , id , _process = None ) :
        sum = 0.0
        for i in xrange ( 1 + id * sliceSize ,  ( id + 1 ) * sliceSize + 1 ) :
            x = ( i - 0.5 ) * delta
            sum += 1.0 / ( 1.0 + x * x )
        channel.write ( sum )
    @process
    def accumulator ( _process = None ) :
        pi = 4.0 * sum ( [ channel.read ( ) for channel in channels ] ) * delta
        elapseTime = time.time ( ) - startTime
        print "==== Python CSP Multiple NestedShallow pi =" , pi
        print "==== Python CSP Multiple NestedShallow iteration count =", n
        print "==== Python CSP Multiple NestedShallow elapse =" , elapseTime
        print "==== Python CSP Multiple NestedShallow process count = ", processCount
        print "==== Python CSP Multiple NestedShallow processor count =" , multiprocessing.cpu_count ( )
    processes = [ ] 
    for i in range ( 0 , processCount ) :
        channel = Channel ( )
        channels.append ( channel )
        processes.append ( calculator ( channel , i ) )
    processes.append ( accumulator ( ) )
    Par ( *processes ).start ( )

if __name__ == '__main__' :
#    import csp.tracer
#    csp.tracer.start_trace()
#    import gc
#    gc.collect()
#    print 'GC Count:', gc.get_count()
    execute ( 1 )
    print
#    gc.collect()
#    print 'GC Count:', gc.get_count()
    execute ( 2 )
    print
#    gc.collect()
#    print 'GC Count:', gc.get_count()
    execute ( 8 )
    print
#    gc.collect()
#    print 'GC Count:', gc.get_count()
    execute ( 32 )
#    csp.tracer.stop_trace()
