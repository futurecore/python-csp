#!/usr/bin/env python

from csp.cspprocess import *

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

@process
def foo(n, _process=None):
    time.sleep(random.random()*5)
    print '%s in PID %g has arg %g' % (_process.getName(), _process.getPid(), n)
    return


@process
def send(cout, _process=None):
    for i in xrange(5):
        print '%s PID: %s sending %g' % (_process.getName(),
                                         _process.getPid(), 
                                         i)
        cout.write(i)
    return


@process
def recv(cin, _process=None):
    for i in xrange(5):
        data = cin.read()
        print '%s PID: %s received %s' % (_process.getName(),
                                          _process.getPid(),
                                          data)
    return


@process
def send100(cout, _process=None):
    for i in xrange(100):
        print '%s PID: %s sending %g' % (_process.getName(),
                                         _process.getPid(), 
                                         i)
        cout.write(i)
    return


@process
def recv100(cin, _process=None):
    for i in xrange(100):
        data = cin.read()
        print '%s PID: %s received %s' % (_process.getName(),
                                          _process.getPid(),
                                          data)
    return


class TestOOP(object):
    
    def __init__(self):
        self.chan = Channel()

    @process
    def send(self, msg, _process=None):
        self.chan.write(msg)

    @process
    def recv(self, _process=None):
        print self.chan.read()


def testoop():
    f = TestOOP()
    Par(f.send('hello world'), f.recv()).start()


@process
def testpoison(chan, _process=None):
    print 'Sending termination event...'
    chan.poison()    


@process
def sendAlt(cout, num, _process=None):
    cout.write(num)
    return

@process
def testAlt0(_process=None):
    alt = Alt(Skip(), Skip(), Skip())
    for i in range(3):
        print '*** TestAlt0 selecting...'
        val = alt.select()
        print '* Got this from Alt:', val


@process
def testAlt1(cin, _process=None):
    alt = Alt(cin)
    numeric = 0 
    while numeric < 1:
        print '*** TestAlt1 selecting...'
        val = alt.select()
        if isinstance(recv, int): numeric += 1 
        print '* Got this from Alt:', val


@process
def testAlt2(cin1, cin2, cin3, _process=None):
    alt = Alt(Skip(), cin1, cin2, cin3)
    numeric = 0 
    while numeric < 3:
        print '*** TestAlt2 selecting...'
        val = alt.select()
        if isinstance(val, int): numeric +=1
        print '* Got this from Alt:', val


@process
def testAlt3(cin1, cin2, cin3, _process=None):
    # For obvious reasons, SKIP cannot go first 
    alt = Alt(cin1, cin2, cin3, Skip())
    numeric = 0
    while numeric < 3:
        print '*** TestAlt3 selecting...'        
        val = alt.pri_select()
        if isinstance(val, int): numeric +=1
        print '* Got this from Alt:', val


@process
def testAlt4(cin1, cin2, cin3, _process=None):
    alt = Alt(Skip(), cin1, cin2, cin3)
    numeric = 0
    while numeric < 3:
        print '*** TestAlt4 selecting...'        
        val = alt.fair_select()
        if isinstance(val, int): numeric +=1
        print '* Got this from Alt:', val

@process
def testOr(cin1, cin2, _process=None):
    print cin1 | cin2
    print cin1 | cin2
    return

@process
def testAltRRep(cin1, cin2, cin3, _process=None):
    gen = Alt(cin1, cin2, cin3) * 3
    print gen.next()
    print gen.next()
    print gen.next()

@process
def testAltLRep(cin1, cin2, cin3, _process=None):
    gen = 3 * Alt(cin1, cin2, cin3)
    print gen.next()
    print gen.next()
    print gen.next()

@process
def chMobSend(cout, klass=Channel, _process=None):
    ch = klass()
    print 'Sending channel about to write channel to cout.'
    if isinstance(chan, FileChannel):
        print 'Using filename:', chan._fname
    cout.write(chan)
    time.sleep(1)
    chan.write('Yeah, baby, yeah!')
    return


@process
def chMobRecv(cin, _process=None):
    print 'Receiving channel about to read channel.'
    chan = cin.read()
    print 'Receiving channel got channel:', type(chan)
    if isinstance(chan, FileChannel):
        print 'Using filename:', chan._fname
    print chan.read()
    return


@process
def recvEv(_process=None):
    #print event
    return

@process
def sendEv(cout, _process=None):
    cout.write('Sending this to a guarded event...')
    return

########## Top level stuff

def _printHeader(name):
    random.seed(time.clock()) # Introduce a bit more randomness...    
    print
    print '****************************************************'
    print '* Testing %s...' % name
    print '****************************************************'
    print
    return

def testSeq():
    _printHeader('Seq')
    print 'With operator overloading...'
    foo(1) > foo(2) > foo(3)
    print
    print 'With process objects...'
    Seq(foo(1), foo(2), foo(3)).start()
    return

def testPar():
    _printHeader('Par')
    print '5 processes with operator overloading...'
    p = foo(1) & foo(2) & foo(3) & foo(4) & foo(5)
    time.sleep(5)
    print
    print '8 processes with operator overloading...'
    p = foo(1) & foo(2) & foo(3) & foo(4) & foo(5) & foo(6) & foo(7) & foo(8)
    time.sleep(5)
    print
    print '5 processes with process objects...'
    Par(foo(1), foo(2), foo(3), foo(4), foo(5)).start()
    time.sleep(5)
    return

def testChan():
    _printHeader('Channels')
    print '1 producer, 1 consumer, 1 channel...'
    c1 = Channel()
    p = Par(recv(c1), send(c1))
    p.start()
    print
    print '5 producers, 5 consumers, 5 channels...'
    chans = [Channel() for i in range(5)]
    p = [send(chan) for chan in chans] + [recv(chan) for chan in chans]
    pp = Par(*p)
    pp.start()
    print
    print '5 producers, 5 consumers, 1 channel...'
    chan = Channel()
    p = [send(chan) for i in range(5)] + [recv(chan) for i in range(5)]
    pp = Par(*p)
    pp.start()
    return

def testOOP():
    _printHeader('channel read/write using object methods...')
    testoop()

def testPoison():
    _printHeader('process termination (by poisoning)')
    chanp = Channel()
    tpar = Par(send100(chanp), recv100(chanp), testpoison(chanp))
    tpar.start()
    time.sleep(5)
    return

def testAlt():
    _printHeader('Alt')
    print 'Alt with 3 SKIPs:'
    ta0 = testAlt0()
    ta0.start()
    ta0._join()
    print
    print 'Alt with 1 channel read:'
    ch1 = Channel()
    ta1 = Par(testAlt1(ch1), sendAlt(ch1, 100))
    ta1.start()
    ta1._join()
    print
    print 'Alt with 1 SKIP, 3 channel reads:'
    ch2, ch3, ch4 = Channel(), Channel(), Channel()
    ta2 = Par(testAlt2(ch2, ch3, ch4),
              sendAlt(ch2, 100),
              sendAlt(ch3, 200),
              sendAlt(ch4, 300))
    ta2.start()
    ta2._join()
    print
    print 'Alt with priSelect on 1 SKIP, 3 channel reads:'
    ch5, ch6, ch7 = Channel(), Channel(), Channel()
    ta3 = Par(testAlt3(ch5, ch6, ch7),
              sendAlt(ch5, 100),
              sendAlt(ch6, 200),
              sendAlt(ch7, 300))
    ta3.start()
    ta3._join()
    print
    print 'Alt with fairSelect on 1 SKIP, 3 channel reads:'
    ch8, ch9, ch10 = Channel(), Channel(), Channel()
    ta4 = Par(testAlt4(ch8, ch9, ch10),
              sendAlt(ch8, 100),
              sendAlt(ch9, 200),
              sendAlt(ch10, 300))
    ta4.start()
    ta4._join()
    return

def testChoice():
    _printHeader('Choice')
    print 'Choice with |:'
    c1, c2 = Channel(), Channel()
    sendAlt(c1, 100) & sendAlt(c2, 200) & testOr(c1, c2)
    return

def testRep():
    _printHeader('Repetition')
    print 'Repetition with Alt * int:'
    ch1, ch2, ch3 = Channel(), Channel(), Channel()
    (sendAlt(ch1, 100) & sendAlt(ch2, 200) & sendAlt(ch3, 300) &
     testAltRRep(ch1, ch2, ch3))
    print
    print 'Repetition with Alt * int:'
    ch1, ch2, ch3 = Channel(), Channel(), Channel()
    (sendAlt(ch1, 100) & sendAlt(ch2, 200) & sendAlt(ch3, 300) &
     testAltLRep(ch1, ch2, ch3))
    return

def testEvent():
    _printHeader('syntactic sugar for guarded events')
    print 'Not implemented yet...'
#    ch = Channel()
#    sendEv() & ch > recvEv()
    return

def testDynamicChannel():
    _printHeader('dynamic channel creation')
    print 'Not implemented yet...'
    return

def testMobility():
    _printHeader('mobility')
    print 'Testing mobility of file channel objects.'
    ch1 = FileChannel()
    par = Par(chMobSend(ch1, klass=FileChannel), chMobRecv(ch1))
    par.start()
    par._join()
    print 
    print 'Testing mobility of channel objects.'
    ch2 = Channel()
    par2 = Par(chMobSend(ch2, klass=Channel), chMobRecv(ch2))
    par2.start()
    par2._join()
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
    parser.add_option('-e', '--event', dest='event', 
                      action='store_true',
                      help='Test syntactic sugar for guarded events')
    parser.add_option('-m', '--mobility', dest='mobility', 
                      action='store_true',
                      help='Test channel and process mobility')

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
        testEvent()
        testDynamicChannel()
#    	testMobility()
        print _exit
        sys.exit()
    if options.seq: testSeq()
    if options.par: testPar()
    if options.chan: testChan()
    if options.oop: testOOP()
    if options.term: testPoison()
    if options.alt: testAlt()
    if options.choice: testChoice()
    if options.rep: testRep()
    if options.event: testEvent()
    if options.mobility: testMobility()
    print _exit
    sys.exit()
