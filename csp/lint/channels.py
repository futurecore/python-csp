#!/usr/bin/env python

"""
Check that every process in a file has correct readsets and writesets.

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
__date__ = 'April 2010'


__all__ = ['ChannelChecker']

class ChannelChecker(visitor.ASTVisitor):
    """Check that documented readsets and writesets are correct
    w.r.t. code.
    """

    def __init__(self, filename):
        visitor.ASTVisitor.__init__(self)
        self.filename = filename
        self.current_process = ''
        self.current_process_lineno = 0
        self.writeset = {}
        self.readset = {}
        self.readset_lineno = 0
        self.writeset_lineno = 0
        return

    def extract_sets(self, doc):
        """Extract the readset and writeset from function
        documentation.
        """
        readset = []
        writeset = []
        has_readset = False
        has_writeset = False
        lineno = 0
        if doc is not None:
            for line in doc.split('\n'):
                lineno += 1
                words = line.strip().split('=')
                if words is not None:
                    if words[0].strip() == 'readset':
                        has_readset = True
                        self.readset_lineno += lineno
                        chans = words[1].strip().split(',')
                        readset = [y for y in [x.strip() for x in chans] if y is not '']
                    elif words[0].strip() == 'writeset':
                        has_writeset = True
                        self.writeset_lineno += lineno
                        chans = words[1].strip().split(',')
                        writeset = [y for y in [x.strip() for x in chans] if y is not '']

        # 'W002':'No readset given in documentation.'
        if not has_readset:
            exstatic.cspwarnings.create_error(self.filename,
                                              self.readset_lineno,
                                              self.current_process,
                                              'W002')

        # 'W003':'No writeset given in documentation.'
        if not has_writeset:
            exstatic.cspwarnings.create_error(self.filename,
                                              self.writeset_lineno,
                                              self.current_process,
                                              'W003')

        return set(readset), set(writeset)

    def is_process(self, decorators):
        """Determine whether or not the current function is a CSP
        process.
        """
        for decorator in decorators:
            if (decorator.name == 'process' or decorator.name == 'forever'):
                return True
        return False

    def check_sets(self, readset, writeset):
        """Check that the documented readset and writeset of the
        current function match the code inside the function
        definition.

        @param readset the documented readset of the current process
        @param writeset the documented writeset of the current process
        """
        # 'W001':'Channel in both readset and writeset.'
        if len(readset.intersection(writeset)) > 0:
            exstatic.cspwarnings.create_error(self.filename,
                                              self.readset_lineno,
                                              self.current_process,
                                              'W001')
        
        # 'E004':'Channel appears in documented readset but not read
        # from in function body.'
        diff = set(self.readset.values()).difference(readset)
        for channel in diff:
            exstatic.cspwarnings.create_error(self.filename,
                                              self.readset_lineno,
                                              self.current_process,
                                              'E004')
            
        # 'E005':'Channel is read from in function body but does not
        # appear in documented readset'
        diff = set(readset).difference(list(self.readset.values()))
        for channel in diff:
            for key in self.readset:
                exstatic.cspwarnings.create_error(self.filename,
                                                  key,
                                                  self.current_process,
                                                  'E005')

        # 'E006':'Channel appears in documented writeset but not
        # written to in function body.'
        diff = set(self.writeset.values()).difference(writeset)
        for channel in diff:
            exstatic.cspwarnings.create_error(self.filename,
                                              self.writeset_lineno,
                                              self.current_process,
                                              'E006')

        # 'E007':'Channel is written to in function body but does not
        # appear in documented writeset'
        diff = set(writeset).difference(list(self.writeset.values()))
        for channel in diff:
            for key in self.writeset:
                exstatic.cspwarnings.create_error(self.filename,
                                                  key,
                                                  self.current_process,
                                                  'E007')

        return

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
        self.readset_lineno, self.writeset_lineno = node.lineno, node.lineno
        readset, writeset = self.extract_sets(node.doc)

        # 'E002':'Channel in readset is not a formal parameter to this
        # process.',
        for channel in readset:
            if not channel in node.argnames:
                exstatic.cspwarnings.create_error(self.filename,
                                                  self.readset_lineno,
                                                  node.name,
                                                  'E002')

        # 'E003':'Channel in writeset is not a formal parameter to
        # this process.',
        for channel in writeset:
            if not channel in node.argnames:
                exstatic.cspwarnings.create_error(self.filename,
                                                  self.writeset_lineno,
                                                  node.name,
                                                  'E003')

        # Ensure that we visit every statement inside this fuction.
        for stmt in node.code:
            self.visit(stmt)

        # Check the documented readset and writeset against actual
        # method calls within the function.
        self.check_sets(readset, writeset)
            
        # Remove information held about this function.
        self.current_process = ''
        self.current_process_lineno = 0
        self.writeset = {}
        self.readset = {}
        return

    def visitCallFunc(self, node):
        """Visit function call.

        TODO: Deal with Alt and Barrier types.
        """        
        callee = node.node
        if isinstance(callee, ast.Getattr):
            if not isinstance(callee.expr, ast.Getattr):
                # Catch all calls to channel read().
                if callee.attrname == 'read':
                    self.readset[callee.lineno] = callee.expr.name
                # Catch all calls to channel write()
                elif callee.attrname == 'write':
                    self.writeset[callee.lineno] = callee.expr.name
        return


if __name__ == '__main__':
    import sys

    lint = ChannelChecker(sys.argv[1])
    compiler.walk(compiler.parseFile(sys.argv[1]),
                  lint,
                  walker=lint,
                  verbose=5)

    exstatic.cspwarnings.print_errors(excluded=[])
