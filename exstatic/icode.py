"""ICODE types defined in Python.

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
__date__ = ''

__all__ = ['IcodeNode', 'ETA', 'Val', 'Arith', 'Bool',
           'Prim', 'Assign', 'Call', 'Select', 'Iterate',
           'Nu', 'NameSpace', 'ParamNameSpace']


# Functions to easily print XML.

def make_tag(name, attributes):
    tag = '< {0}'.format(name)
    tag += '>'
    return tag


# ICODE types.

class IcodeNode(object):
    """Abstract base class for all ICODE types.
    """

    def __init__(self, lineno, annote):
        """
        @param lineno line number
        @param annote dictionary of annotations
        """
        self.annote = annote
        self.lineno = lineno
        return

    def _annote2xml(self):
        """Convert dict of annotations to xml.
        """
        x = '<annote lineno=' + str(self.lineno) + ' '
        for key, val in self.annote.values():
            x+= str(key) + '=' + str(val) + ' '
        return x + '/>\n'

    def xml(self):
        raise NotImplementedError

    
class ETA(IcodeNode):
    """Empty node. Can be used to represent None / null, etc.
    """

    def __init__(self, lineno, annote):
        IcodeNode.__init__(self, lineno, annote)
        return

    def xml(self):
        return '<eta>' + self._annote2xml() + '</eta>\n'

    
class Val(IcodeNode):
    """Literals and other values.
    """

    def __init__(self, lineno, val, annote):
        IcodeNode.__init__(self, lineno, annote)
        self.val = val
        return

    def xml(self):
        return '<val>' + str(self.val) + self._annote2xml() + '</val>\n'

    
class Arith(IcodeNode):
    """Arithmetic expressions.
    """

    def __init__(self, lineno, e1, e2, aop, annote):
        IcodeNode.__init__(self, lineno, annote)
        self.e1 = e1
        self.e2 = e2
        self.aop = aop
        return

    def xml(self):
        raise NotImplementedError

    
class Bool(IcodeNode):
    """Boolean expressions.
    """

    def __init__(self, lineno, e1, e2, bop, annote):
        IcodeNode.__init__(self, lineno, annote)
        self.e1 = e1
        self.e2 = e2
        self.bop = bop
        return

    def xml(self):
        raise NotImplementedError

    
class Prim(IcodeNode):
    """Statements...should rename this really.
    """

    def __init__(self, lineno, e1, e2, pop, annote):
        IcodeNode.__init__(self, lineno, e1, e2, pop, annote)
        self.e1 = e1
        self.e2 = e2
        self.pop = pop
        return

    def xml(self):
        raise NotImplementedError

    
class Assign(IcodeNode):
    """Assignments.
    """

    def __init__(self, lineno, lvalue, rvalue, annote):
        IcodeNode.__init__(self, lineno, annote)
        self.lvalue = lvalue
        self.rvalue = rvalue
        return

    def xml(self):
        icode = '<assign><lvalue>'
        icode += self.lvalue.xml()
        icode += '</lvalue>'
        icode += '<rvalue>'
        icode += self.rvalue.xml()
        icode += '</rvalue>'
        icode += self._annote2xml()
        icode += '</assign>\n'
        return icode

    
class Call(IcodeNode):
    """Calls to execute functions, closures, methods, continuations, etc.
    """

    def __init__(self, lineno, name, args, annote):
        IcodeNode.__init__(self, lineno, annote)
        self.name = name
        self.args = args
        return

    def xml(self):
        raise NotImplementedError

    
class Select(IcodeNode):
    """Selection statements.
    """

    def __init__(self, lineno, guards, annote):
        IcodeNode.__init__(self, lineno, annote)
        self.guards = guards
        return

    def xml(self):
        raise NotImplementedError

    
class Iterate(IcodeNode):
    """Iteration.
    """

    def __init__(self, lineno, guards, annote):
        IcodeNode.__init__(self, lineno, annote)
        self.guards = guards
        return

    def xml(self):
        raise NotImplementedError

    
class Nu(IcodeNode):
    """Names.
    """

    def __init__(self, lineno, n, annote):
        IcodeNode.__init__(self, lineno, annote)
        self.n = n
        return

    def xml(self):
        return ('<nu>' + str(self.n) + self._annote2xml() + '</nu>\n')

    
class NameSpace(IcodeNode):
    """Un-paramaterised name spaces.
    """

    def __init__(self, lineno, name, space, annote):
        IcodeNode.__init__(self, lineno, annote)
        self.name = name
        self.space = space # iterable of some sort
        return

    def xml(self):
        raise NotImplementedError

    
class ParamNameSpace(IcodeNode):
    """Paramaterised name spaces.
    """

    def __init__(self, lineno, name, args, space, annote):
        IcodeNode.__init__(self, lineno, annote)
        self.name = name
        self.args = args
        self.space = space # iterable of some sort
        return

    def xml(self):
        raise NotImplementedError

