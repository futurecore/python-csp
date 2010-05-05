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

You should have rceeived a copy of the GNU General Public License
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

    def visitFunction(self, node):
#        print "VISIT FUNCTION!"
#        print node.__dict__.keys()
        if node.decorators is not None:
            for name in node.decorators:
                if name.name == 'process' or name.name == 'forever':
#                    self.processes.push(cspmodel.Process(node.name))
                    print 'Function %s is a CSP process' % node.name
                else: print 'Function %s is NOT a CSP process' % node.name

    # def visitAssign(self, node):
    #     print 'VISIT ASSIGN'
    #     if isinstance(node.expr, ast.CallFunc):
    #         print 'Expr details:', node.expr.node.__dict__
    #         if node.expr.node.name == 'Channel':
    #             self.channels.push(cspmodel.Channel(node.nodes[0].name))

    def visitCallFunc(self, node):
        callee = node.node
        print dir(callee)
        try:
            print 'Visiting function call %' % callee.name
        except:
            try:
                print 'Visiting anonymous function call %s' % callee.expr
            except:
                pass
 #       print 'CALL:', node.node.attrname
 #       print node.node.expr
        # CALL: start
        # CallFunc(Name('Par'), [CallFunc(Name('foo'), [Const(100), Name('mychan')], None, None),
        #                        CallFunc(Name('bar'), [Name('mychan')], None, None)], None, None)
        


if __name__ == '__main__':
    import sys
    
    lint = ChannelChecker()
    compiler.walk(compiler.parseFile(sys.argv[1]),
                  lint,
                  walker=lint,
                  verbose=5)

