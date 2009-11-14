#!/bin/env python2.6

"""
Bulk synchronous processing primitives for Python.

TODO: Add Buckets (due to Welch + Kerridge)

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
 
from __future__ import with_statement

__author__ = 'Sarah Mount <s.mount@wlv.ac.uk>'
__date__ = 'November 2009'

import threading

# Multiprocessing libary -- name changed between versions.
try:
    # Version 2.6 and above
    import multiprocessing as processing
except ImportError:
    raise ImportError('No library available for multiprocessing.\n'+
                      'bsp.Barrier is only compatible with Python 2. 6 and above.')

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
        self.lock = processing.Condition()
        return

