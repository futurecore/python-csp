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

from __future__ import absolute_import 

import os
import multiprocessing
import threading
import time

from .csp import *


__author__ = 'Sarah Mount <s.mount@wlv.ac.uk>'
__date__ = 'May 2010'


### Names exported by this module
__all__ = ['Timer', 'Barrier']

class Timer(Guard):
    """Guard which only commits to synchronisation when a timer has expired.
    """

    def __init__(self):
        super(Timer, self).__init__()
        self.now = time.time()
        self.name = 'Timer guard created at:' + str(self.now)
        self.alarm = None

    def set_alarm(self, timeout):
        self.now = time.time()
        self.alarm = self.now + timeout
    
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
    
    def enable(self):
        pass
    
    def disable(self):
        pass

    def select(self):
        pass

    
class AbstractBarrier(object):

    def __init__(self, participants=0):
        self.participants = participants
        self.not_ready = participants
        self.lock = None # MUST be overridden in subclass
        self.reset(participants)

    def reset(self, participants):
        assert participants >= 0
        with self.lock:
            self.participants = participants
            self.not_ready = participants

    def enrol(self):
        with self.lock:
            self.participants += 1
            self.not_ready += 1

    def retire(self):
        with self.lock:
            self.participants -= 1
            self.not_ready -= 1
            if self.not_ready == 0:
                self.not_ready = self.participants
                self.lock.notifyAll()
            assert self.not_ready >= 0

    def synchronise(self):
        with self.lock:
            self.not_ready -= 1
            if self.not_ready > 0:
                self.lock.wait()
            else:
                self.not_ready = self.participants
                self.lock.notifyAll()

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


# TODO: Move these two classes to the modules corresponding to
# their CSP process implementation (i. e. os_process/os_thread).

class BarrierThreading(AbstractBarrier):

    def __init__(self):
        super(BarrierThreading, self).__init__()
        self.lock = threading.Condition()


class BarrierProcessing(AbstractBarrier):

    def __init__(self):
        super(BarrierProcessing, self).__init__()
        self.lock = multiprocessing.Condition()


# FIXME: This is no longer always work.
# FIXME: Add a function in csp/csp.py to tell you which version of the
# library you are using.
if 'CSP' in os.environ:
    if os.environ['CSP'] == 'PROCESSES':
        Barrier = BarrierProcessing
    elif os.environ['CSP'] == 'THREADS':
        Barrier = BarrierThreading
    else:
        Barrier = BarrierProcessing
else:
    Barrier = BarrierProcessing
