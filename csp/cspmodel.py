#!/usr/bin/env python

"""
Simple representation of CSP models, with graphviz and FDR2 output.

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
__date__ = 'April 2010'


class CSPModel(object):

    def __init__(self):
        return

    def fdr(self):
        """Generate a variant of this CSP model to a text file.
        Should be suitable for using as an input to the FDR2 tool.

        MUST be overridden in subclasses.
        """
        raise Exception('fdr() MUST be overridden in subclasses.')

    def dot(self):
        """Generate a variant of this CSP model to a text file.
        Should be suitable for using as an input to the graphiz toolset.

        MUST be overridden in subclasses.
        """
        raise Exception('fdr() MUST be overridden in subclasses.')



class Process(CSPModel):

    def __init__(self, name):
        CSPModel.__init__(self)
        self.name = name

    def fdr(self):
        # WRONG, this should be a definition
        return self.name.upper()

    
class Par(CSPModel):

    def __init__(self, procs):
        CSPModel.__init__(self)
        self.procs = procs

    def fdr(self):
        if len(self.procs) == 0:
            return ''
        fdr_string = self.procs[0].fdr()
        for proc in self.procs[1:]:
            fdr_string += ' ||| ' + proc
        return fdr_string


class Seq(CSPModel):

    def __init__(self, procs):
        CSPModel.__init__(self)
        self.procs = procs
        return

    def fdr(self):
        if len(self.procs) == 0:
            return ''
        fdr_string = self.procs[0].fdr()
        for proc in self.procs[1:]:
            fdr_string += ' ; ' + proc
        return fdr_string


class Channel(CSPModel):

    def __init__(self, name):
        CSPModel.__init__(self)
        self.name = name
        return

    def fdr(self):
        return 'channel ' + self.name + '\n'
    

class Alt(CSPModel):

    def __init__(self):
        CSPModel.__init__(self)


if __name__ == '__main__':
    print 'WRITE SOME TESTS'
 
