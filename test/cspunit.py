#!/usr/bin/env python

from csp.cspprocess import *
import itertools
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


class __TestSeq(unittest.TestCase):
    """Test Seq objects and syntactic sugar for them.
    """

    @process
    def write_one(self, obj, filename, _process=None):
        fd = open(filename, 'a').write(str(obj))
        return

    def tear_down(self):
        os.unlink(temp)
        return


class TestSeqOperator(__TestSeq):

    def runTest(self):
        global temp
        self.write_one('1\n', temp) > self.write_one('2\n', temp) > self.write_one('3\n', temp)
        fd = open(temp, 'r')
        self.assertEquals(int(fd.readline()), 1)
        self.assertEquals(int(fd.readline()), 2)
        self.assertEquals(int(fd.readline()), 3)
        fd.close()
        return


class TestSeqObjects(__TestSeq):

    def runTest(self):
        global temp
        Seq(self.write_one('1\n', temp),
            self.write_one('2\n', temp),
            self.write_one('3\n', temp)).start()
        fd = open(temp, 'r')
        self.assertEquals(int(fd.readline()), 1)
        self.assertEquals(int(fd.readline()), 2)
        self.assertEquals(int(fd.readline()), 3)
        fd.close()
        return


class __TestChannel(unittest.TestCase):
    """Test basic channel reading and writing.
    """

    @process
    def write(self, obj, chan, _process=None):
        chan.write(obj)
        return

    @process
    def read_ret(self, cin, cout, _process=None):
        obj = cin.read()
        cout.write(obj)
        return


class TestChannelSingle(__TestChannel):

    def runTest(self):
        """Test single reader, single writer on C{Channel} objects.
        """
        c1, c2 = Channel(), Channel()
        self.write(100, c1) & self.read_ret(c1, c2)
        val = c2.read()
        self.assertEquals(val, 100)
        return

class TestFileChannelSingle(__TestChannel):

    def runTest(self):
        """Test single reader, single writer on C{FileChannel}
        objects.
        """
        c1, c2 = FileChannel(), FileChannel()
        self.write(100, c1) & self.read_ret(c1, c2)
        val = c2.read()
        self.assertEquals(val, 100)
        return

class TestChannelMultiple(__TestChannel):

    def runTest(self):
        """Test multiple readers, multiple writers on C{Channel}
        objects.
        """
        c1, c2 = Channel(), Channel()
        out = []
        def gen():
            for i in xrange(10):
                yield self.write(i, c1)
                yield self.read_ret(c1, c2)
        procs = list(gen())
        par = Par(*procs)
        par.start()
        par._join()
        for i in xrange(10):
            out.append(c2.read())
        out.sort()
        self.assertEquals(out, range(10))
        return

class TestFileChannelMultiple(__TestChannel):

    def runTest(self):
        """Test multiple readers, multiple writers on C{FileChannel}
        objects.
        """
        c1, c2 = FileChannel(), FileChannel()
        out = []
        def gen():
            for i in xrange(10):
                yield self.write(i, c1)
                yield self.read_ret(c1, c2)
        procs = list(gen())
        par = Par(*procs)
        par.start()
        par._join()
        for i in xrange(10):
            out.append(c2.read())
        out.sort()
        self.assertEquals(out, range(10))
        return


class TestOr(unittest.TestCase):
    """Test syntactic sugar for Alting with the | operator.
    """

    @process
    def choice(self, cin1, cin2, cout, _process=None):
        output = []
        output.append(cin1 | cin2)
        output.append(cin1 | cin2)
        cout.write(output)
        return

    @process
    def send(self, obj, chan, _process=None):
        chan.write(obj)
        return

    def runTest(self):
        c1, c2, c3 = Channel(), Channel(), Channel()
        self.send(100, c1) & self.send(200, c2) & self.choice(c1, c2, c3)
        out = c3.read()
        out.sort()
        self.assertEquals(out, [100, 200])
        return


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


class TestFail(unittest.TestCase):

    def runTest(self):
        self.assertTrue(False)

if __name__ == '__main__':
# We could have just done this, if we hand't wanted to mangle the wiki pages:
#    import sys
#    unittest.main()
#    sys.exit()
    
    tests = [(TestSeqOperator(), unittest.TestResult()),
             (TestSeqObjects(), unittest.TestResult()),
             (TestOr(), unittest.TestResult()),
             # TestAlt(), # Remove until Mohammad has finished his proofs.
             (TestFail(), unittest.TestResult()),
             (TestChannelSingle(), unittest.TestResult()),
             (TestFileChannelSingle(), unittest.TestResult()),
             (TestChannelMultiple(), unittest.TestResult()),
             (TestFileChannelMultiple(), unittest.TestResult())]

    # Results
    successes = 0
    failures = 0
    errors = 0

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
            msg += 'ERROR ' + res.errors[0] + ' ' + res.errors[1] + '\n'
    msg += '\n----------------------------------------------------------------------\n'
    msg += 'Ran %i tests in %gs.\n' % (len(tests), duration)
    if failures == 0 and errors == 0:
        msg += 'OK. '
    elif failures > 0:
        msg += 'FAILED. (failures=%i) ' % failures
    if errors > 0:
        msg += 'ERRORS. (errors=%i)' % errors

    # Print output to STDOUT.
    print msg

    # Write results of testing out to wiki page for SVN.
    wikipage = '../../wiki/UnitTestingStatus.wiki'

    template = """#summary Current unit testing status
#labels Phase-QA

= Current unit testing status =

== csp.process results ==

=== Summary ===

http://chart.apis.google.com/chart?cht=bhg&chs=400x200&chd=t:%i|%i|%i&chco=00cc00,cc0000,0000cc&chm=tPASSED,00cc00,0,0,13|tFAILED,cc0000,1,1,13,-1|tERRORS,0000cc,2,1,13&nonsense=foo.png'

=== Testing output ===

{{{
%s
}}}

""" % (successes, failures, errors, msg)

    fd = open(wikipage, 'w')
    fd.write(template)
    fd.close()
    print 'Written wiki page to working copy of SVN.\n'
