#!/usr/bin/env python

"""
If you want to use the python-csp library then this is the file to
import. It attempts to match the best possible implementation of CSP
for your platform.

If you wish to choose to use the multiprocess (multicore) or threaded
version of the libraries explicitly then set an environment variable
in your opertaing system called "CSP". This should be either set to
"PROCESSES" or "THREADS" depending on what you want to use.


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
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
"""

from __future__ import absolute_import 

from contextlib import contextmanager

import os
import sys


### Names exported by this module
__all__ = ['set_debug', 'CSPProcess', 'CSPServer', 'Alt',
           'Par', 'Seq', 'Guard', 'Channel', 'FileChannel',
           'process', 'forever', 'Skip', 'CSP_IMPLEMENTATION']


__author__ = 'Sarah Mount <s.mount@wlv.ac.uk>'
__date__ = 'July 2010'


# FIXME: Simplify this logic. See the thread on "Importing different
# implementations of the library" on the mailing list.

# If multiprocessing is not available then import threads.
major, minor = sys.version_info[:2]
if (major, minor) < (2, 6):
    try:
        from .os_thread import *
    except:
        from .os_process import *

# If multiprocessing is likely to be available then let the user
# choose which version of the implementation they wish to use.
elif 'CSP' in os.environ:
    if os.environ['CSP'].upper() == 'THREADS':
        from .os_thread import *
    else:
        from .os_process import *

# If no useful information is available then try to import the
# multiprocessing version of the code else catch the resulting
# exception and use the threaded version.
else: 
    try:
        from .os_process import *
    except:
        from .os_thread import *



class CSP(object):
    """Context manager to execute Python functions sequentially or in
    parallel, similarly to OCCAM syntax:

    csp = CSP()
    with csp.seq:
        csp.process(myfunc1, arg1, arg2)
        with csp.par:
            csp.process(myfunc2, arg1, arg2)
            csp.process(myfunc3, arg1, arg2)
    csp.start()    
    # myfunc3 and myfunc4 will be executed in parallel.
    # myfunc1 and myfunc2 will be executed sequentially,
    # and myfunc3 and myfunc4 will be executed after
    # myfunc2 has returned.
    """

    def __init__(self):
        self.processes = []
     
    @contextmanager
    def par(self):
        """Context manager to execute functions in parallel.

        csp = CSP()
        with csp.seq:
            csp.process(myfunc1, arg1, arg2)
            csp.process(myfunc2, arg1, arg2)
        csp.start()
        # myfunc1 and myfunc2 will be executed in parallel.
        """
        self.processes.append([])
        yield
        proc_list = self.processes.pop()
        par = Par(*proc_list)
        if len(self.processes) > 0:
            self.processes[-1].append(par)
        else:
            self.processes.append(par)
        return

    @contextmanager
    def seq(self):
        """Context manager to execute functions in sequence.

        csp = CSP()
        with csp.seq:
            csp.process(myfunc1, arg1, arg2)
            csp.process(myfunc2, arg1, arg2)
        csp.start()
        # myfunc1 and myfunc2 will be executed sequentially.
        """
        self.processes.append([])
        yield
        proc_list = self.processes.pop()
        seq = Seq(*proc_list)
        if len(self.processes) > 0:
            self.processes[-1].append(seq)
        else:
            self.processes.append(seq)
        return

    def process(self, func, *args, **kwargs):
        """Add a process to the current list of proceses.

        Likely, this will be called from inside a context manager, e.g.:

        csp = CSP()
        with csp.par:
            csp.process(myfunc1, arg1, arg2)
            csp.process(myfunc2, arg1, arg2)
        csp.start()
        """
        self.processes[-1].append(CSPProcess(func, *args, **kwargs))
        return

    def start(self):
        """Start all processes in self.processes (in parallel) and run
        to completion.
        """
        if len(self.processes) == 0:
            return
        elif len(self.processes) == 1:
            self.processes[0].start()
        else:
            Par(*self.processes).start()
        return
