#!/usr/bin/env python

"""Primitives for forking.

Should not be used outside of this package.

TODO: Write a Windows version of this file
TODO: http://sourceforge.net/projects/pywin32/
TODO: http://msdn.microsoft.com/en-us/library/ms810613.aspx
TODO: http://docs.python.org/library/mmap.html

Copyright (C) Sarah Mount, 2008-12.

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
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
02110-1301, USA
"""

__author__ = 'Sarah Mount <s.mount@wlv.ac.uk>'
__date__ = '2012-01-04'

# pylint: disable-msg=W0102
# pylint: disable-msg=W0212

import os
import signal
import sys

class Process(object):
    """Operating system process that can fork().

    This class is a superclass to the CSPProcess, Par and Seq classes.
    """
    def __init__(self, target=None, args=(), kwargs={}):
        self._started = False
        self._pid = None
        self._parent_pid = os.getpid()
        self._target = target
        self._args = tuple(args)
        self._kwargs = dict(kwargs)
        self._returncode = None
        return

    def getPid(self):
        return self._pid

    def run(self):
        self._target(*self._args, **self._kwargs)        
        return
    
    def start(self):
        self._started = True
        self._pid = os.fork()
        if self._pid == 0:
            try:
                self.run()
                os._exit(0)
            except KeyboardInterrupt:
                sys.exit()
        return
    
    def wait(self):
        if self._pid == 0 or not self._started: return
        try:
            _, self._returncode = os.wait()
        except os.error: # Child process not created
            pass
        return self._returncode

    def send_signal(self, sig):
        """Send a signal to the process
        """
        if self._returncode is not None:
            os.kill(self._pid, sig)
        return

    def terminate(self):
        """Terminate the process with SIGTERM
        """
        if self._started and self._returncode is not None:
            self.send_signal(signal.SIGTERM)
        return

    def kill(self):
        """Kill the process with SIGKILL
        """
        if self._started and self._returncode is not None:
            self.send_signal(signal.SIGKILL)
        return
