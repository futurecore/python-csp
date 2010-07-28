#!/usr/bin/env python

"""
Visitor pattern for ICODE.

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
__date__ = '2010-05-16'


# Names exported by this module
__all__ = ['IcodeVisitor', 'ExampleIcodeVisitor', 'GraphIcodeVisitor']


class IcodeVisitor:
    """Performs a depth-first walk of an ICODE tree.

    Largely taken from compiler.visitor in the Python2.6 distribution.

    The IcodeVisitor will walk an ICODE tree, performing either a
    preorder or postorder traversal depending on which method is
    called.

    methods:
    preorder(tree, visitor)
    postorder(tree, visitor)
        tree: an instance of ast.Node
        visitor: an instance with visitXXX methods

    The IcodeVisitor is responsible for walking over the tree in the
    correct order.  For each node, it checks the visitor argument for
    a method named 'visitNodeType' where NodeType is the name of the
    node's class, e.g. Class.  If the method exists, it is called
    with the node as its sole argument.

    The visitor method for a particular node type can control how
    child nodes are visited during a preorder walk.  (It can't control
    the order during a postorder walk, because it is called _after_
    the walk has occurred.)  The ASTVisitor modifies the visitor
    argument by adding a visit method to the visitor; this method can
    be used to visit a child node of arbitrary type.
    """

    VERBOSE = 0

    def __init__(self):
        self.node = None
        self._cache = {}

    def default(self, node, *args):
        for child in node.getChildNodes():
            self.dispatch(child, *args)

    def dispatch(self, node, *args):
        self.node = node
        klass = node.__class__
        meth = self._cache.get(klass, None)
        if meth is None:
            className = klass.__name__
            meth = getattr(self.visitor, 'visit' + className, self.default)
            self._cache[klass] = meth
        return meth(node, *args)

    def preorder(self, tree, visitor, *args):
        """Do preorder walk of tree using visitor"""
        self.visitor = visitor
        visitor.visit = self.dispatch
        self.dispatch(tree, *args)


class ExampleIcodeVisitor(IcodeVisitor):
    """Prints examples of the nodes that aren't visited

    This visitor-driver is only useful for development, when it's
    helpful to develop a visitor incrementally, and get feedback on what
    you still have to do.
    """
    examples = {}

    def dispatch(self, node, *args):
        self.node = node
        meth = self._cache.get(node.__class__, None)
        className = node.__class__.__name__
        if meth is None:
            meth = getattr(self.visitor, 'visit' + className, 0)
            self._cache[node.__class__] = meth
        if self.VERBOSE > 1:
            print ( "dispatch", className, (meth and meth.__name__ or '') )
        if meth:
            meth(node, *args)
        elif self.VERBOSE > 0:
            klass = node.__class__
            if klass not in self.examples:
                self.examples[klass] = klass
                print ( )
                print ( self.visitor )
                print ( klass )
                for attr in dir(node):
                    if attr[0] != '_':
                        print ( "\t", "{0}-12.12s".format(attr), getattr(node, attr) )
                print ( )
            return self.default(node, *args)


class GraphVisitor(IcodeVisitor):
    """Visitor which produces a Graphviz representation of the Icode
    tree.
    """

    def __init__(self):
        self.num = 0
        return

    def visitETA(self, node):
        pass

    def visitVal(self, node):
        pass

    def visitArith(self, node):
        pass

    def visitBool(self, node):
        pass

    def visitPrim(self, node):
        pass

    def visitAssign(self, node):
        pass

    def visitCall(self, node):
        pass

    def visitSelect(self, node):
        pass

    def visitIterate(self, node):
        pass

    def visitNu(self, node):
        pass

    def visitNameSpace(self, node):
        pass

    def visitParamNameSpace(self, node):
        pass
        

_walker = IcodeVisitor
def walk(tree, visitor, walker=None, verbose=None):
    if walker is None:
        walker = _walker()
    if verbose is not None:
        walker.VERBOSE = verbose
    walker.preorder(tree, visitor)
    return walker.visitor


# class CopyAndPasteVisitor(IcodeVisitor):

#     def __init__(self):
#         return

#     def visitETA(self, node):
#         pass

#     def visitVal(self, node):
#         pass

#     def visitArith(self, node):
#         pass

#     def visitBool(self, node):
#         pass

#     def visitPrim(self, node):
#         pass

#     def visitAssign(self, node):
#         pass

#     def visitCall(self, node):
#         pass

#     def visitSelect(self, node):
#         pass

#     def visitIterate(self, node):
#         pass

#     def visitNu(self, node):
#         pass

#     def visitNameSpace(self, node):
#         pass

#     def visitParamNameSpace(self, node):
#         pass
        
