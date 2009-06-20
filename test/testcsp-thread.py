#!/usr/bin/env python

from csp.cspthread import *
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
    print ('%s in thread %s has arg %g' %
           (_process.getName(), _process.getPid(), n))
    return

@process
def send(cout, _process=None):
    for i in xrange(5):
        print '%s thread: %s sending %g' % (_process.getName(),
                                            _process.getPid(), 
                                            i)
        cout.write(i)
    return

@process
def recv(cin, _process=None):
    for i in xrange(5):
        data = cin.read()
        print '%s thread: %s received %s' % (_process.getName(),
                                             _process.getPid(),
                                             data)
    return

@process
def send100(cout, _process=None):
    for i in xrange(100):
        print '%s thread: %s sending %g' % (_process.getName(),
                                            _process.getPid(), 
                                            i)
        cout.write(i)
    return

@process
def recv100(cin, _process=None):
    for i in xrange(100):
        data = cin.read()
        print '%s thread: %s received %s' % (_process.getName(),
                                             _process.getPid(),
                                             data)
    return

class TestOOP(object):
    def __init__(self):
        self.ch = Channel()
    @process
    def send(self, msg, _process=None):
        self.ch.write(msg)
    @process
    def recv(self, _process=None):
        print self.ch.read()

def testoop():
    f = TestOOP()
    PAR(f.send('hello world'), f.recv()).start()

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
    alt = ALT(SKIP(), SKIP(), SKIP())
    for i in range(3):
        print '*** TestAlt0 selecting...'
        recv = alt.select()
        print '* Got this from Alt:', recv

@process
def testAlt1(cin, _process=None):
    alt = ALT(SKIP(), cin)
    numeric = 0 
    while numeric < 1:
        print '*** TestAlt1 selecting...'
        recv = alt.select()
        if isinstance(recv, int): numeric +=1 
        print '* Got this from Alt:', recv

@process
def testAlt2(cin1, cin2, cin3, _process=None):
    alt = ALT(SKIP(), cin1, cin2, cin3)
    numeric = 0 
    while numeric < 3:
        print '*** TestAlt2 selecting...'
        recv = alt.select()
        if isinstance(recv, int): numeric +=1
        print '* Got this from Alt:', recv
        
@process
def testAlt3(cin1, cin2, cin3, _process=None):
    # For obvious reasons, SKIP cannot go first 
    alt = ALT(cin1, cin2, cin3, SKIP())
    numeric = 0
    while numeric < 3:
        print '*** TestAlt3 selecting...'        
        recv = alt.priSelect()
        if isinstance(recv, int): numeric +=1
        print '* Got this from Alt:', recv
        
@process
def testAlt4(cin1, cin2, cin3, _process=None):
    alt = ALT(SKIP(), cin1, cin2, cin3)
    numeric = 0
    while numeric < 3:
        print '*** TestAlt4 selecting...'        
        recv = alt.fairSelect()
        if isinstance(recv, int): numeric +=1
        print '* Got this from Alt:', recv

@process
def chMobSend(cout, klass=Channel, _process=None):
    ch = klass()
    print 'Sending channel about to write channel to cout.'
    if isinstance(ch, FileChannel):
        print 'Using filename:', ch._fname
    cout.write(ch)
    time.sleep(1)
    ch.write('Yeah, baby, yeah!')
    return

@process
def chMobRecv(cin, _process=None):
    print 'Receiving channel about to read channel.'
    ch = cin.read()
    print 'Receiving channel got channel:', type(ch)
    if isinstance(ch, FileChannel):
        print 'Using filename:', ch._fname
    print ch.read()
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
    _printHeader('SEQ')
    print 'With operator overloading...'
    foo(1) > foo(2) > foo(3)
    print
    print 'With process objects...'
    SEQ(foo(1), foo(2), foo(3)).start()
    return

def testPar():
    _printHeader('PAR')
    print '5 processes with operator overloading...'
    p = foo(1) & foo(2) & foo(3) & foo(4) & foo(5)
    time.sleep(5)
    print
    print '8 processes with operator overloading...'
    p = foo(1) & foo(2) & foo(3) & foo(4) & foo(5) & foo(6) & foo(7) & foo(8)
    time.sleep(5)
    print
    print '5 processes with process objects...'
    PAR(foo(1), foo(2), foo(3), foo(4), foo(5)).start()
    time.sleep(5)
    return

def testChan():
    _printHeader('Channels')
    print '1 producer, 1 consumer, 1 channel...'
    c1 = Channel()
    p = PAR(recv(c1), send(c1))
    p.start()
    print
    print '5 producers, 5 consumers, 5 channels...'
    chans = [Channel() for i in range(5)]
    p = [send(ch) for ch in chans] + [recv(ch) for ch in chans]
    pp = PAR(*p)
    pp.start()
    print
    print '5 producers, 5 consumers, 1 channel...'
    chan = Channel()
    p = [send(chan) for i in range(5)] + [recv(chan) for i in range(5)]
    pp = PAR(*p)
    pp.start()
    return

def testOOP():
    _printHeader('channel read/write using object methods...')
    testoop()

def testPoison():
    _printHeader('process termination (by poisoning)')
    cp = Channel()
    tp = PAR(send100(cp), recv100(cp), testpoison(cp))
    tp.start()
    time.sleep(5)
    return

def testAlt():
    _printHeader('ALT')
    print 'Alt with 3 SKIPs:'
    ta0 = testAlt0()
    ta0.start()
    ta0._join()
    print
    print 'Alt with 1 SKIP, 1 channel read:'
    ch1 = Channel()
    ta1 = PAR(testAlt1(ch1), sendAlt(ch1, 100))
    ta1.start()
    ta1._join()
    print
    print 'Alt with 1 SKIP, 3 channel reads:'
    ch2, ch3, ch4 = Channel(), Channel(), Channel()
    ta2 = PAR(testAlt2(ch2, ch3, ch4),
              sendAlt(ch2, 100),
              sendAlt(ch3, 200),
              sendAlt(ch4, 300))
    ta2.start()
    ta2._join()
    print
    print 'Alt with priSelect on 1 SKIP, 3 channel reads:'
    ch5, ch6, ch7 = Channel(), Channel(), Channel()
    ta3 = PAR(testAlt3(ch5, ch6, ch7),
              sendAlt(ch5, 100),
              sendAlt(ch6, 200),
              sendAlt(ch7, 300))
    ta3.start()
    ta3._join()
    print
    print 'Alt with fairSelect on 1 SKIP, 3 channel reads:'
    ch8, ch9, ch10 = Channel(), Channel(), Channel()
    ta4 = PAR(testAlt4(ch8, ch9, ch10),
              sendAlt(ch8, 100),
              sendAlt(ch9, 200),
              sendAlt(ch10, 300))
    ta4.start()
    ta4._join()
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
    ch = FileChannel()
    p = PAR(chMobSend(ch, klass=FileChannel), chMobRecv(ch))
    p.start()
    p._join()
    print 
    print 'Testing mobility of channel objects.'
    ch2 = Channel()
    p2 = PAR(chMobSend(ch2, klass=Channel), chMobRecv(ch2))
    p2.start()
    p2._join()
    return

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()

    parser.add_option('-a', '--all', dest='all', 
                      action='store_true',
                      help='Test all CSP features')    
    parser.add_option('-s', '--seq', dest='seq', 
                      action='store_true',
                      help='Test SEQ')
    parser.add_option('-p', '--par', dest='par', 
                      action='store_true',
                      help='Test PAR')
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
                      help='Test ALTernatives')
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
    if options.event: testEvent()
    if options.mobility: testMobility()
    print _exit
    sys.exit()
