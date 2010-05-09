#!/usr/bin/env python

"""
Unit testing framework for python-csp. Same API as unittest.py in the
standard distribution.

Copyright (C) Sarah Mount, 2010.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have rceeived a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


__author__ = 'Sarah Mount <s.mount@wlv.ac.uk>'
__credits__ = 'Steve Purcell, author of unittest.py in stdlib'
__date__ = 'May 2010'


import unittest


# Exported classes and functions
__all__ = ['TestResult', 'TestCase', 'TestSuite', 'TextTestRunner',
           'TestLoader', 'FunctionTestCase', 'main', 'defaultTestLoader']

# Expose obsolete functions for backwards compatibility
__all__.extend(['getTestCaseNames', 'makeSuite', 'findTestCases'])


# Names exported from the standard library
TestResult        = unittest.TestResult
TestSuite         = unittest.TestSuite
TextTestRunner    = unittest.TextTestRunner
TestLoader        = unittest.TestLoader
FunctionTestCase  = unittest.FunctionTestCase
main              = unittest.main
defaultTestLoader = unittest.defaultTestLoader
getTestCaseNames  = unittest.getTestCaseNames
makeSuite         = unittest.makeSuite
findTestCases     = unittest.findTestCases


# Overriding TestCase with CSP specialisms
class TestCase(unittest.TestCase):
    """Test case, adapted for CSP style code.
    """

    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self, methodname)
        return

    def fail(self, msg=None):
        """Fail immediately, with the given message."""
        raise self.failureException, msg

    def failIf(self, expr, msg=None):
        "Fail the test if the expression is true."
        if expr: raise self.failureException, msg

    def failUnless(self, expr, msg=None):
        """Fail the test unless the expression is true."""
        if not expr: raise self.failureException, msg

    def failUnlessRaises(self, excClass, callableObj, *args, **kwargs):
        """Fail unless an exception of class excClass is thrown
           by callableObj when invoked with arguments args and keyword
           arguments kwargs. If a different type of exception is
           thrown, it will not be caught, and the test case will be
           deemed to have suffered an error, exactly as for an
           unexpected exception.
        """
        try:
            callableObj(*args, **kwargs)
        except excClass:
            return
        else:
            if hasattr(excClass,'__name__'): excName = excClass.__name__
            else: excName = str(excClass)
            raise self.failureException, "%s not raised" % excName

    def failUnlessEqual(self, channel, expected, msg=None):
        """Fail if the two objects are unequal as determined by the '=='
           operator.
        """
        if not first == second:
            raise self.failureException, \
                  (msg or '%r != %r' % (channel.read(), expected))

    def failIfEqual(self, channel, expected, msg=None):
        """Fail if the two objects are equal as determined by the '=='
           operator.
        """
        if first == second:
            raise self.failureException, \
                  (msg or '%r == %r' % (channel.read(), expected))

    def failUnlessAlmostEqual(self, channel, expected, places=7, msg=None):
        """Fail if the two objects are unequal as determined by their
           difference rounded to the given number of decimal places
           (default 7) and comparing to zero.

           Note that decimal places (from zero) are usually not the same
           as significant digits (measured from the most signficant digit).
        """
        if round(abs(second-first), places) != 0:
            raise self.failureException, \
                  (msg or '%r != %r within %r places' % (channel.read(), expected, places))

    def failIfAlmostEqual(self, channel, expected, places=7, msg=None):
        """Fail if the two objects are equal as determined by their
           difference rounded to the given number of decimal places
           (default 7) and comparing to zero.

           Note that decimal places (from zero) are usually not the same
           as significant digits (measured from the most signficant digit).
        """
        if round(abs(second-first), places) == 0:
            raise self.failureException, \
                  (msg or '%r == %r within %r places' % (channel.read(), expected, places))

    # Synonyms for assertion methods

    assertEqual = assertEquals = failUnlessEqual

    assertNotEqual = assertNotEquals = failIfEqual

    assertAlmostEqual = assertAlmostEquals = failUnlessAlmostEqual

    assertNotAlmostEqual = assertNotAlmostEquals = failIfAlmostEqual

    assertRaises = failUnlessRaises

    assert_ = assertTrue = failUnless

    assertFalse = failIf


# Executing this module from the command line
if __name__ == "__main__":
    main(module=None)
