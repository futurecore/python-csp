#!/usr/bin/env python

"""
Combined linting for python-csp.

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

import compiler
import csp.lint.channels
import csp.lint.processes

import exstatic.cspwarnings


__all__ = ['run']


checkers = [csp.lint.channels.ChannelChecker,
            csp.lint.processes.ProcessChecker]


def run(filename, excluded=[]):
    exstatic.cspwarnings.reset_errors()
    for checker in checkers:
        lint = checker(filename)
        compiler.walk(compiler.parseFile(filename),
                      lint,
                      walker=lint,
                      verbose=5)
    exstatic.cspwarnings.print_errors(excluded=excluded)
    return

if __name__ == '__main__':
    import sys
    if sys.argv > 1:
        run(sys.argv[1])
    sys.exit()
