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
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
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
    smap = map(str, args)
    if DEBUG:
        print 'DEBUG:', ' '.join(smap)

from functools import wraps # Easy decorators
import operator
import os
import random
import socket
import sys
import tempfile
import time

# Are we sending secure messages?
try:
    import hmac
    import hashlib
    SECURITY_ON = True
except ImportError:
    SECURITY_ON = False
# Override the above, for testing:
SECURITY_ON = False

try: # Python optimisation compiler
    import psyco
    psyco.full()
except ImportError:
    print 'No available optimisation'

import threading

#try:
#    import cPickle as pickle # Faster pickle
#except ImportError:
import pickle

### CONSTANTS

_BUFFSIZE = 1024

_HOST = socket.gethostbyname(socket.gethostname())
_CHANNEL_PORT = 9890
_OTA_PORT = 8888
_VIS_PORT = 8889

### Seeded random number generator (16 bytes)

_rangen = random.Random(os.urandom(16))

### Authentication

def _makeDigest(message):
    """Return a digest for a given message."""
    return hmac.new('these/are/the/droids', message, hashlib.sha1).hexdigest()


class CorruptedData(Exception):
    """Used to verify that data has come from an honest source.
    """

    def __init__(self):
        super(CorruptedData, self).__init__()
        return

    def __str__(self):
        return 'Data sent with incorrect authentication key.'


class NoGuardInALT(Exception):
    """Raised when an ALT has no guards to select.
    """

    def __init__(self):
        super(NoGuardInALT, self).__init__()
        return

    def __str__(self):
        return 'Every ALT must have at least one guard.'


### Special constants / exceptions for termination and mobility
### Better not to use classes/objects here or pickle will get confused
### by the way that csp.__init__ manages the namespace.

_POISON = ';;;__POISON__;;;'
"""Used as special data sent down a channel to invoke termination."""

_SUSPEND = ';;;__SUSPEND__;;;' 	### NOT IMPLEMENTED
"""Used as special data sent down a channel to invoke suspension."""

_RESUME = ';;;__RESUME__;;;'	### NOT IMPLEMENTED
"""Used as special data sent down a channel to resume operation."""


class ChannelPoison(Exception):
    """Used to poison a processes and propagate to all known channels.
    """

    def __init__(self):
        super(ChannelPoison, self).__init__()
        return

    def __str__(self):
        return 'Posioned channel exception.'


class ChannelAbort(Exception):
    """Used to stop a channel write if a select aborts...
    """

    def __init__(self):
        super(ChannelAbort, self).__init__()
        return

    def __str__(self):
        return 'Channel abort exception.'


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

    def _start(self):
        """Start only if self is not running."""
        if not self._Thread__started.is_set():
            self.start()

    def _join(self, timeout=None):
        """Join only if self is running and impose a timeout."""
        if self._Thread__started.is_set():
            self.join(timeout)

    def _terminate(self):
        """Terminate only if self is running.

        FIXME: This doesn't work yet...
        """
        if self._Thread__started.is_set():
            _debug(str(self.getName()), 'terminating now...')
            self._Thread__stop()

    def __and__(self, other):
        """Implementation of CSP PAR.

        Requires timeout with a small value to ensure
        parallelism. Otherwise a long sequence of '&' operators will
        run in sequence (because of left-to-right evaluation and
        orders of precedence.
        """
        assert _isCSPType(other)
        p = PAR(other, self, timeout=0.1)
        p.start()
        return p

    def __gt__(self, other):
        """Implementation of CSP SEQ."""
        assert _isCSPType(other)
        s = SEQ(self, other)
        s.start()
        return s


class CSPProcess(threading.Thread, CSPOpMixin):
    """Implementation of CSP processes.
    Not intended to be used in client code. Use @process instead.
    """

    def __init__(self, func, *args, **kwargs):
        threading.Thread.__init__(self,
                                  target=func,
                                  args=(args),
                                  kwargs=kwargs)
        assert callable(func)
        for arg in list(self._Thread__args) + self._Thread__kwargs.values():
            if _isCSPType(arg):
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

    def run(self, event=None):
        try:
            self._Thread__target(*self._Thread__args, **self._Thread__kwargs)
        except ChannelPoison:
            if self.enclosing:
                self.enclosing._terminate()
            self._terminate()
            del self
        except ProcessSuspend:
            raise NotImplementedError('Process suspension not yet implemented')
        except Exception:
            t, exc, tb = sys.exc_info()
            sys.excepthook(t, exc, tb)
        return


class Guard(object):

    def isSelectable(self):
        raise NotImplementedError('Must be implemented in subclass')

    def enable(self):
        raise NotImplementedError('Must be implemented in subclass')

    def disable(self):
        raise NotImplementedError('Must be implemented in subclass')

    def select(self):
        raise NotImplementedError('Must be implemented in subclass')

    def poison(self):
        pass

    def __str__(self):
        return 'CSP Guard: must be subclassed.'


class TimedGuard(Guard):

    def __init__(self, timer):
        super(TimedGuard, self).__init__()
        self.tau = timer
        return

    def isSelectable(self):
        return True

    def enable(self):
        return

    def disable(self):
        return

    def select(self):
        time.sleep(self.tau)
        return


class ConditionGuard(Guard):
    """ ??? """

    def __init__(self, expr):
        assert callable(expr)
        self.expr = expr
        super(ConditionGuard, self).__init__()
        return

    def isSelectable(self):
        return bool(self.expr())

    def enable(self):
        return

    def disable(self):
        return

    def select(self):
        return


class _PortFactory(object):
    """Singleton factory class, generating unique (per-host) port numbers.
    """
    __instance = None

    def __new__(cls, *args, **kargs):
        """Create a new instance of this class, ensuring conformance
        to the singleton pattern.

        See U{http://en.wikipedia.org/wiki/Singleton_pattern#Python}
        """
        if cls.__instance is None:
            cls.__instance = object.__new__(cls, *args, **kargs)
        return cls.__instance

    def __init__(self):
        self.portnum = 27899
        return

    def port(self):
        """Return a new port number which is unique on this host.
        """
        port = self.portnum
        self.portnum += 1
        return port


class _NameFactory(object):
    """Singleton factory class, generating unique (per-network) channel names.
    """
    __instance = None

    def __new__(cls, *args, **kargs):
        """Create a new instance of this class, ensuring conformance
        to the singleton pattern.

        See U{http://en.wikipedia.org/wiki/Singleton_pattern#Python}
        """
        if cls.__instance is None:
            cls.__instance = object.__new__(cls, *args, **kargs)
        return cls.__instance

    def __init__(self):
        self.i = ~sys.maxint
        return

    def name(self):
        """Return a new channel name which is unique within this network.
        """
        name = _HOST + ':' + str(os.getpid()) + ':'+ str(self.i)
        self.i += 1
        return name


class Channel(Guard):
    """CSP Channel objects.

    In python-csp there are two sorts of channel. In JCSP terms these
    are Any2Any, ALTing channels. However, each channel creates an
    operating system level pipe. Since this is a file object the
    number of channels a program can create is limited to the maximum
    number of files the operating system allows to be open at any one
    time. To avoid this bottleneck use L{FileChannel} objects, which
    close the file descriptor used for IPC after every read or write
    operations. Read and write operations are, however, over 20 time
    slower when performed on L{FileChannel} objects.

    Subclasses of C{Channel} must call L{_setup()} in their
    constructor and override L{put}, L{get}, L{__del__},
    L{__getstate__} and L{__setstate__}, the latter two methods for
    pickling.
    """
    NAMEFACTORY = _NameFactory()

    def __init__(self):
        self.name = Channel.NAMEFACTORY.name()
        self._wlock = None	# Write lock.
        self._rlock = None	# Read lock.
        self._available = None
        self._taken = None
        self._isAlting = None
        self._isSelectable = None
        self._hasSelected = None
        self._store = None # Holds value transferred by channel
        self._setup()
        super(Channel, self).__init__()
        return

    def _setup(self):
        """Set up synchronisation.

        MUST be called in __init__ of this class and all subclasses.
        """
        # Process-safe synchronisation.
        self._wlock = threading.RLock()	# Write lock.
        self._rlock = threading.RLock()	# Read lock.
        self._available = threading.Semaphore(0)
        self._taken = threading.Semaphore(0)
        # Process-safe synchronisation for CSP Select / Occam ALT.
        self._isAlting = False
        self._isSelectable = False
        # Kludge to say a select has finished (to prevent the channel
        # from being re-enabled). If values were really process safe
        # we could just have writers set _isSelectable and read that.
        self._hasSelected = False

    def __getstate__(self):
        """Return state required for pickling."""
        state = [self._available.getValue(),
                 self._taken.getValue(),
                 self._isAlting,
                 self._isSelectable,
                 self._hasSelected]
        if self._available.getValue() > 0:
            obj = self.get()
        else:
            obj = None
        state.append(obj)
        return state

    def __setstate__(self, state):
        """Restore object state after unpickling."""
        self._wlock = threading.RLock()	# Write lock.
        self._rlock = threading.RLock()	# Read lock.
        self._available = threading.Semaphore(state[0])
        self._taken = threading.Semaphore(state[1])
        self._isAlting = state[2]
        self._isSelectable = state[3]
        self._hasSelected = state[4]
        if state[5] is not None:
            self.put(state[5])
        return

    def put(self, item):
        """Put C{item} on a process-safe store.
        """
        self._store = pickle.dumps(item)

    def get(self):
        """Get a Python object from a process-safe store.
        """
        item = pickle.loads(self._store)
        self._store = None
        return item

    def __del__(self):
        return

    def isSelectable(self):
        """Test whether ALT can select this channel.
        """
        _debug('ALT THINKS _isSelectable IS: ' +
               str(self._isSelectable))
        return self._isSelectable

    def write(self, obj):
        """Write a Python object to this channel.
        """
        _debug('+++ Write on Channel %s started.' % self.name)
        with self._wlock: # Protect from races between multiple writers.
            # If this channel has already been selected by an ALT then
            # _hasSelected will be True, blocking other readers. If a
            # new write is performed that flag needs to be reset for
            # the new write transaction.
            self._hasSelected = False
            # Make the object available to the reader.
            self.put(obj)
            self._available.release()
            _debug('++++ Writer on Channel %s: _available: %i _taken: %i. ' %
                   (self.name, self._available._Semaphore__value,
                    self._taken._Semaphore__value))
            # Block until the object has been read.
            self._taken.acquire()
            # Remove the object from the channel.
        _debug('+++ Write on Channel %s finished.' % self.name)
        return

    def read(self):
        """Read (and return) a Python object from this channel.
        """
#        assert self._isAlting.value == Channel.FALSE
#        assert self._isSelectable.value == Channel.FALSE
        _debug('+++ Read on Channel %s started.' % self.name)
        with self._rlock: # Protect from races between multiple readers.
            # Block until an item is in the Channel.
            _debug('++++ Reader on Channel %s: _available: %i _taken: %i. ' %
                   (self.name, self._available._Semaphore__value,
                    self._taken._Semaphore__value))
            self._available.acquire()
            # Get the item.
            _debug('++++ Reader on Channel %s: _available: %i _taken: %i. ' %
                   (self.name, self._available._Semaphore__value,
                    self._taken._Semaphore__value))
            obj = self.get()
            # Announce the item has been read.
            self._taken.release()
        _debug('+++ Read on Channel %s finished.' % self.name)
        if obj == _POISON:
            raise ChannelPoison()
        return obj

    def enable(self):
        """Enable a read for an ALT select.

        MUST be called before L{select()} or L{isSelectable()}.
        """
        # Prevent re-synchronization.
        if (self._hasSelected or self._isSelectable):
            return
        self._isAlting = True
        with self._rlock:
            # Attempt to acquire _available.
            time.sleep(0.00001) # Won't work without this -- why?
            retval = self._available.acquire(blocking=False)
        if retval:
            self._isSelectable = True
        else:
            self._isSelectable = False
        return

    def disable(self):
        """Disable this channel for ALT selection.

        MUST be called after L{enable} if this channel is not selected.
        """
        self._isAlting = False
        if self._isSelectable:
            with self._rlock:
                self._available.release()
            self._isSelectable = False
        return

    def select(self):
        """Complete a Channel read for an ALT select.
        """
        _debug('channel select starting')
        assert self._isSelectable == True
        with self._rlock:
            _debug('got read lock')
            # Obtain object on Channel.
            obj = self.get()
            _debug('got obj')
            # Notify write() that object is taken.
            self._taken.release()
            _debug('released _taken')
            # Reset flags to ensure a future read / enable / select.
            self._isSelectable = False
            self._isAlting = False
            self._hasSelected = True
            _debug('reset bools')
        if obj == _POISON:
            raise ChannelPoison()
        return obj

    def __str__(self):
        return 'Channel using OS pipe for IPC.'

    def poison(self):
        """Poison a channel causing all processes using it to terminate.
        """
        raise ChannelPoison()

    def suspend(self):
        raise NotImplementedError('Suspend / resume not implemented')

    def resume(self):
        raise NotImplementedError('Suspend / resume not implemented')


class FileChannel(Channel):
    """Channel objects using files on disk.

    C{FileChannel} objects close their files after each read or write
    operation. The advantage of this is that client code can create as
    many C{FileChannel} objects as it wishes (unconstrained by the
    operating system's maximum number of open files). In return there
    is a performance hit -- reads and writes are around 10 x slower on
    C{FileChannel} objects compared to L{Channel} objects.
    """

    def __init__(self):
        self._wlock = None	# Write lock.
        self._rlock = None	# Read lock.
        self._available = None
        self._taken = None
        self._isAlting = None
        self._isSelectable = None
        self._hasSelected = None
        # Process-safe store.
        fd, self._fname = tempfile.mkstemp()
        os.close(fd)
        self._setup()
        return

    def __getstate__(self):
        """Return state required for pickling."""
        state = [pickle.dumps(self._available),
                 pickle.dumps(self._taken),
                 pickle.dumps(self._isAlting),
                 pickle.dumps(self._isSelectable),
                 pickle.dumps(self._hasSelected),
                 self._fname]
        if self._available.getValue() > 0:
            obj = self.get()
        else:
            obj = None
        state.append(obj)
        return state

    def __setstate__(self, state):
        """Restore object state after unpickling."""
        self._wlock = threading.RLock()	# Write lock.
        self._rlock = threading.RLock()	# Read lock.
        self._available = pickle.loads(state[0])
        self._taken = pickle.loads(state[1])
        self._isAlting = pickle.loads(state[2])
        self._isSelectable = pickle.loads(state[3])
        self._hasSelected = pickle.loads(state[4])
        self._fname = state[5]
        if state[6] is not None:
            self.put(state[6])
        return

    def put(self, item):
        f = file(self._fname, 'w')
        f.write(pickle.dumps(item))
        f.flush()
        f.close()
        return

    def get(self):
        s = ''
        while s=='':
            f = file(self._fname, 'r')
            s = f.read()
            f.close()
        # Unlinking here ensures that FileChannel objects exhibit the
        # same semantics as Channel objects.
        os.unlink(self._fname)
        obj = pickle.loads(s)
        return obj

    def __del__(self):
        if os.path.exists(self._fname):
            # Necessary if the Channel has been deleted by poisoning.
            os.unlink(self._fname)
        return

    def __str__(self):
        return 'Channel using files for IPC.'

    def suspend(self):
        raise NotImplementedError('Suspend / resume not implemented')

    def resume(self):
        raise NotImplementedError('Suspend / resume not implemented')


### CSP combinators -- PAR, ALT, SEQ, ...

class ALT(CSPOpMixin):
    """CSP select (OCCAM ALT) process.

    What should happen if a guard is poisoned?
    """

    def __init__(self, *args):
        super(ALT, self).__init__()
        for arg in args:
            assert isinstance(arg, Guard)
        self.guards = list(args)
        self.lastSelected = None

    def poison(self):
        """Poison the last selected guard and unlink from the guard list.

        Sets self.lastSelected to None.
        """
        _debug(type(self.lastSelected))
        self.lastSelected.disable() # Just in case
        try:
            self.lastSelected.poison()
        except:
            pass
        _debug('Poisoned last selected.')
        self.guards.remove(self.lastSelected)
        _debug('%i guards' % len(self.guards))
        self.lastSelected = None

    def _preselect(self):
        """Check for special cases when any form of select() is called.
        """
        if len(self.guards) == 0:
            raise NoGuardInALT()
        elif len(self.guards) == 1:
            _debug('ALT Selecting unique guard:', self.guards[0].name)
            self.lastSelected = self.guards[0]
            return self.guards[0].read()
        return None

    def select(self):
        """Randomly select from ready guards."""
        selected = self._preselect()
        if selected is not None:
            return selected
        for g in self.guards:
            g.enable()
        _debug('Alt enabled all guards')
        ready = [g for g in self.guards if g.isSelectable()]
        while len(ready) == 0:
            time.sleep(0.01) # Not sure about this.
            ready = [g for g in self.guards if g.isSelectable()]
            _debug('Alt got no items to choose from')
        _debug('Alt got %i items to choose from' % len(ready))
        selected = _rangen.choice(ready)
        self.lastSelected = selected
        for g in self.guards:
            if g is not selected:
                g.disable()
        return selected.select()

    def fairSelect(self):
        if self.lastSelected is None:
            return self.select()
        selected = self._preselect()
        if selected is not None:
            return selected
        for g in self.guards:
            g.enable()
        _debug('Alt enabled all guards')
        ready = [g for g in self.guards if g.isSelectable()]
        while len(ready) == 0:
            time.sleep(0.1) # Not sure about this.
            ready = [g for g in self.guards if g.isSelectable()]
        _debug('Alt got %i items to choose from' % len(ready))
        selected = None
        if self.lastSelected in ready and len(ready) > 1:
            ready.remove(self.lastSelected)
            _debug('Alt removed last selected from ready list')
        selected = _rangen.choice(ready)
        self.lastSelected = selected
        for g in self.guards:
            if g is not selected:
                g.disable()
        return selected.select()

    def priSelect(self):
        selected = self._preselect()
        if selected is not None:
            return selected
        for g in self.guards:
            g.enable()
        _debug('Alt enabled all guards')
        ready = [g for g in self.guards if g.isSelectable()]
        while len(ready) == 0:
            time.sleep(0.01) # Not sure about this.
            ready = [g for g in self.guards if g.isSelectable()]
        _debug('Alt got %i items to choose from' % len(ready))
        selected = ready[0]
        self.lastSelected = selected
        for g in self.guards:
            if g is not selected:
                g.disable()
        return selected.select()


class PAR(threading.Thread, CSPOpMixin):
    """Run CSP processes in parallel.
    """

    def __init__(self, *procs, **kwargs):
        super(PAR, self).__init__(None)
        if 'timeout' in kwargs:
            self.timeout = kwargs['timeout']
        else:
            self.timeout=0.5
        self.procs = []
        for proc in procs:
            # FIXME: only catches shallow nesting.
            if isinstance(proc, PAR):
                self.procs += proc.procs
            else:
                self.procs.append(proc)
        for proc in self.procs:
            proc.enclosing = self
        _debug('# processes in PAR:', len(self.procs))
        return

    def __str__(self):
        return 'CSP PAR running in process %i.' % self.getPid()

    def run(self):
        self.start()

    def _terminate(self):
        for proc in self.procs:
            proc._terminate()
        if self._Thread__started.is_set():
            self._Thread__stop()

    def start(self):
        """Start then synchronize with the execution of parallel processes.
        Return when all parallel processes have returned.
        """
        try:
            for proc in self.procs:
                proc._start()
            for proc in self.procs:
                proc._join(self.timeout)
        except ChannelPoison:
            self._terminate()
        except ProcessSuspend:
            raise NotImplementedError('Process suspension not yet implemented')
        except Exception:
            t, exc, tb = sys.exc_info()
            sys.excepthook(t, exc, tb)
        return


class SEQ(threading.Thread, CSPOpMixin):
    """Run CSP processes sequentially.
    """

    def __init__(self, *procs):
        super(SEQ, self).__init__()
        self.procs = []
        for proc in procs:
            # FIXME: only catches shallow nesting.
            if isinstance(proc, SEQ):
                self.procs += proc.procs
            else:
                self.procs.append(proc)
        for proc in self.procs:
            proc.enclosing = self
        return

    def __str__(self):
        return 'CSP SEQ running in process %i.' % self.getPid()

    def stop(self):
        for proc in self.procs:
            proc._terminate()
        if self._Thread__started.is_set():
            self._Thread__stop()

    def start(self):
        try:
            for proc in self.procs:
                proc._start()
                proc._join()
        except ChannelPoison:
            self._terminate()
        except ProcessSuspend:
            raise NotImplementedError('Process suspension not yet implemented')
        except Exception:
            t, exc, tb = sys.exc_info()
            sys.excepthook(t, exc, tb)
        return

### Function decorators

def process(func):
    """Decorator to turn a function into a CSP process.

    Note that the function itself will not be a CSPProcess object, but
    will generate a CSPProcess object when called.
    """

    @wraps(func)
    def _call(*args, **kwargs):
        return CSPProcess(func, *args, **kwargs)
    return _call

### List of CSP based types (class names). Used by _isCSPType.
_csptypes = [CSPProcess, PAR, SEQ, ALT]


def _isCSPType(name):
    """Return True if name is any type of CSP process."""
    for ty in _csptypes:
        if isinstance(name, ty):
            return True
    return False

# Common idioms for processes, guards, etc.
# Mainly taken from JCSP plugNplay package.

class SKIP(Guard):

    def __init__(self):
        Guard.__init__(self)

    def isSelectable(self):
        return True

    def enable(self):
        return

    def disable(self):
        return

    def select(self):
        return 'SKIP'

    def __str__(self):
        return 'SKIP guard is always selectable.'


class TimerGuard(Guard):

    def __init__(self):
        raise NotImplementedError('Timer guards not yet implemented.')


@process
def ZEROES(cout, _process=None):
    """Writes out a stream of zeroes."""
    while True:
        cout.write(0)
    return


@process
def ID(cin, cout, _process=None):
    """ID is the CSP equivalent of lambda x: x.
    """
    while True:
        cout.write(cin.read())
    return


@process
def SUCC(cin, cout, _process=None):
    """SUCC is the successor process, which writes out 1 + its input event.
    """
    while True:
        cout.write(cin.read() + 1)
    return


@process
def PRED(cin, cout, _process=None):
    """PRED is the predecessor process, which writes out 1 - its input event.
    """
    while True:
        cout.write(cin.read() - 1)
    return


@process
def PREFIX(cin, cout, prefixItem=None, _process=None):
    """
    """
    t = prefixItem
    while True:
        cout.write(t)
        t = cin.read()
    return


@process
def DELTA2(cin, cout1, cout2, _process=None):
    """DELTA2 sends input values down two output channels.
    """
    while True:
        t = cin.read()
        cout1.write(t)
        cout2.write(t)
    return


@process
def MUX2(cin1, cin2, cout, _process=None):
    """MUX2 provides a fair multiplex between two input channels.
    """
    alt = ALT(cin1.read, cin2.read)
    while True:
        c = alt.priSelect()
        cout.write(c.read())
    return


@process
def CLOCK(cout, resolution=1, _process=None):
    """Send None object down output channel every C{resolution} seconds.
    """
    while True:
        time.sleep(resolution)
        cout.write(None)
    return


@process
def PRINTER(cin, _process=None, out=sys.stdout):
    while True:
        msg = str(cin.read()) + '\n'
        out.write(msg)
    return


@process
def PAIRS(cin1, cin2, cout, _process=None):
    while True:
        in1 = cin1.read()
        in2 = cin2.read()
        cout.write(in1 + in2)
    return


@process
def MULT(cin, cout, scale, _process=None):
    while True:
        cout.write(cin.read() * scale)
    return


@process
def GENERATE(cout, _process=None):
    i = 0
    while True:
        cout.write(i)
        i += 1
    return


@process
def FIXEDDELAY(cin, cout, delay, _process=None):
    while True:
        in1 = cin.read()
        time.sleep(delay)
        cout.write(in1)
    return


@process
def FIBONACCI(cout, _process=None):
    a = b = 1
    while True:
        cout.write(a)
        a, b = b, a+b
    return


@process
def BLACKHOLE(cin, _process=None):
    while True:
        cin.read()
    return


@process
def SIGN(cin, cout, prefix, _process=None):
    while True:
        d = cin.read()
        cout.write(prefix + str(d))
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

PLUS = _applybinop(operator.__add__,
                   """Writes out the addition of two input events.
""")

SUB = _applybinop(operator.__sub__,
                  """Writes out the subtraction of two input events.
""")

MUL = _applybinop(operator.__mul__,
                  """Writes out the multiplication of two input events.
""")

DIV = _applybinop(operator.__div__,
                  """Writes out the division of two input events.
""")

FLOORDIV = _applybinop(operator.__floordiv__,
                       """Writes out the floor div of two input events.
""")

MOD = _applybinop(operator.__mod__,
                  """Writes out the modulo of two input events.
""")

POW = _applybinop(operator.__pow__,
                  """Writes out the power of two input events.
""")

LSHIFT = _applybinop(operator.__lshift__,
                     """Writes out the left shift of two input events.
""")

RSHIFT = _applybinop(operator.__rshift__,
                     """Writes out the right shift of two input events.
""")

NEG = _applyunop(operator.__neg__,
                 """Writes out the negation of input events.
""")

# Bitwise operators

NOT = _applyunop(operator.__inv__,
                 """Writes out the inverse of input events.
""")

AND = _applybinop(operator.__and__,
                  """Writes out the bitwise and of two input events.
""")

OR = _applybinop(operator.__or__,
                 """Writes out the bitwise or of two input events.
""")

NAND = _applybinop(lambda x, y: ~ (x & y),
                   """Writes out the bitwise nand of two input events.
""")

NOR = _applybinop(lambda x, y: ~ (x | y),
                  """Writes out the bitwise nor of two input events.
""")

XOR = _applybinop(operator.xor,
                  """Writes out the bitwise xor of two input events.
""")

# Logical operators

LAND = _applybinop(lambda x, y: x and y,
                   """Writes out the logical and of two input events.
""")

LOR = _applybinop(lambda x, y: x or y,
                  """Writes out the logical or of two input events.
""")

LNOT = _applyunop(operator.__not__,
                  """Writes out the logical not of input events.
""")

LNAND = _applybinop(lambda x, y: not (x and y),
                    """Writes out the logical nand of two input events.
""")

LNOR = _applybinop(lambda x, y: not (x or y),
                   """Writes out the logical nor of two input events.
""")

LXOR = _applybinop(lambda x, y: (x or y) and (not x and y),
                   """Writes out the logical xor of two input events.
""")

# Comparison operators

EQ = _applybinop(operator.__eq__,
                 """Writes True if two input events are equal (==).
""")

NE = _applybinop(operator.__ne__,
                   """Writes True if two input events are not equal (not ==).
""")

GEQ = _applybinop(operator.__ge__,
                   """Writes True if 'right' input event is >= 'left'.
""")

LEQ = _applybinop(operator.__le__,
                   """Writes True if 'right' input event is <= 'left'.
""")

GT = _applybinop(operator.__gt__,
                   """Writes True if 'right' input event is > 'left'.
""")

LT = _applybinop(operator.__lt__,
                   """Writes True if 'right' input event is < 'left'.
""")

IS = _applybinop(lambda x, y: x is y,
                 """Writes True if two input events are the same (is).
""")

IS_NOT = _applybinop(lambda x, y: not (x is y),
                   """Writes True if two input events are not the same (is).
""")
