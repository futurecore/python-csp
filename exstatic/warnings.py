#!/usr/bin/env python

"""
Generic warnings and errors for Exstatic.

TODO: Document this module.

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
__date__ = 'May 2010'

import os.path
import sys

severity = {'I':'Information', 'W':'Warning', 'E':'Error'}


__all__ = ['severity', 'ExstaticErrorList', 'ExstaticError',
           'ExstaticErrorFactory']


class ExstaticErrorList(object):

    def __init__(self, errcodes):
        self.error_factory = ExstaticErrorFactory(errcodes)
        self.errors = []
        return

    def create_error(self, filename, lineno, scope, errcode):
        error = self.error_factory.create_error(filename, lineno, scope, errcode)
        self.errors.append(error)
        return

    def get_errors(self, excluded=[]):
        """Return a list of the current errors, excluding any in the
        excluded set.
        """
        errors = []
        for error in self.errors:
            if not error.errcode in excluded:
                errors.append(error)
        return errors

    def print_errors(self, out=sys.stdout, excluded=[]):
        """Print a list of the current errors, excluding any in the
        excluded set.
        """
        for error in self.errors:
            if not error.errcode in excluded:
                out.write(str(error))
                out.write('\n')
        return

    def reset_errors(self):
        self.errors = []
        return


class ExstaticErrorFactory(object):

    def __init__(self, errcodes):
        """
        @param errcodes dictionary of error codes -> explainations
        """
        self.errcodes = errcodes
        return

    def create_error(self, filename, lineno, scope, errcode):
        """Create and return a new error.
        """
        obj = ExstaticError(filename, lineno, scope, errcode)
        obj.set_explaination(self.errcodes[errcode])
        return obj


class ExstaticError(object):

    def __init__(self, filename, lineno, scope, errcode):
        """
        @param filename: name of the file in which error occurs
        @param lineno: line number on which error occurs
        @param scope: scope that the error occurs in (e.g. function name)
        @param errcode: name of this particular error
        """
        self.filename = os.path.basename(filename)
        self.lineno = lineno
        self.scope = scope
        self.errcode = errcode
        self.explaination = ''
        return

    def get_severity(self):
        """
        @return 'E' for an error and 'W' for a warning.
        """
        return severity[self.errcode[0]]

    def set_explaination(self, explain):
        self.explaination = explain
        return

    def __str__(self):
        return '[{0}:{1}] {2} ({3}, {4}): {5}'.format(self.filename,
                                                      self.lineno,
                                                      self.get_severity(),
                                                      self.errcode,
                                                      self.scope,
                                                      self.explaination)

