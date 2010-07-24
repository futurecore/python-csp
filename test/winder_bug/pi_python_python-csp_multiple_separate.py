#!/usr/bin/env python
# -*- mode:python; coding:utf-8; -*-

#  Calculation of Pi using quadrature.  Using the python-csp package by Sarah Mount.
#
#  Copyright © 2009-10 Russel Winder

import time
import multiprocessing

import sys
sys.path.insert(0, "../..")

from csp.csp import *

@process
def calculator ( channel , id , sliceSize , delta ) :
    """
    readset =
    writeset = channel
    """
    sum = 0.0
    for i in range ( 1 + id * sliceSize , ( id + 1 ) * sliceSize + 1 ) :
        x = ( i - 0.5 ) * delta
        sum += 1.0 / ( 1.0 + x * x )
    channel.write ( sum )
        
@process
def accumulator ( channels , n , delta , startTime , processCount ) :
    """
    readset = channels
    writeset =
    """
    pi = 4.0 * sum ( [ channel.read ( ) for channel in channels ] ) * delta
    elapseTime = time.time ( ) - startTime
    print ( "==== Python CSP Multiple pi = " + str ( pi ) )
    print ( "==== Python CSP Multiple iteration count = " + str ( n ) )
    print ( "==== Python CSP Multiple elapse = " + str ( elapseTime ) )
    print ( "==== Python CSP Multiple process count = " + str ( processCount ) )
    print ( "==== Python CSP Multiple processor count = " + str ( multiprocessing.cpu_count ( ) ) )

def execute ( processCount ) :
    n = 100000000 # 10 times fewer due to speed issues.
    delta = 1.0 / n
    startTime = time.time ( )
    sliceSize = n / processCount
    channels = [ ]
    processes = [ ] 
    for i in range ( 0 , processCount ) : 
        channel = Channel ( )
        channels.append ( channel )
        processes.append ( calculator ( channel , i , sliceSize , delta ) )
    processes.append ( accumulator ( channels , n , delta , startTime , processCount ) )
    Par ( *processes ).start ( )

if __name__ == '__main__' :
    execute ( 1 )
    print ( )
    execute ( 2 )
    print ( )
    execute ( 8 )
    print ( )
    execute ( 32 )
