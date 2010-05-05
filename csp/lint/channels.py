#!/usr/bin/env python

"""

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

import csp.tracer.icode as icode

from csp.tracer.stack import Stack

__author__ = 'Sarah Mount <s.mount@wlv.ac.uk>'
__date__ = 'April 2010'


class ChannelChecker(visitor.ASTVisitor):

    def __init__(self):
        visitor.ASTVisitor.__init__(self)
        self.model = '\n'
        self.processes = Stack()
        return

    def extract_sets(self, doc):
        readset = []
        writeset = []
        if doc is None:
            return readset, writeset
        for line in doc.split('\n'):
            words = line.strip().split('=')
            if words is not None:
                if words[0].strip() == 'readset':
                    chans = words[1].strip().split(',')
                    readset = filter(lambda y: y is not '',
                                     map(lambda x: x.strip(), chans))
                elif words[0].strip() == 'writeset':
                    chans = words[1].strip().split(',')
                    writeset = filter(lambda y: y is not '',
									  map(lambda x: x.strip(), chans))
                else:
                    continue
        return readset, writeset

    def is_process(self, decorators):
        for decorator in decorators:
            if (decorator.name == 'process' or
                decorator.name == 'forever'):
                return True
        return False

    def visitFunction(self, node):
#        print "VISIT FUNCTION!", dir(node)
#        print node.code.__class__
        if (node.decorators is None or
            self.is_process(node.decorators) is None):
            return
        print 'Function %s is a CSP process' % node.name
        readset, writeset = self.extract_sets(node.doc)
        print node.name, 'has readset:', readset, len(readset)
        print node.name, 'has writeset:', writeset, len(writeset)
        for channel in readset:
            if not channel in node.argnames:
                print 'ERROR line %i: Channel %s in readset is not a formal parameter to this process' % (node.lineno, channel)
        for channel in writeset:
            if not channel in node.argnames:
                print 'ERROR line %i: Channel %s in writeset is not a formal parameter to this process' % (node.lineno, channel)

        # Ensure that we visit every line of code in this function.
        for stmt in node.code:
            self.visit(stmt)

    def visitCallFunc(self, node):
        callee = node.node
        if isinstance(callee, ast.Getattr):
            if not isinstance(callee.expr, ast.Getattr):
                print 'Visiting anonymous function call %s' % callee.expr.name
#                print node
#                print dir(node)
                print callee.expr.name + '.' + callee.attrname

    # def visitAssign(self, node):
    #     print 'VISIT ASSIGN'
    #     if isinstance(node.expr, ast.CallFunc):
    #         print 'Expr details:', node.expr.node.__dict__
    #         if node.expr.node.name == 'Channel':
    #             self.channels.push(cspmodel.Channel(node.nodes[0].name))


if __name__ == '__main__':
    import sys
    
    lint = ChannelChecker()
    compiler.walk(compiler.parseFile(sys.argv[1]),
                  lint,
                  walker=lint,
                  verbose=5)

