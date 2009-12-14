#!/usr/bin/env python2.6

"""
Tracer for python-csp generating a process graph with graphviz.

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
__date__ = 'June 2009'

from csp.cspprocess import *
#import inspect
import os
import sys

context = [] # Stack.
nodes = []
arcs = {}

def start_trace():
    """Start the tracer."""
    sys.settrace(tracer)

def stop_trace():
    """Stop the tracer."""
    sys.settrace(None)
    
def tracer(frame, event, arg):
    """Tracer for python-csp. Collect information to construct a
    process graph.
    """
    global context        # Name of each caller. Should be a stack.
    global nodes
    global arcs
    rho = {}
    if event == 'call':
        code = frame.f_code
        callee = code.co_name
        if callee == '?':
            callee = '__main__'
        print 'CALLEE: %s' % callee
        context.append(callee)
        print 'LOCALS:', frame.f_locals
        try:
            klass = frame.f_locals['self'].__class__.__name__
            print 'CLASS: %' % klass
        except Exception, e:
            klass = None
        if klass:
            if 'csp.CSPProcess' == klass:
                context.append(callee)
                for local in frame.f_locals:
                    kls = local.__class__.__name__
                    if ('csp.Channel' == kls or
                        'csp.FileChannel' == kls or
                        'csp.NetworkChannel' == kls):
                        rho[context[-1]] = local
                    else: pass
            else: pass
    elif event == 'return':
        context.pop()
    else: pass
    return tracer

def write_dotfile(filename='procgraph.dot'):
    """
    """
    global nodes
    global arcs
    dot = "graph pythoncsp {\n  node [shape=ellipse];"
    for proc in nodes:
        dot += " " + str(proc) + ";"
    dot += "\n"
    for channel in arcs:
        for i in xrange(len(arcs[channel])):
            for j in xrange(i+1, len(arcs[channel])):
                dot += (str(arcs[channel][i]) + " -- " +
                        str(arcs[channel][j]) +
                        "  [ label=" + str(channel) + " ];\n")
    dot += '  label = "\\n\\nCSP Process Relationships\\n";\n'
    dot += "  fontsize=20;\n}"
    fh = open(filename)
    fh.write(dot)
    fh.close()
    return

def write_png(infile='procgraph.dot', outfile='procgraph.png'):
    os.system('neato -v -Goverlap=-1 -Gsplines=true -Gsep=.1 -Gstart=-1000 Gepsilon=.0000000001 -Tpng ' + infile + ' -o' + outfile)

if __name__ == '__main__':
    pass
