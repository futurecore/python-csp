#!/usr/bin/env python

import csp.cspprocess
import csp.cspthread

import unittest
import os
import time

"""
Unit tests for basic python-csp functionality.

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
"""

__author__ = 'Sarah Mount <s.mount@wlv.ac.uk>'
__date__ = 'June 2009'


temp = 'unittest.out'

################################################################################
# Seq tests.
################################################################################

class __TestSeqProc(unittest.TestCase):
    """Test Seq objects and syntactic sugar for them.
    """

    @csp.cspprocess.process
    def write_one(self, obj, filename, _process=None):
        fd = open(filename, 'a').write(str(obj))
        return

    def tear_down(self):
        os.unlink(temp)
        return


class TestSeqOperatorProc(__TestSeqProc):

    def runTest(self):
        global temp
        self.write_one('1\n', temp) > self.write_one('2\n', temp) > self.write_one('3\n', temp)
        fd = open(temp, 'r')
        self.assertEquals(int(fd.readline()), 1)
        self.assertEquals(int(fd.readline()), 2)
        self.assertEquals(int(fd.readline()), 3)
        fd.close()
        return


class TestSeqObjectsProc(__TestSeqProc):

    def runTest(self):
        global temp
        csp.cspprocess.Seq(self.write_one('1\n', temp),
                           self.write_one('2\n', temp),
                           self.write_one('3\n', temp)).start()
        fd = open(temp, 'r')
        self.assertEquals(int(fd.readline()), 1)
        self.assertEquals(int(fd.readline()), 2)
        self.assertEquals(int(fd.readline()), 3)
        fd.close()
        return


class __TestSeqThread(unittest.TestCase):
    """Test Seq objects and syntactic sugar for them.
    """

    @csp.cspthread.process
    def write_one(self, obj, filename, _process=None):
        fd = open(filename, 'a').write(str(obj))
        return

    def tear_down(self):
        os.unlink(temp)
        return


class TestSeqOperatorThread(__TestSeqThread):

    def runTest(self):
        global temp
        self.write_one('1\n', temp) > self.write_one('2\n', temp) > self.write_one('3\n', temp)
        fd = open(temp, 'r')
        self.assertEquals(int(fd.readline()), 1)
        self.assertEquals(int(fd.readline()), 2)
        self.assertEquals(int(fd.readline()), 3)
        fd.close()
        return


class TestSeqObjectsThread(__TestSeqThread):

    def runTest(self):
        global temp
        csp.cspthread.Seq(self.write_one('1\n', temp),
                          self.write_one('2\n', temp),
                          self.write_one('3\n', temp)).start()
        fd = open(temp, 'r')
        self.assertEquals(int(fd.readline()), 1)
        self.assertEquals(int(fd.readline()), 2)
        self.assertEquals(int(fd.readline()), 3)
        fd.close()
        return

################################################################################
# Channel object tests for csp.cspprocess.
################################################################################

class __TestChannelProc(unittest.TestCase):
    """Test basic channel reading and writing.
    """

    @csp.cspprocess.process
    def write(self, obj, chan, _process=None):
        chan.write(obj)
        return

    @csp.cspprocess.process
    def read_ret(self, cin, cout, _process=None):
        obj = cin.read()
        cout.write(obj)
        return


class TestChannelSingleProc(__TestChannelProc):

    def runTest(self):
        """Test single reader, single writer on C{Channel} objects.
        """
        c1, c2 = csp.cspprocess.Channel(), csp.cspprocess.Channel()
        self.write(100, c1) & self.read_ret(c1, c2)
        val = c2.read()
        self.assertEquals(val, 100)
        return


class TestFileChannelSingleProc(__TestChannelProc):

    def runTest(self):
        """Test single reader, single writer on C{FileChannel}
        objects.
        """
        c1, c2 = csp.cspprocess.FileChannel(), csp.cspprocess.FileChannel()
        self.write(100, c1) & self.read_ret(c1, c2)
        val = c2.read()
        self.assertEquals(val, 100)
        return


class TestNetworkChannelSingleProc(__TestChannelProc):

    def runTest(self):
        """Test single reader, single writer on C{Channel} objects.
        """
        c1 = csp.cspprocess.NetworkChannel()
        c2 = csp.cspprocess.NetworkChannel()
        self.write(100, c1) & self.read_ret(c1, c2)
        val = c2.read()
        self.assertEquals(val, 100)
        return


class TestChannelMultipleProc(__TestChannelProc):

    def runTest(self):
        """Test multiple readers, multiple writers on C{Channel}
        objects.
        """
        c1, c2 = csp.cspprocess.Channel(), csp.cspprocess.Channel()
        out = []
        def gen():
            for i in xrange(10):
                yield self.write(i, c1)
                yield self.read_ret(c1, c2)
        procs = list(gen())
        par = csp.cspprocess.Par(*procs)
        par.start()
        par._join()
        for i in xrange(10):
            out.append(c2.read())
        out.sort()
        self.assertEquals(out, range(10))
        return


class TestFileChannelMultipleProc(__TestChannelProc):

    def runTest(self):
        """Test multiple readers, multiple writers on C{FileChannel}
        objects.
        """
        c1, c2 = csp.cspprocess.FileChannel(), csp.cspprocess.FileChannel()
        out = []
        def gen():
            for i in xrange(10):
                yield self.write(i, c1)
                yield self.read_ret(c1, c2)
        procs = list(gen())
        par = csp.cspprocess.Par(*procs)
        par.start()
        par._join()
        for i in xrange(10):
            out.append(c2.read())
        out.sort()
        self.assertEquals(out, range(10))
        return


class TestNetworkChannelMultipleProc(__TestChannelProc):

    def runTest(self):
        """Test multiple readers, multiple writers on C{FileChannel}
        objects.
        """
        c1 = csp.cspprocess.NetworkChannel()
        c2 = csp.cspprocess.NetworkChannel()
        out = []
        def gen():
            for i in xrange(10):
                yield self.write(i, c1)
                yield self.read_ret(c1, c2)
        procs = list(gen())
        par = csp.cspprocess.Par(*procs)
        par.start()
        par._join()
        for i in xrange(10):
            out.append(c2.read())
        out.sort()
        self.assertEquals(out, range(10))
        return


################################################################################
# Channel object tests for csp.cspthreads.
################################################################################

class __TestChannelThread(unittest.TestCase):
    """Test basic channel reading and writing.
    """

    @csp.cspthread.process
    def write(self, obj, chan, _process=None):
        chan.write(obj)
        return

    @csp.cspthread.process
    def read_ret(self, cin, cout, _process=None):
        obj = cin.read()
        cout.write(obj)
        return


class TestChannelSingleThread(__TestChannelThread):

    def runTest(self):
        """Test single reader, single writer on C{Channel} objects.
        """
        c1, c2 = csp.cspthread.Channel(), csp.cspthread.Channel()
        self.write(100, c1) & self.read_ret(c1, c2)
        val = c2.read()
        self.assertEquals(val, 100)
        return


class TestFileChannelSingleThread(__TestChannelThread):

    def runTest(self):
        """Test single reader, single writer on C{FileChannel}
        objects.
        """
        c1, c2 = csp.cspthread.FileChannel(), csp.cspthread.FileChannel()
        self.write(100, c1) & self.read_ret(c1, c2)
        val = c2.read()
        self.assertEquals(val, 100)
        return


class TestNetworkChannelSingleThread(__TestChannelThread):

    def runTest(self):
        """Test single reader, single writer on C{FileChannel}
        objects.
        """
        c1, c2 = csp.cspthread.NetworkChannel(), csp.cspthread.NetworkChannel()
        self.write(100, c1) & self.read_ret(c1, c2)
        val = c2.read()
        self.assertEquals(val, 100)
        return


class TestChannelMultipleThread(__TestChannelThread):

    def runTest(self):
        """Test multiple readers, multiple writers on C{Channel}
        objects.
        """
        c1, c2 = csp.cspthread.Channel(), csp.cspthread.Channel()
        out = []
        def gen():
            for i in xrange(10):
                yield self.write(i, c1)
                yield self.read_ret(c1, c2)
        procs = list(gen())
        par = csp.cspthread.Par(*procs)
        par.start()
        par._join()
        for i in xrange(10):
            out.append(c2.read())
        out.sort()
        self.assertEquals(out, range(10))
        return


class TestFileChannelMultipleThread(__TestChannelThread):

    def runTest(self):
        """Test multiple readers, multiple writers on C{FileChannel}
        objects.
        """
        c1, c2 = csp.cspthread.FileChannel(), csp.cspthread.FileChannel()
        out = []
        def gen():
            for i in xrange(10):
                yield self.write(i, c1)
                yield self.read_ret(c1, c2)
        procs = list(gen())
        par = csp.cspthread.Par(*procs)
        par.start()
        par._join()
        for i in xrange(10):
            out.append(c2.read())
        out.sort()
        self.assertEquals(out, range(10))
        return


class TestNetworkChannelMultipleThread(__TestChannelThread):

    def runTest(self):
        """Test multiple readers, multiple writers on C{FileChannel}
        objects.
        """
        c1 = csp.cspthread.NetworkChannel()
        c2 = csp.cspthread.NetworkChannel()
        out = []
        def gen():
            for i in xrange(10):
                yield self.write(i, c1)
                yield self.read_ret(c1, c2)
        procs = list(gen())
        par = csp.cspthread.Par(*procs)
        par.start()
        par._join()
        for i in xrange(10):
            out.append(c2.read())
        out.sort()
        self.assertEquals(out, range(10))
        return


################################################################################
# Timer guard tests for csp.cspprocess
################################################################################

class TestTimerGuardProc(unittest.TestCase):

    def setUp(self):
        self.timeout = 5.0 # seconds
        return

    def runTest(self):
        guard = csp.cspprocess.TimerGuard()
        guard.set_alarm(self.timeout)
        alt = csp.cspprocess.Alt(guard)
        t0 = guard.read()
        alt.select()
        duration = guard.read() - t0
        self.assertAlmostEqual(duration, self.timeout, 1) # Equal to 1 d.p.
        return


class TestSleepProc(unittest.TestCase):

    def setUp(self):
        self.timeout = 5.0
        return
    
    def runTest(self):
        guard = csp.cspprocess.TimerGuard()
        t0 = guard.read()
        guard.sleep(self.timeout)
        t1 = guard.read()
        self.assertAlmostEqual(t1 - t0, self.timeout, 1) # Equal to 1 d.p.
        return

################################################################################
# Timer guard tests for csp.cspthread
################################################################################

class TestTimerGuardThread(unittest.TestCase):

    def setUp(self):
        self.timeout = 5.0 # seconds
        return
    
    def runTest(self):
        guard = csp.cspthread.TimerGuard()
        guard.set_alarm(self.timeout)
        alt = csp.cspthread.Alt(guard)
        t0 = guard.read()
        alt.select()
        duration = guard.read() - t0
        self.assertAlmostEqual(duration, self.timeout, 1) # Equal to 1 d.p.
        return


class TestSleepThread(unittest.TestCase):

    def setUp(self):
        self.timeout = 5.0
        return
    
    def runTest(self):
        guard = csp.cspthread.TimerGuard()
        t0 = guard.read()
        guard.sleep(self.timeout)
        t1 = guard.read()
        self.assertAlmostEqual(t1 - t0, self.timeout, 1) # Equal to 1 d.p.
        return


################################################################################
# Choice operator tests
################################################################################

class TestOrProc(unittest.TestCase):
    """Test syntactic sugar for Alting with the | operator.
    """

    @csp.cspprocess.process
    def choice(self, cin1, cin2, cout, _process=None):
        output = []
        output.append(cin1 | cin2)
        output.append(cin1 | cin2)
        cout.write(output)
        return

    @csp.cspprocess.process
    def send(self, obj, chan, _process=None):
        chan.write(obj)
        return

    def runTest(self):
        c1, c2, c3 = csp.cspprocess.Channel(), csp.cspprocess.Channel(), csp.cspprocess.Channel()
        self.send(100, c1) & self.send(200, c2) & self.choice(c1, c2, c3)
        out = c3.read()
        out.sort()
        self.assertEquals(out, [100, 200])
        return


class TestOrThread(unittest.TestCase):
    """Test syntactic sugar for Alting with the | operator.
    """

    @csp.cspthread.process
    def choice(self, cin1, cin2, cout, _process=None):
        output = []
        output.append(cin1 | cin2)
        output.append(cin1 | cin2)
        cout.write(output)
        return

    @csp.cspthread.process
    def send(self, obj, chan, _process=None):
        chan.write(obj)
        return

    def runTest(self):
        c1, c2, c3 = csp.cspthread.Channel(), csp.cspthread.Channel(), csp.cspthread.Channel()
        self.send(100, c1) & self.send(200, c2) & self.choice(c1, c2, c3)
        out = c3.read()
        out.sort()
        self.assertEquals(out, [100, 200])
        return


################################################################################
# Alt tests -- will be replaced when Mohammad's proofs are complete.
################################################################################

# class TestAlt(unittest.TestCase):

#     # FIXME: Add in fair_select() and pri_select()
#     # FIXME: Split into single units

#     @process
#     def send_one(self, obj, cout, _process=None):
#         cout.write(obj)
#         return

#     @process
#     def send_three_par(self, obj, cout1, cout2, cout3, _process=None):
#         par = Par(self.send_one(obj, cout1),
#                   self.send_one(obj, cout2),
#                   self.send_one(obj, cout3))
#         par.start()
#         par._join()
#         return

#     @process
#     def alt_three_oplr(self, cin1, cin2, cin3, cout, _process=None):
#         gen = 3 * Alt(cin1, cin2, cin3)
#         out = []
#         out.append(gen.next())
#         out.append(gen.next())
#         out.append(gen.next())
#         cout.write(out)
#         return

#     @process
#     def alt_three_oprl(self, cin1, cin2, cin3, cout, _process=None):
#         gen = Alt(cin1, cin2, cin3) * 3
#         out = []
#         out.append(gen.next())
#         out.append(gen.next())
#         out.append(gen.next())
#         cout.write(out)
#         return

#     @process
#     def alt_three(self, cin1, cin2, cin3, cout, _process=None):
#         alt = Alt(cin1, cin2, cin3)
#         out = []
#         out.append(alt.select())
#         out.append(alt.select())
#         out.append(alt.select())
#         cout.write(out)
#         return

#     def test_alt(self):
#         c1, c2, c3, c4 = Channel(), Channel(), Channel(), Channel()
#         par = Par(self.send_three_par(100, c1, c2, c3),
#                   self.alt_three(c1, c2, c3, c4))
#         par.start()
#         self.assertEquals(c4.read(), [100, 100, 100])
#         return
    
#     def test_alt_oplr(self):
#         c1, c2, c3, c4 = Channel(), Channel(), Channel(), Channel()
#         par = Par(self.send_three_par(100, c1, c2, c3),
#                   self.alt_three_oplr(c1, c2, c3,c4))
#         par.start()
#         ll = c4.read()
#         self.assertEquals(ll, [100, 100, 100])
#         return

#     def test_alt_oprl(self):
#         c1, c2, c3, c4 = Channel(), Channel(), Channel(), Channel()
#         par = Par(self.send_three_par(100, c1, c2, c3),
#                   self.alt_three_oprl(c1, c2, c3,c4))
#         par.start()
#         ll = c4.read()
#         self.assertEquals(ll, [100, 100, 100])
#         return

def runtests(tests):
    """Run a set of unit tests and return a summary of results.

    @param tests: list of C{TestCase}, C{TestResult} tuples.
    """
    # Results.
    successes = 0
    failures = 0
    errors = 0
    # Run tests and generate nice textual output.
    msg = '\n----------------------------------------------------------------------\n'
    t0 = time.time()
    for test, res in tests:
        test.run(res)
        if res.wasSuccessful():
            successes += 1
            msg += '.'
        if len(res.failures) > 0:
            failures += len(res.failures)
            msg += 'F'
        if len(res.errors) > 0:
            errors += len(res.errors)
            msg += 'E'
    t1 = time.time()
    duration = t1 - t0
    msg += '\n======================================================================\n'
    for test, res in tests:
        if len(res.failures) > 0:
            for klass, err in res.failures:
                msg += 'FAIL: ' + str(klass) + ' ' + err + ' '
        if len(res.errors) > 0:
            for klass, err in res.errors:
                msg += 'ERROR:' + str(klass) + '\n' + err + '\n'
    msg += 'Ran %i tests in %gs.\n' % (len(tests), duration)
    msg += '\n----------------------------------------------------------------------\n'
    if failures == 0 and errors == 0:
        msg += 'OK. '
    elif failures > 0:
        msg += 'FAILED. (failures=%i) ' % failures
    if errors > 0:
        msg += 'ERRORS. (errors=%i)' % errors
    return successes, failures, errors, msg
    

if __name__ == '__main__':
# We could have just done this, if we hand't wanted to mangle the wiki pages:
#    import sys
#    unittest.main()
#    sys.exit()

    proctests = [(TestSeqOperatorProc(), unittest.TestResult()),
                 (TestSeqObjectsProc(), unittest.TestResult()),
                 (TestOrProc(), unittest.TestResult()),
                 (TestTimerGuardProc(), unittest.TestResult()),
                 (TestSleepProc(), unittest.TestResult()),
                 (TestChannelSingleProc(), unittest.TestResult()),
                 (TestFileChannelSingleProc(), unittest.TestResult()),
                 (TestNetworkChannelSingleProc(), unittest.TestResult()),
                 (TestChannelMultipleProc(), unittest.TestResult()),
                 (TestFileChannelMultipleProc(), unittest.TestResult()),
                 (TestNetworkChannelMultipleProc(), unittest.TestResult())]

    threadtests = [(TestSeqOperatorThread(), unittest.TestResult()),
                 (TestSeqObjectsThread(), unittest.TestResult()),
                 (TestOrThread(), unittest.TestResult()),
                 (TestTimerGuardThread(), unittest.TestResult()),
                 (TestSleepThread(), unittest.TestResult()),
                 (TestChannelSingleThread(), unittest.TestResult()),
                 (TestFileChannelSingleThread(), unittest.TestResult()),
                 (TestNetworkChannelSingleThread(), unittest.TestResult()),
                 (TestChannelMultipleThread(), unittest.TestResult()),
                 (TestFileChannelMultipleThread(), unittest.TestResult()),
                 (TestNetworkChannelMultipleThread(), unittest.TestResult())]


    print
    print '*** Running unit tests for csp.cspprocess. This may take a while...'
    print
    procsucc, procfail, procerr, procmsg = runtests(proctests)
    print procmsg
    print
    print '*** Running unit tests for csp.cspthread. This may take a while...'
    print
    threadsucc, threadfail, threaderr, threadmsg = runtests(threadtests)
    print threadmsg

    # Write results of testing out to wiki page for SVN.
    wikipage = '../../wiki/UnitTestingStatus.wiki'

    template = """#summary Current unit testing status
#labels Phase-QA

= Current unit testing status =

== csp.cspprocess summary of results ===

http://chart.apis.google.com/chart?cht=bhg&chs=400x150&chd=t:%i|%i|%i&chco=00cc00,cc0000,0000cc&chm=tPASSED,00cc00,0,0,13|tFAILED,cc0000,1,1,13,-1|tERRORS,0000cc,2,1,13&nonsense=foo.png'

== csp.process testing output ==

{{{
%s
}}}

== csp.cspthread summary of results ===

http://chart.apis.google.com/chart?cht=bhg&chs=400x150&chd=t:%i|%i|%i&chco=00cc00,cc0000,0000cc&chm=tPASSED,00cc00,0,0,13|tFAILED,cc0000,1,1,13,-1|tERRORS,0000cc,2,1,13&nonsense=foo.png'

== csp.process testing output ==

{{{
%s
}}}

""" % (procsucc, procfail, procerr, procmsg, threadsucc, threadfail, threaderr, threadmsg)

    # Write out to wiki page.
    fd = open(wikipage, 'w')
    fd.write(template)
    fd.close()
    print
    print 'Written wiki page to working copy of SVN.'
    print
