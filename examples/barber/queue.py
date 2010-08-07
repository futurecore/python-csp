#!/usr/bin/env python

"""
This is a python-csp implementation of the Kamaelia box, based on
Michael Spark's OCCAM code: http://pastebin.com/B1kqx88G

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
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


__author__ = 'Sarah Mount <s.mount@wlv.ac.uk>'
__date__ = 'July 2010'


import logging
import os

from csp.csp import *
from csp.builtins import Generate, Printer


import random
_RANGEN = random.Random(os.urandom(16))


class GuardedAlt(Alt):
    """Guarded selection, as in OCCAM.

    In this form of ALTing, the GuardedAlt object is passed a list of
    callable / Guard (usually Channel) pairs. When select is called,
    the result is usually the result of a Channel read from a channel
    which has a waiting writer, for which the corresponding callable
    evaluates to True.

    For example:

        x = 3
        alt = Alt((lambda x > 3, c1), (lambda x : x <= 3, c2))
        print alt.select()

    will print the result of reading from c2 as soon as c2 is blocked
    on the offer of a channel write.
    
    Maybe this should be the default implementation of Alting? A great
    deal of code is shared between the Alt class and GuardedAlt. I
    have left this in, for backwards compatibility and efficiency, but
    it should probably be looked at again.
    """
    def __init__(self, *args):
        super(GuardedAlt, self).__init__()
        for (call, guard) in args:
            assert callable(call)
            assert isinstance(guard, Guard)
        self.guards = list(args)
        self.last_selected = None
        # These two should not be needed, but they should be bound to
        # a sensible method, since they would otherwise be inherited
        # from Alt.
        self.fair_select = self.select
        self.pri_select = self.select

    def poison(self):
        """Poison the last selected guard and unlink from the guard list.

        Sets self.last_selected to None.
        """
        logging.debug(str(type(self.last_selected)))
        self.last_selected.disable() # Just in case
        try:
            self.last_selected.poison()
        except Exception:
            pass
        logging.debug('Poisoned last selected.')
        self.guards.remove(self.last_selected)
        logging.debug('{0} guards'.format(len(self.guards)))
        self.last_selected = None

    def _preselect(self):
        """Check for special cases when any form of select() is called.
        """
        if len(self.guards) == 0:
            raise NoGuardInAlt()
        elif len(self.guards) == 1:
            call, guard = self.guards[0]
            logging.debug('Alt Selecting unique guard: {0}'.format(guard.name))
            self.last_selected = guard
            while not (call() and guard.is_selectable()):
                guard.enable()
            return guard.select()
        return None

    def select(self):
        """Randomly select from ready guards."""
        if len(self.guards) < 2:
            return self._preselect()
        ready = []
        while len(ready) == 0:
            for (call, guard) in self.guards:
                guard.enable()
            for (call, guard) in self.guards:
                if call() and guard.is_selectable():
                    ready.append(guard)
            logging.debug('Alt got {0} items to choose from out of {1}'.format(len(ready), len(self.guards)))
        selected = _RANGEN.choice(ready)
        self.last_selected = selected
        for call, guard in self.guards:
            if guard is not selected:
                guard.disable()
        return selected.select()
    

@process
def BoundedQueue(cin, cout, maxsize):
    """Port of Michael Spark's OCCAM code.
    """
    
    @process
    def inproc(chan_in, chan_next, chan_pass):
        queue = []
        alt = GuardedAlt((lambda : len(queue) < maxsize, chan_in),
                         (lambda : len(queue) > 0, chan_next))
        while True:
            msg = alt.select()
            if alt.last_selected == chan_in:
                queue.append(msg)
                print 'QUEUE:', queue # Bad style
            elif alt.last_selected == chan_next:
                chan_pass.write(queue[0])
                queue = queue[1:]

    @process
    def outproc(chan_next, chan_pass, chan_out):
        while True:
            chan_next.write("ANY")
            msg = chan_pass.read()
            chan_out.write(msg)
    
    chan_pass, chan_next = Channel(), Channel()
    Par(inproc(cin, chan_next, chan_pass),
        outproc(chan_next, chan_pass, cout)).start()
    

@process
def test_queue():
    @process
    def source(cout, n=15):
        for i in xrange(n):
            cout.write(i)
        cout.poison()

    cin, cout = Channel(), Channel()
    Par(source(cin), BoundedQueue(cin, cout, 5), Printer(cout)).start()
    return


@process
def test_alt(cout1, cout2):
    alt = Alt(cout1)           # Simplest case, should act like read.
#    alt = Alt(cout1, cout2)   # Basic test.
#    alt = GuardedAlt((lambda: True, cout1), (lambda: True, cout))
    while True:
        print alt.select()


@process
def test_runner():
    chan1, chan2 = Channel(), Channel()
    Par(Generate(chan1), Generate(chan2), test_alt(chan1, chan2)).start()

if __name__ == '__main__':
#    set_debug(True)
    test_runner().start()
#    test_queue().start()
