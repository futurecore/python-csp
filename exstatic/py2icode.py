#!/usr/bin/env python

"""
py2icode.py produces an ICODE representation of a Python file.

Usage: py2icode.py <in_file> ?<out_file>

<in_file> should be a python file for processing. The full path is not
needed.  <out_file> is the name of the file which should store the
ICODE translation of <in_file>.  If no name is given STDOUT is used.
"""

__author__ = 'Sarah Mount <s.mount@coventry.ac.uk>'
__date__ = '2010-05-16'


DEBUG = True

import ast, sys
from pyicode import *

__all__ = ['Ast2IcodeVisitor']

class Ast2IcodeVisitor(ast.NodeTransformer):
    """
    AST Visitor which creates an ICODE translation of the AST, stored
    in its icode attribute.
    """
    def __init__(self):
        super(AST2ICODEVisitor, self)
        self.icode = '' # BAH

    def vist_Function(self, node):
        pass
        
        
#    def default(self, node):
#        """Gives debug info in place of unwritten visit methods."""
#        self.generic_visit(node)
#        return node
#         self.icode += "\nDEBUG: START NODE\n"
#         self.icode += '\t__repr__:' + node.__repr__() + '\n'
#         self.icode += '\t__dict__:' + str(node.__dict__) + '\n'
#         self.icode += "DEBUG: END NODE\n"


if __name__ == '__main__':
    if DEBUG: print ( 'Debugging: ON. Script arguments:' + str ( sys.argv ) )
    # Determine the input file.
    if len(sys.argv) == 1: 
        print ( 'You must specify a Python file for processing.' )
        sys.exit(1)
    else:
        i_file = sys.argv[1]
    # Determine the output file. Use sys.stdout if none specified.
    if len(sys.argv) > 2: 
        o_file = sys.argv[2]
        o_fd = open(sys.argv[2], 'w')
        if DEBUG: print ( 'Output file:' + str ( sys.argv[2] ) )
    else:
        if DEBUG: print ( 'Using STDOUT for output.' )
        o_file = ''
        o_fd = sys.stdout
    # This is the important stuff.
    infile = open(i_file).read()
    tree = compile(infile, '<string>', 'exec')#, ast.PyCF_ONLY_AST)
    outtree = AST2ICODEVisitor().visit(tree)
    o_fd.write(outtree.xml())
    if not o_file == '':
        o_fd.close()
    # ...end of important stuff.

####################################################################
#                          SCRATCH SPACE                           #
####################################################################
#
#        self.icode += "\tSTART CHILD NODES\n"
#        for i in node.getChildNodes():
#            self.icode += '\t\t__repr__:' + i.__repr__() + '\n'
#            self.icode += '\t\t__dict__:' + str(i.__dict__) + '\n'
#            self.dispatch(i)
#        self.icode += "\tEND CHILD NODES\n"



############# SCRATCH
    # def visit_Const(self, node):
    #     self.generic_visit(node)
    #     return IcodeConst(node.value, lineno=node.lineno)

    # def visit_Assign(self, node):
    #     print 'ASSIGN'
    #     for key,val in node.__dict__.items():
    #         print key, val
    #     print 'END'
    #     self.generic_visit(node)
    #     return IcodeAssign(node.nodes, node.expr, lineno=node.lineno)

    # def visit_Import(self, node):
    #     self.generic_visit(node)
    #     return IcodeImport(node.names)

    
