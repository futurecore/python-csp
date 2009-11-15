#!/usr/bin/env python

"""Communicating sequential processes, in Python.

When using CSP Python as a DSL, this module will normally be imported
via the statement 'from csp.csp import *'. For that reason this module
imports all names from the csp.builtins module (and therefore that
module should not normally be imported by client code).

Copyright (C) Sarah Mount, 2009.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A ParTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have rceeived a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
"""

from __future__ import with_statement

__author__ = 'Sarah Mount <s.mount@wlv.ac.uk>'
__date__ = 'June 2009'

#DEBUG = True
DEBUG = False


def _debug(*args):
    """Customised debug logging.

    FIXME: Replace this with the builtin logging module.
    """
    smap = map(str, args)
    if DEBUG:
        print 'DEBUG:', ' '.join(smap)

from functools import wraps # Easy decorators

# Import barrier from bulk synchronous processing library
from bsp.bsp import BarrierThreading as Barrier

# Import channels for this version of the library
from threadchannels import *

import inspect
import operator
import os
import random
import sys
import threading
import time


try: # Python optimisation compiler
    import psyco
    psyco.full()
except ImportError:
    print 'No available optimisation'


### Seeded random number generator (16 bytes)

_RANGEN = random.Random(os.urandom(16))


class NoGuardInAlt(Exception):
    """Raised when an Alt has no guards to select.
    """

    def __init__(self):
        super(NoGuardInAlt, self).__init__()
        return

    def __str__(self):
        return 'Every Alt must have at least one guard.'


class ProcessSuspend(Exception):
    """Used to suspend a process.
    """

    def __init__(self):
        super(ProcessSuspend, self).__init__()
        return

    def __str__(self):
        return 'Process suspend exception.'

### Fundamental CSP concepts -- Processes, Channels, Guards

class CSPOpMixin(object):
    """Mixin class used for operator overloading in CSP process types.
    """

    def __init__(self):
        return

    def spawn(self):
        """Start only if self is not running."""
        if not self._Thread__started.is_set():
            threading.Thread.start(self)
        return

    def start(self, timeout=None):
        """Start only if self is not running."""
        if not self._Thread__started.is_set():
            threading.Thread.start(self)
            threading.Thread.join(self, timeout)

    def join(self, timeout=None):
        """Join only if self is running and impose a timeout."""
        if self._Thread__started.is_set():
            threading.Thread.join(self, timeout)

    def referent_visitor(self, referents):
        for obj in referents:
            if obj is self or obj is None:
                continue
            if isinstance(obj, Channel):
                obj.poison()
            elif ((hasattr(obj, '__getitem__') or hasattr(obj, '__iter__')) and
                  not isinstance(obj, basestring)):
                self.referent_visitor(obj)
            elif isinstance(obj, CSPProcess):
                self.referent_visitor(obj.args + tuple(obj.kwargs.values()))
            elif hasattr(obj, '__dict__'):
                self.referent_visitor(obj.__dict__.values())
		return

    def terminate(self):
        """Terminate only if self is running.

        FIXME: This doesn't work yet...
        """
        if self._Thread__started.is_set():
            _debug(str(self.getName()), 'terminating now...')
            return #threading.Thread._Thread__stop(self) # Sets an event object

    def __and__(self, other):
        """Implementation of CSP Par.

        Requires timeout with a small value to ensure
        parallelism. Otherwise a long sequence of '&' operators will
        run in sequence (because of left-to-right evaluation and
        orders of precedence.
        """
        assert _is_csp_type(other)
        par = Par(other, self, timeout = 0.1)
        par.start(timeout = 0.1)
        return par

    def __gt__(self, other):
        """Implementation of CSP Seq."""
        assert _is_csp_type(other)
        seq = Seq(self, other)
        seq.start(timeout = 0.1)
        return seq

    def __mul__(self, n):
        assert n > 0
        clone = None
        for i in xrange(n):
            clone = copy.copy(self)
            clone.start()
        return

    def __rmul__(self, n):
        assert n > 0
        clone = None
        for i in xrange(n):
            clone = copy.copy(self)
            clone.start()
        return


class CSPProcess(threading.Thread, CSPOpMixin):
    """Implementation of CSP processes.
    Not intended to be used in client code. Use @process instead.
    """

    def __init__(self, func, *args, **kwargs):
        threading.Thread.__init__(self,
                                  target=func,
                                  args=(args),
                                  kwargs=kwargs)
        assert inspect.isfunction(func) # Check we aren't using objects
        assert not inspect.ismethod(func) # Check we aren't using objects
        
        CSPOpMixin.__init__(self)

        for arg in list(args) + kwargs.values():
            if _is_csp_type(arg):
                arg.enclosing = self
        # Add a ref to this process so _target can access the
        # underlying operating system process.
        self._Thread__kwargs['_process'] = self
        self.enclosing = None
        return

    def getPid(self):
        """Return thread ident.

        The name of this method ensures that the CSPProcess interface
        in this module is identical to the one defined in
        cspprocess.py.
        """
        return self.ident

    def __str__(self):
        return 'CSPProcess running in TID %s' % self.getName()

    def run(self): #, event=None):
        """Called automatically when the L{start} methods is called.
        """
        try:
            self._Thread__target(*self._Thread__args, **self._Thread__kwargs)
        except ChannelPoison:
            _debug(str(self), 'in', self.getPid(), 'got ChannelPoison exception')
            self.referent_visitor(self._Thread__args +
	    						  tuple(self._Thread__kwargs.values()))
        except ProcessSuspend:
            raise NotImplementedError('Process suspension not yet implemented')
        except Exception:
            typ, excn, tback = sys.exc_info()
            sys.excepthook(typ, excn, tback)


### CSP combinators -- Par, Alt, Seq, ...

class Alt(CSPOpMixin):
    """CSP select (OCCAM ALT) process.

    What should happen if a guard is poisoned?
    """

    def __init__(self, *args):
        super(Alt, self).__init__()
        for arg in args:
            assert isinstance(arg, Guard)
        self.guards = list(args)
        self.last_selected = None

    def poison(self):
        """Poison the last selected guard and unlink from the guard list.

        Sets self.last_selected to None.
        """
        _debug(type(self.last_selected))
        self.last_selected.disable() # Just in case
        try:
            self.last_selected.poison()
        except:
            pass
        _debug('Poisoned last selected.')
        self.guards.remove(self.last_selected)
        _debug('%i guards' % len(self.guards))
        self.last_selected = None

    def _preselect(self):
        """Check for special cases when any form of select() is called.
        """
        if len(self.guards) == 0:
            raise NoGuardInAlt()
        elif len(self.guards) == 1:
            _debug('Alt Selecting unique guard:', self.guards[0].name)
            self.last_selected = self.guards[0]
            self.guards[0].enable()
            while not self.guards[0].is_selectable():
                time.sleep(0.01)
            return self.guards[0].select()
        return None

    def select(self):
        """Randomly select from ready guards."""
        if len(self.guards) < 2:
            return self._preselect()
        for guard in self.guards:
            guard.enable()
        _debug('Alt enabled all guards')
        ready = [guard for guard in self.guards if guard.is_selectable()]
        while len(ready) == 0:
            time.sleep(0.01) # Not sure about this.
            ready = [guard for guard in self.guards if guard.is_selectable()]
            _debug('Alt got no items to choose from')
        _debug('Alt got %i items to choose from' % len(ready))
        selected = _RANGEN.choice(ready)
        self.last_selected = selected
        for guard in self.guards:
            if guard is not selected:
                guard.disable()
        return selected.select()

    def fair_select(self):
        """Select a guard to synchronise with. Do not select the
        previously selected guard (unless it is the only guard
        available).
        """
        if len(self.guards) < 2:
            return self._preselect()
        for guard in self.guards:
            guard.enable()
        _debug('Alt enabled all guards')
        ready = [guard for guard in self.guards if guard.is_selectable()]
        while len(ready) == 0:
            time.sleep(0.1) # Not sure about this.
            ready = [guard for guard in self.guards if guard.is_selectable()]
        _debug('Alt got %i items to choose from' % len(ready))
        selected = None
        if self.last_selected in ready and len(ready) > 1:
            ready.remove(self.last_selected)
            _debug('Alt removed last selected from ready list')
        selected = _RANGEN.choice(ready)
        self.last_selected = selected
        for guard in self.guards:
            if guard is not selected:
                guard.disable()
        return selected.select()

    def pri_select(self):
        """Select a guard to synchronise with, in order of
        "priority". The guard with the lowest index in the L{guards}
        list has the highest priority.
        """
        if len(self.guards) < 2:
            return self._preselect()
        for guard in self.guards:
            guard.enable()
        _debug('Alt enabled all guards')
        ready = [guard for guard in self.guards if guard.is_selectable()]
        while len(ready) == 0:
            time.sleep(0.01) # Not sure about this.
            ready = [guard for guard in self.guards if guard.is_selectable()]
        _debug('Alt got %i items to choose from' % len(ready))
        self.last_selected = ready[0]
        for guard in ready[1:]:
            guard.disable()
        return ready[0].select()

    def __mul__(self, n):
        assert n > 0
        for i in xrange(n):
            yield self.select()
        return

    def __rmul__(self, n):
        assert n > 0
        for i in xrange(n):
            yield self.select()
        return


class Par(threading.Thread, CSPOpMixin):
    """Run CSP processes in parallel.
    """

    def __init__(self, *procs, **kwargs):
        super(Par, self).__init__(None)
        if 'timeout' in kwargs:
            self.timeout = kwargs['timeout']
        else:
            self.timeout = 0.1
        self.procs = []
        for proc in procs:
            # FIXME: only catches shallow nesting.
            if isinstance(proc, Par):
                self.procs += proc.procs
            else:
                self.procs.append(proc)
        for proc in self.procs:
            proc.enclosing = self
        _debug('# processes in Par:', len(self.procs))
        return

    def __str__(self):
        return 'CSP Par running in process %i.' % self.getPid()

    def terminate(self):
        """Terminate the execution of this process.
        """
        for proc in self.procs:
            proc.terminate()
        if self._Thread__started.is_set():
            Thread._Thread__stop(self)

    def getPid(self):
        """Return thread ident.

        The name of this method ensures that the CSPProcess interface
        in this module is identical to the one defined in
        cspprocess.py.
        """
        return self.ident

    def start(self):
        """Run this process. Analogue of L{CSPProcess.run}.
        """
        self.start()

    def join(self):
        for proc in self.procs:
            proc.join()

    def start(self):
        """Start then synchronize with the execution of parallel processes.
        Return when all parallel processes have returned.
        """
        try:
            for proc in self.procs:
                proc.spawn()
            for proc in self.procs:
                proc.join() #self.timeout)
        except ChannelPoison:
            _debug(str(self), 'in', self.getPid(), 'got ChannelPoison exception')
            self.referent_visitor(self.args + tuple(self.kwargs.values()))
        except ProcessSuspend:
            raise NotImplementedError('Process suspension not yet implemented')
        except Exception:
            typ, excn, tback = sys.exc_info()
            sys.excepthook(typ, excn, tback)


class Seq(threading.Thread, CSPOpMixin):
    """Run CSP processes sequentially.
    """

    def __init__(self, *procs):
        super(Seq, self).__init__()
        self.procs = []
        for proc in procs:
            # FIXME: only catches shallow nesting.
            if isinstance(proc, Seq):
                self.procs += proc.procs
            else:
                self.procs.append(proc)
        for proc in self.procs:
            proc.enclosing = self
        return

    def __str__(self):
        return 'CSP Seq running in process %i.' % self.getPid()

    def join(self):
        for proc in self.procs:
            proc.join()

    def terminate(self):
        """Terminate the execution of this process.
        """
        for proc in self.procs:
            proc.terminate()
        if self._Thread__started.is_set():
            Thread._Thread__stop(self)

    def start(self):
        """Start this process running.
        """
        try:
            for proc in self.procs:
                proc.start()
                proc.join()
        except ChannelPoison:
            _debug(str(self), 'in', self.getPid(), 'got ChannelPoison exception')
            self.referent_visitor(self.args + tuple(self.kwargs.values()))
        except ProcessSuspend:
            raise NotImplementedError('Process suspension not yet implemented')
        except Exception:
            typ, excn, tback = sys.exc_info()
            sys.excepthook(typ, excn, tback)


### Function decorators

def process(func):
    """Decorator to turn a function into a CSP process.

    Note that the function itself will not be a CSPProcess object, but
    will generate a CSPProcess object when called.
    """

    @wraps(func)
    def _call(*args, **kwargs):
        """Call the target function."""
        return CSPProcess(func, *args, **kwargs)
    return _call

### List of CSP based types (class names). Used by _is_csp_type.
_CSPTYPES = [CSPProcess, Par, Seq, Alt]


def _is_csp_type(name):
    """Return True if name is any type of CSP process."""
    for typ in _CSPTYPES:
        if isinstance(name, typ):
            return True
    return False

# Design patterns

class TokenRing(Par):
    def __init__(self, func, size, numtoks=1, _process=None):
        self.chans = [Channel() for channel in xrange(size)]
        self.procs = [func(index=i,
                           tokens=numtoks,
                           numnodes=size,
                           inchan=self.chans[i-1],
                           outchan=self.chans[i]) for i in xrange(size)]
        super(TokenRing, self).__init__(*self.procs) 
        return

# PlugNPlay guards and processes

class Skip(Guard):
    """Guard which will always return C{True}. Useful in L{Alt}s where
    the programmer wants to ensure that L{Alt.select} will always
    synchronise with at least one guard.
    """

    def __init__(self):
        Guard.__init__(self)

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


class TimerGuard(Guard):
    """Guard which only commits to synchronisation when a timer has expired.
    """

    def __init__(self):
        super(TimerGuard, self).__init__()
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

@process
def Zeroes(cout, _process=None):
    """Writes out a stream of zeroes."""
    while True:
        cout.write(0)
    return


@process
def Id(cin, cout, _process=None):
    """Id is the CSP equivalent of lambda x: x.
    """
    while True:
        cout.write(cin.read())
    return


@process
def Succ(cin, cout, _process=None):
    """Succ is the successor process, which writes out 1 + its input event.
    """
    while True:
        cout.write(cin.read() + 1)
    return


@process
def Pred(cin, cout, _process=None):
    """Pred is the predecessor process, which writes out 1 - its input event.
    """
    while True:
        cout.write(cin.read() - 1)
    return


@process
def Prefix(cin, cout, prefix_item=None, _process=None):
    """Prefix a write on L{cout} with the value read from L{cin}.

    @type prefix_item: object
    @param prefix_item: prefix value to use before first item read from L{cin}.
    """
    pre = prefix_item
    while True:
        cout.write(pre)
        pre = cin.read()
    return


@process
def Delta2(cin, cout1, cout2, _process=None):
    """Delta2 sends input values down two output channels.
    """
    while True:
        val = cin.read()
        cout1.write(val)
        cout2.write(val)
    return


@process
def Mux2(cin1, cin2, cout, _process=None):
    """Mux2 provides a fair multiplex between two input channels.
    """
    alt = Alt(cin1.read, cin2.read)
    while True:
        guard = alt.pri_select()
        cout.write(guard.read())
    return

@process
def Multiply(cin0,cin1,cout0,_process=None):
    
    while True:
        cout0.write(cin0.read() * cin1.read())
    return


@process
def Clock(cout, resolution=1, _process=None):
    """Send None object down output channel every C{resolution} seconds.
    """
    while True:
        time.sleep(resolution)
        cout.write(None)
    return


@process
def Printer(cin, _process=None, out=sys.stdout):
    """Print all values read from L{cin} to standard out or L{out}.
    """
    while True:
        msg = str(cin.read()) + '\n'
        out.write(msg)
    return


@process
def Pairs(cin1, cin2, cout, _process=None):
    """Read values from L{cin1} and L{cin2} and write their addition
    to L{cout}.
    """
    while True:
        in1 = cin1.read()
        in2 = cin2.read()
        cout.write(in1 + in2)
    return


@process
def Mult(cin, cout, scale, _process=None):
    """Scale values read on L{cin} and write to L{cout}.
    """
    while True:
        cout.write(cin.read() * scale)
    return


@process
def Generate(cout, _process=None):
    """Generate successive (+ve) ints and write to L{cout}.
    """
    counter = 0
    while True:
        cout.write(counter)
        counter += 1
    return


@process
def FixedDelay(cin, cout, delay, _process=None):
    """Read values from L{cin} and write to L{cout} after a delay of
    L{delay} seconds.
    """
    while True:
        in1 = cin.read()
        time.sleep(delay)
        cout.write(in1)
    return


@process
def Fibonacci(cout, _process=None):
    """Write successive Fibonacci numbers to L{cout}.
    """
    a_int = b_int = 1
    while True:
        cout.write(a_int)
        a_int, b_int = b_int, a_int + b_int
    return


@process
def Blackhole(cin, _process=None):
    """Read values from L{cin} and do nothing with them.
    """
    while True:
        cin.read()
    return


@process
def Sign(cin, cout, prefix, _process=None):
    """Read values from L{cin} and write to L{cout}, prefixed by L{prefix}.
    """
    while True:
        val = cin.read()
        cout.write(prefix + str(val))
    return


### Magic for processes built on Python operators

def _applyunop(unaryop, docstring):
    """Create a process whose output is C{unaryop(cin.read())}.
    """

    @process
    def _myproc(cin, cout, _process=None):
        while True:
            in1 = cin.read()
            cout.write(unaryop(in1))
        return
    _myproc.__doc__ = docstring
    return _myproc


def _applybinop(binop, docstring):
    """Create a process whose output is C{binop(cin1.read(), cin2.read())}.
    """

    @process
    def _myproc(cin1, cin2, cout, _process=None):
        while True:
            in1 = cin1.read()
            in2 = cin2.read()
            cout.write(binop(in1, in2))
        return
    _myproc.__doc__ = docstring
    return _myproc

# Numeric operators

Plus = _applybinop(operator.__add__,
                   """Writes out the addition of two input events.
""")

Sub = _applybinop(operator.__sub__,
                  """Writes out the subtraction of two input events.
""")

Mul = _applybinop(operator.__mul__,
                  """Writes out the multiplication of two input events.
""")

Div = _applybinop(operator.__div__,
                  """Writes out the division of two input events.
""")


FloorDiv = _applybinop(operator.__floordiv__,
                       """Writes out the floor div of two input events.
""")

Mod = _applybinop(operator.__mod__,
                  """Writes out the modulo of two input events.
""")

Pow = _applybinop(operator.__pow__,
                  """Writes out the power of two input events.
""")

LShift = _applybinop(operator.__lshift__,
                     """Writes out the left shift of two input events.
""")

RShift = _applybinop(operator.__rshift__,
                     """Writes out the right shift of two input events.
""")

Neg = _applyunop(operator.__neg__,
                 """Writes out the negation of input events.
""")

# Bitwise operators

Not = _applyunop(operator.__inv__,
                 """Writes out the inverse of input events.
""")

And = _applybinop(operator.__and__,
                  """Writes out the bitwise and of two input events.
""")

Or = _applybinop(operator.__or__,
                 """Writes out the bitwise or of two input events.
""")

Nand = _applybinop(lambda x, y: ~ (x & y),
                   """Writes out the bitwise nand of two input events.
""")

Nor = _applybinop(lambda x, y: ~ (x | y),
                  """Writes out the bitwise nor of two input events.
""")

Xor = _applybinop(operator.xor,
                  """Writes out the bitwise xor of two input events.
""")

# Logical operators

Land = _applybinop(lambda x, y: x and y,
                   """Writes out the logical and of two input events.
""")

Lor = _applybinop(lambda x, y: x or y,
                  """Writes out the logical or of two input events.
""")

Lnot = _applyunop(operator.__not__,
                  """Writes out the logical not of input events.
""")

Lnand = _applybinop(lambda x, y: not (x and y),
                    """Writes out the logical nand of two input events.
""")

Lnor = _applybinop(lambda x, y: not (x or y),
                   """Writes out the logical nor of two input events.
""")

Lxor = _applybinop(lambda x, y: (x or y) and (not x and y),
                   """Writes out the logical xor of two input events.
""")

# Comparison operators

Eq = _applybinop(operator.__eq__,
                 """Writes True if two input events are equal (==).
""")

Ne = _applybinop(operator.__ne__,
                   """Writes True if two input events are not equal (not ==).
""")

Geq = _applybinop(operator.__ge__,
                   """Writes True if 'right' input event is >= 'left'.
""")

Leq = _applybinop(operator.__le__,
                   """Writes True if 'right' input event is <= 'left'.
""")

Gt = _applybinop(operator.__gt__,
                   """Writes True if 'right' input event is > 'left'.
""")

Lt = _applybinop(operator.__lt__,
                   """Writes True if 'right' input event is < 'left'.
""")

Is = _applybinop(lambda x, y: x is y,
                 """Writes True if two input events are the same (is).
""")

Is_Not = _applybinop(lambda x, y: not (x is y),
                   """Writes True if two input events are not the same (is).
""")
