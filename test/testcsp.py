#!/usr/bin/env python

"""
Simple tests for basic python-csp functionality.

Copyright (C) Sarah Mount, 2009.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have rceeived a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
"""

import os
import random
import sys
import time

sys.path.insert(0, "..")

from csp.csp import *
#from csp.os_process import *
#from csp.os_thread import *
from csp.guards import Timer
#set_debug(True)

@process
def foo(n):
    time.sleep(random.random()*2)
    print('foo() got argument {0}'.format(n))
    return


@process
def send(cout):
    """
    readset =
    writeset = cout
    """
    for i in range(5):
        print('send() is sending {0}'.format(i))
        cout.write(i)
    return


@process
def recv(cin):
    """
    readset = cin
    writeset =
    """
    for i in range(5):
        data = cin.read()
        print('recv() has received {0}'.format(str(data)))
    return


@process
def send100(cout):
    """
    readset =
    writeset = cout
    """
    for i in range(100):
        print('send100() is sending {0}'.format(i))
        cout.write(i)
    return


@process
def recv100(cin):
    """
    readset = cin
    writeset =
    """
    for i in range(100):
        data = cin.read()
        print('recv100() has received {0}'.format(str(data)))
    return


class TestOOP(object):
    
    def __init__(self):
        self.chan = Channel()
        return

    @process
    def send(self, msg):
        """
        readset = self.chan
        writeset =
        """
        self.chan.write(msg)
        return

    @process
    def recv(self):
        """
        readset = self.chan
        writeset =
        """
        print(self.chan.read())
        return


def testoop():
    f = TestOOP()
    Par(f.send('hello world'), f.recv()).start()
    return


@process
def testpoison(chan):
    print('Sending termination event...')
    chan.poison()
    return


@process
def sendAlt(cout, num):
    """
    readset =
    writeset = cout
    """
    t = Timer()
    t.sleep(1)
    cout.write(num)
    return


@process
def testAlt0():
    alt = Alt(Skip(), Skip(), Skip())
    for i in range(3):
        print('*** TestAlt0 selecting...')
        val = alt.select()
        print('* Got this from Alt:' + str(val))
    return


@process
def testAlt1(cin):
    """
    readset = cin
    writeset =
    """
    alt = Alt(cin)
    numeric = 0 
    while numeric < 1:
        print('*** TestAlt1 selecting...')
        val = alt.select()
        if isinstance(val, int): numeric += 1 
        print('* Got this from Alt:' + str(val))
    return


@process
def testAlt2(cin1, cin2, cin3):
    """
    readset = cin1, cin2, cin3
    writeset =
    """
    alt = Alt(Skip(), cin1, cin2, cin3)
    numeric = 0 
    while numeric < 3:
        print('*** TestAlt2 selecting...')
        val = alt.select()
        if isinstance(val, int): numeric +=1
        print('* Got this from Alt:' + str(val))
    return


@process
def testAlt3(cin1, cin2, cin3):
    """
    readset = cin1, cin2, cin3
    writeset =
    """
    # For obvious reasons, SKIP cannot go first 
    alt = Alt(cin1, cin2, cin3, Skip())
    numeric = 0
    while numeric < 3:
        print('*** TestAlt3 selecting...')        
        val = alt.pri_select()
        if isinstance(val, int): numeric +=1
        print('* Got this from Alt:' + str(val))
    return


@process
def testAlt4(cin1, cin2, cin3):
    """
    readset = cin1, cin2, cin3
    writeset =
    """
    alt = Alt(Skip(), cin1, cin2, cin3)
    numeric = 0
    while numeric < 3:
        print('*** TestAlt4 selecting...')        
        val = alt.fair_select()
        if isinstance(val, int): numeric +=1
        print('* Got this from Alt:' + str(val))
    return


@process
def testOr(cin1, cin2):
    """
    readset = cin1, cin2
    writeset =
    """
    print(cin1 | cin2)
    print(cin1 | cin2)
    return


@process
def testAltRRep(cin1, cin2, cin3):
    """
    readset = cin1, cin2, cin3
    writeset =
    """
    gen = Alt(cin1, cin2, cin3) * 3
    print(next(gen))
    print(next(gen))
    print(next(gen))
    return


@process
def testAltLRep(cin1, cin2, cin3):
    """
    readset = cin1, cin2, cin3
    writeset =
    """
    gen = 3 * Alt(cin1, cin2, cin3)
    print(next(gen))
    print(next(gen))
    print(next(gen))
    return


########## Top level stuff

def _printHeader(name):
    random.seed(time.clock()) # Introduce a bit more randomness...    
    print('')
    print('****************************************************')
    print('* Testing {0}...'.format(name))
    print('****************************************************')
    print('')
    return


def testSeq():
    _printHeader('Seq')
    print('With operator overloading...')
    foo(1) > foo(2) > foo(3)
    print('')
    print('With process objects...')
    Seq(foo(1), foo(2), foo(3)).start()
    return


def testPar():
    _printHeader('Par')
    print('5 processes with operator overloading...')
    foo(1) // (foo(2), foo(3), foo(4), foo(5))
    print('')
    print('8 processes with operator overloading...')
    foo(1) // (foo(2), foo(3), foo(4), foo(5), foo(6), foo(7), foo(8))
    print('')
    print('5 processes with process objects...')
    Par(foo(1), foo(2), foo(3), foo(4), foo(5)).start()
    return


def testChan():
    _printHeader('Channels')
    print('1 producer, 1 consumer, 1 channel...')
    c1 = Channel()
    p = Par(recv(c1), send(c1))
    p.start()
    print('')
    print('5 producers, 5 consumers, 5 channels...')
    chans = [Channel() for i in range(5)]
    p = [send(chan) for chan in chans] + [recv(chan) for chan in chans]
    pp = Par(*p)
    pp.start()
    print('')
    print('5 producers, 5 consumers, 1 channel...')
    chan = Channel()
    p = [send(chan) for i in range(5)] + [recv(chan) for i in range(5)]
    pp = Par(*p)
    pp.start()
    return


def testOOP():
    _printHeader('channel read/write using object methods...')
    testoop()
    return


def testPoison():
    _printHeader('process termination (by poisoning)')
    chanp = Channel()
    Par(send100(chanp), recv100(chanp), testpoison(chanp)).start()
    return


def testAlt():
    _printHeader('Alt')
    print('Alt with 3 SKIPs:')
    ta0 = testAlt0()
    ta0.start()
    print('')
    print('Alt with 1 channel read:')
    ch1 = Channel()
    Par(testAlt1(ch1), sendAlt(ch1, 100)).start()
    print('')
    print('Alt with 1 SKIP, 3 channel reads:')
    ch2, ch3, ch4 = Channel(), Channel(), Channel()
    Par(testAlt2(ch2, ch3, ch4),
		sendAlt(ch2, 100),
		sendAlt(ch3, 200),
		sendAlt(ch4, 300)).start()
    print('')
    print('Alt with priSelect on 1 SKIP, 3 channel reads:')
    ch5, ch6, ch7 = Channel(), Channel(), Channel()
    ta3 = Par(testAlt3(ch5, ch6, ch7),
              sendAlt(ch5, 100),
              sendAlt(ch6, 200),
              sendAlt(ch7, 300))
    ta3.start()
    print('')
    print('Alt with fairSelect on 1 SKIP, 3 channel reads:')
    ch8, ch9, ch10 = Channel(), Channel(), Channel()
    Par(testAlt4(ch8, ch9, ch10),
		sendAlt(ch8, 100),
		sendAlt(ch9, 200),
		sendAlt(ch10, 300)).start()
    return


def testChoice():
    _printHeader('Choice')
    print('Choice with |:')
    c1, c2 = Channel(), Channel()
    Par(sendAlt(c1, 100), sendAlt(c2, 200), testOr(c1, c2)).start()
    return


def testRep():
    _printHeader('Repetition')
    print('Repetition with Alt * int:')
    ch1, ch2, ch3 = Channel(), Channel(), Channel()
    Par(sendAlt(ch1, 100), sendAlt(ch2, 200), sendAlt(ch3, 300),
        testAltRRep(ch1, ch2, ch3)).start()
    print('')
    print('Repetition with Alt * int:')
    ch1, ch2, ch3 = Channel(), Channel(), Channel()
    Par(sendAlt(ch1, 100), sendAlt(ch2, 200), sendAlt(ch3, 300),
        testAltLRep(ch1, ch2, ch3)).start()
    return


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()

    parser.add_option('-a', '--all', dest='all', 
                      action='store_true',
                      help='Test all CSP features')    
    parser.add_option('-s', '--seq', dest='seq', 
                      action='store_true',
                      help='Test Seq')
    parser.add_option('-p', '--par', dest='par', 
                      action='store_true',
                      help='Test Par')
    parser.add_option('-c', '--chan', dest='chan', 
                      action='store_true',
                      help='Test Channels')
    parser.add_option('-o', '--oop', dest='oop',
                      action='store_true',
                      help='Test OOP')
    parser.add_option('-t', '--poison', dest='term', 
                      action='store_true',
                      help='Test process termination')
    parser.add_option('-l', '--alt', dest='alt', 
                      action='store_true',
                      help='Test Alternatives')
    parser.add_option('-i', '--choice', dest='choice',
                      action='store_true',
                      help='Test syntactic sugar for choice.')
    parser.add_option('-r', '--rep', dest='rep',
                      action='store_true',
                      help='Test syntactic sugar for repetition.')

    (options, args) = parser.parse_args()

#    _exit = '\nPress Ctrl-c to terminate CSP channel server.'
    _exit = '\nTesting complete.'
    
    if options.all:
        testSeq()
        testPar()
        testChan()
        testOOP()
        testPoison()
        testAlt()
        testChoice()
        testRep()
        print(_exit)
        sys.exit()
    elif options.seq: testSeq()
    elif options.par: testPar()
    elif options.chan: testChan()
    elif options.oop: testOOP()
    elif options.term: testPoison()
    elif options.alt: testAlt()
    elif options.choice: testChoice()
    elif options.rep: testRep()
    else: parser.print_help()
    print(_exit)
    sys.exit()
