#!/usr/bin/env python

"""
Check for errors in process definitions.

Copyright (C) Sarah Mount, 2010.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import compiler
import compiler.ast as ast
import compiler.visitor as visitor

import exstatic.cspwarnings


__author__ = 'Sarah Mount <s.mount@wlv.ac.uk>'
__date__ = 'May 2010'


__all__ = ['ProcessChecker']

class ProcessChecker(visitor.ASTVisitor):
    """Check that documented readsets and writesets are correct
    w.r.t. code.
    """

    def __init__(self, filename):
        visitor.ASTVisitor.__init__(self)
        self.filename = filename
        self.current_process = ''
        self.current_process_lineno = 0
        return


    def is_process(self, decorators):
        """Determine whether or not the current function is a CSP
        process.
        """
        for decorator in decorators:
            if (decorator.name == 'process' or decorator.name == 'forever'):
                return True
        return False


    def visitFunction(self, node):
        """Visit function definition.
        """
        
        # If this function definition is not a CSP process, ignore it.
        if (node.decorators is None or
            self.is_process(node.decorators) is None):            
            return

        # Store useful information about this process.
        self.current_process = node.name
        self.current_process_lineno = node.lineno

        # 'I001':'Function is a CSP process or server process',
        exstatic.cspwarnings.create_error(self.filename,
                                          self.current_process_lineno,
                                          self.current_process,
                                          'I001')

        # 'W004':'@process or @forever applied to method (rather than function)'
        if 'self' in node.argnames:
            exstatic.cspwarnings.create_error(self.filename,
                                              self.current_process_lineno,
                                              self.current_process,
                                              'W004')
        
        return


if __name__ == '__main__':
    import sys

    lint = ProcessChecker(sys.argv[1])
    compiler.walk(compiler.parseFile(sys.argv[1]),
                  lint,
                  walker=lint,
                  verbose=5)

    exstatic.cspwarnings.print_errors(excluded=[])
