#!/usr/bin/env python

"""
Builtin guard types. For builtin processes see csp.builtins.

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
__date__ = 'May 2010'


import os
import multiprocessing
import threading
import time

if os.environ.has_key('CSP'):
    if os.environ['CSP'] == 'PROCESSES':
        from csp.cspprocess import *
    elif os.environ['CSP'] == 'THREADS':
        from csp.cspthread import *
    else:
        from csp.cspprocess import *
else:
    from csp.cspprocess import *   


### Names exported by this module
__all__ = ['Skip', 'Timer', 'Barrier']


class Skip(Guard):
    """Guard which will always return C{True}. Useful in L{Alt}s where
    the programmer wants to ensure that L{Alt.select} will always
    synchronise with at least one guard.
    """

    def __init__(self):
        Guard.__init__(self)
        self.name = None
        return

    def is_selectable(self):
        """Skip is always selectable."""
        return True

    def enable(self):
        """Has no effect."""
        return

    def disable(self):
        """Has no effect."""
        return

    def select(self):
        """Has no effect."""
        return 'Skip'

    def __str__(self):
        return 'Skip guard is always selectable.'


class Timer(Guard):
    """Guard which only commits to synchronisation when a timer has expired.
    """

    def __init__(self):
        super(Timer, self).__init__()
        self.now = time.time()
        self.name = 'Timer guard created at:' + str(self.now)
        self.alarm = None
        return

    def set_alarm(self, timeout):
        self.now = time.time()
        self.alarm = self.now + timeout
        return
    
    def is_selectable(self):
        self.now = time.time()
        if self.alarm is None:
            return True
        elif self.now < self.alarm:
            return False
        return True

    def read(self):
        """Return current time.
        """
        self.now = time.time()
        return self.now

    def sleep(self, timeout):
        """Put this process to sleep for a number of seconds.
        """
        time.sleep(timeout)
        return
    
    def enable(self):
        return
    
    def disable(self):
        return

    def select(self):
        return

    
class AbstractBarrier(object):

    def __init__(self, participants=0):
        self.participants = participants
        self.not_ready = participants
        self.lock = None # MUST be overridden in subclass
        self.reset(participants)
        return

    def reset(self, participants):
        assert participants >= 0
        with self.lock:
            self.participants = participants
            self.not_ready = participants
        return

    def enrol(self):
        with self.lock:
            self.participants += 1
            self.not_ready += 1
        return

    def retire(self):
        with self.lock:
            self.participants -= 1
            self.not_ready -= 1
            if self.not_ready == 0:
                self.not_ready = self.participants
                self.lock.notifyAll()
            assert self.not_ready >= 0
        return

    def synchronise(self):
        with self.lock:
            self.not_ready -= 1
            if self.not_ready > 0:
                self.lock.wait()
            else:
                self.not_ready = self.participants
                self.lock.notifyAll()
        return

    def synchronise_withN(self, n):
        """Only syncrhonise when N participants are enrolled.
        """
        with self.lock:
            if self.participants != n:
                self.lock.wait()
            self.not_ready -= 1
            if self.not_ready > 0:
                self.lock.wait()
            else:
                self.not_ready = self.participants
                self.lock.notifyAll()
        return


class BarrierThreading(AbstractBarrier):

    def __init__(self):
        super(BarrierThreading, self).__init__()
        self.lock = threading.Condition()
        return


class BarrierProcessing(AbstractBarrier):

    def __init__(self):
        super(BarrierProcessing, self).__init__()
        self.lock = multiprocessing.Condition()
        return


if os.environ.has_key('CSP'):
    if os.environ['CSP'] == 'PROCESSES':
        Barrier = BarrierProcessing
    elif os.environ['CSP'] == 'THREADS':
        Barrier = BarrierThreading
    else:
        Barrier = BarrierProcessing
else:
    Barrier = BarrierProcessing
