#!/usr/bin/env python

"""Communicating sequential processes, in Python.

When using CSP Python as a DSL, this module will normally be imported
via the statement 'from csp.cspthread import *'. 

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
#DEBUG = False

from functools import wraps # Easy decorators

# Import barrier from bulk synchronous processing library
from bsp.bsp import BarrierThreading as Barrier

import copy
import gc
import inspect
import logging
import os
import random
import socket
import sys
import tempfile
import threading
import time
import uuid


try: # Python optimisation compiler
    import psyco
    psyco.full()
except ImportError:
    print 'No available optimisation'


# Are we sending secure messages?
try:
    import hmac
    import hashlib
    SECURITY_ON = True
except ImportError:
    SECURITY_ON = False
# Override the above, for testing:
SECURITY_ON = False

try:
    import cPickle as mypickle # Faster pickle
except ImportError:
    import pickle as mypickle


# Configure logging.
logging.basicConfig(level=logging.CRITICAL)
#logging.basicConfig(level=logging.NOTSET)


### Seeded random number generator (16 bytes)

_RANGEN = random.Random(os.urandom(16))


### CONSTANTS

_BUFFSIZE = 1024

_HOST = socket.gethostbyname(socket.gethostname())
_CHANNEL_PORT = 9890
_OTA_PORT = 8888
_VIS_PORT = 8889

### Authentication

def _make_digest(message):
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
            logging.debug(str(self.getName()), 'terminating now...')
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
        par.start()
        return par

    def __gt__(self, other):
        """Implementation of CSP Seq."""
        assert _is_csp_type(other)
        seq = Seq(self, other)
        seq.start()
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
            logging.debug(str(self), 'in', self.getPid(), 'got ChannelPoison exception')
            self.referent_visitor(self._Thread__args +
                                  tuple(self._Thread__kwargs.values()))
        except ProcessSuspend:
            raise NotImplementedError('Process suspension not yet implemented')
        except KeyboardInterrupt:
            sys.exit()
        except Exception:
            typ, excn, tback = sys.exc_info()
            sys.excepthook(typ, excn, tback)

    def __del__(self):
        """Run the garbage collector automatically on deletion of this
        object.

        This prevents the "Winder Bug" found in tests/winder_bug of
        the distribution, where successive process graphs are created
        in memory and, when the "outer" CSPProcess object returns from
        its .start() method the process graph is not garbage
        collected. This accretion of garbage can cause degenerate
        behaviour which is difficult to debug, such as a program
        pausing indefinitely on Channel creation.
        """
        gc.collect()
        return


class CSPServer(CSPProcess):
    """Implementation of CSP server processes.
    Not intended to be used in client code. Use @forever instead.
    """

    def __init__(self, func, *args, **kwargs):
        CSPProcess.__init__(self, func, *args, **kwargs)
        return

    def __str__(self):
        return 'CSPServer running in PID %s' % self.getPid()

    def run(self): #, event=None):
        """Called automatically when the L{start} methods is called.
        """
        try:
            func = self._target(*self._args, **self._kwargs)
            while sys.gettrace() is None:
                func.next()
        except ChannelPoison:
            logging.debug(str(self), 'in', self.getPid(), 'got ChannelPoison exception')
            self.referent_visitor(self._args + tuple(self._kwargs.values()))
#            if self._popen is not None: self.terminate()
        except ProcessSuspend:
            raise NotImplementedError('Process suspension not yet implemented')
        except KeyboardInterrupt:
            sys.exit()
        except Exception:
            typ, excn, tback = sys.exc_info()
            sys.excepthook(typ, excn, tback)
        return

    
### CSP combinators -- Par, Alt, Seq, ...

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
        logging.debug('# processes in Par:', len(self.procs))
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
            logging.debug(str(self), 'in', self.getPid(), 'got ChannelPoison exception')
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
                CSPOpMixin.start(proc)
                proc.join()
        except ChannelPoison:
            logging.debug(str(self), 'in', self.getPid(), 'got ChannelPoison exception')
            self.referent_visitor(self.args + tuple(self.kwargs.values()))
        except ProcessSuspend:
            raise NotImplementedError('Process suspension not yet implemented')
        except Exception:
            typ, excn, tback = sys.exc_info()
            sys.excepthook(typ, excn, tback)


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
        logging.debug(type(self.last_selected))
        self.last_selected.disable() # Just in case
        try:
            self.last_selected.poison()
        except:
            pass
        logging.debug('Poisoned last selected.')
        self.guards.remove(self.last_selected)
        logging.debug('%i guards' % len(self.guards))
        self.last_selected = None

    def _preselect(self):
        """Check for special cases when any form of select() is called.
        """
        if len(self.guards) == 0:
            raise NoGuardInAlt()
        elif len(self.guards) == 1:
            logging.debug('Alt Selecting unique guard:', self.guards[0].name)
            self.last_selected = self.guards[0]
            while not self.guards[0].is_selectable():
                self.guards[0].enable()
            return self.guards[0].select()
        return None

    def select(self):
        """Randomly select from ready guards."""
        if len(self.guards) < 2:
            return self._preselect()
        for guard in self.guards:
            guard.enable()
        logging.debug('Alt enabled all guards')
        ready = [guard for guard in self.guards if guard.is_selectable()]
        while len(ready) == 0:
            time.sleep(0.01) # Not sure about this.
            ready = [guard for guard in self.guards if guard.is_selectable()]
            logging.debug('Alt got no items to choose from')
        logging.debug('Alt got %i items to choose from' % len(ready))
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
        logging.debug('Alt enabled all guards')
        ready = [guard for guard in self.guards if guard.is_selectable()]
        while len(ready) == 0:
            time.sleep(0.1) # Not sure about this.
            ready = [guard for guard in self.guards if guard.is_selectable()]
        logging.debug('Alt got %i items to choose from' % len(ready))
        selected = None
        if self.last_selected in ready and len(ready) > 1:
            ready.remove(self.last_selected)
            logging.debug('Alt removed last selected from ready list')
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
        logging.debug('Alt enabled all guards')
        ready = [guard for guard in self.guards if guard.is_selectable()]
        while len(ready) == 0:
            time.sleep(0.01) # Not sure about this.
            ready = [guard for guard in self.guards if guard.is_selectable()]
        logging.debug('Alt got %i items to choose from' % len(ready))
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


### Guards and channels

class Guard(object):
    """Abstract class to represent CSP guards.

    All methods must be overridden in subclasses.
    """

    def is_selectable(self):
        """Should return C{True} if this guard can be selected by an L{Alt}.
        """
        raise NotImplementedError('Must be implemented in subclass')

    def enable(self):
        """Prepare for, but do not commit to a synchronisation.
        """
        raise NotImplementedError('Must be implemented in subclass')

    def disable(self):
        """Roll back from an L{enable} call.
        """
        raise NotImplementedError('Must be implemented in subclass')

    def select(self):
        """Commit to a synchronisation started by L{enable}.
        """
        raise NotImplementedError('Must be implemented in subclass')

    def poison(self):
        """Terminate all processes attached to this guard.
        """
        pass

    def __str__(self):
        return 'CSP Guard: must be subclassed.'

    def __or__(self, other):
        assert isinstance(other, Guard)
        alt = Alt(self, other)
        print 'Alt created.'
        return alt.select()

    def __ror__(self, other):
        assert isinstance(other, Guard)
        alt = Alt(self, other)
        print 'Alt created'
        alt.select()


class Channel(Guard):
    """CSP Channel objects.

    In python-csp there are two sorts of channel. In JCSP terms these
    are Any2Any, Alting channels. However, each channel creates an
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

    def __init__(self):
        self.name = uuid.uuid1()
        self._wlock = None	   # Write lock protects from races between writers.
        self._rlock = None	   # Read lock protects from races between readers.
        self._plock = None
        self._available = None     # Released if writer has made data available.
        self._taken = None         # Released if reader has taken data.
        self._is_alting = None     # True if engaged in an Alt synchronisation.
        self._is_selectable = None # True if can be selected by an Alt.
        self._has_selected = None  # True if already been committed to select.
        self._store = None # Holds value transferred by channel
        self._poisoned = False
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
        self._plock = threading.Lock()  # Fix poisoning.
        self._available = threading.Semaphore(0)
        self._taken = threading.Semaphore(0)
        # Process-safe synchronisation for CSP Select / Occam Alt.
        self._is_alting = False
        self._is_selectable = False
        # Kludge to say a select has finished (to prevent the channel
        # from being re-enabled). If values were really process safe
        # we could just have writers set _is_selectable and read that.
        self._has_selected = False

    def __getstate__(self):
        """Return state required for pickling."""
        state = [self._available._Semaphore__value,
                 self._taken._Semaphore__value,
                 self._is_alting,
                 self._is_selectable,
                 self._has_selected]
        if self._available._Semaphore__value > 0:
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
        self._is_alting = state[2]
        self._is_selectable = state[3]
        self._has_selected = state[4]
        if state[5] is not None:
            self.put(state[5])
        return

    def put(self, item):
        """Put C{item} on a process-safe store.
        """
        self.checkpoison()
        self._store = mypickle.dumps(item, protocol=1)

    def get(self):
        """Get a Python object from a process-safe store.
        """
        self.checkpoison()        
        item = mypickle.loads(self._store)
        self._store = None
        return item

    def is_selectable(self):
        """Test whether Alt can select this channel.
        """
        logging.debug('Alt THINKS _is_selectable IS: ' +
               str(self._is_selectable))
        self.checkpoison()
        return self._is_selectable

    def write(self, obj):
        """Write a Python object to this channel.
        """
        self.checkpoison()
        logging.debug('+++ Write on Channel %s started.' % self.name)        
        with self._wlock: # Protect from races between multiple writers.
            # If this channel has already been selected by an Alt then
            # _has_selected will be True, blocking other readers. If a
            # new write is performed that flag needs to be reset for
            # the new write transaction.
            self._has_selected = False
            # Make the object available to the reader.
            self.put(obj)
            # Announce the object has been released to the reader.
            self._available.release()
            logging.debug('++++ Writer on Channel %s: _available: %i _taken: %i. ' %
                   (self.name, self._available._Semaphore__value,
                    self._taken._Semaphore__value))
            # Block until the object has been read.
            self._taken.acquire()
            # Remove the object from the channel.
        logging.debug('+++ Write on Channel %s finished.' % self.name)
        return

    def read(self):
        """Read (and return) a Python object from this channel.
        """
        # FIXME: These assertions sometimes fail...why?
#        assert self._is_alting.value == Channel.FALSE
#        assert self._is_selectable.value == Channel.FALSE
        self.checkpoison()
        logging.debug('+++ Read on Channel %s started.' % self.name)
        with self._rlock: # Protect from races between multiple readers.
            # Block until an item is in the Channel.
            logging.debug('++++ Reader on Channel %s: _available: %i _taken: %i. ' %
                   (self.name, self._available._Semaphore__value,
                    self._taken._Semaphore__value))
            self._available.acquire()
            # Get the item.
            obj = self.get()
            # Announce the item has been read.
            self._taken.release()
        logging.debug('+++ Read on Channel %s finished.' % self.name)
        return obj

    def enable(self):
        """Enable a read for an Alt select.

        MUST be called before L{select()} or L{is_selectable()}.
        """
        self.checkpoison()
        # Prevent re-synchronization.
        if (self._has_selected or self._is_selectable):
            return
        self._is_alting = True
        with self._rlock:
            # Attempt to acquire _available.
            time.sleep(0.00001) # Won't work without this -- why?
            retval = self._available.acquire(blocking=False)
        if retval:
            self._is_selectable = True
        else:
            self._is_selectable = False
        logging.debug('Enable on guard', self.name, '_is_selectable:',
               self._is_selectable, '_available:',
               self._available)
        return

    def disable(self):
        """Disable this channel for Alt selection.

        MUST be called after L{enable} if this channel is not selected.
        """
        self.checkpoison()
        self._is_alting = False
        if self._is_selectable:
            with self._rlock:
                self._available.release()
            self._is_selectable = False
        return

    def select(self):
        """Complete a Channel read for an Alt select.
        """
        self.checkpoison()
        logging.debug('channel select starting')
        assert self._is_selectable == True
        with self._rlock:
            logging.debug('got read lock on channel',
                   self.name, '_available: ',
                   self._available._Semaphore__value)
            # Obtain object on Channel.
            obj = self.get()
            logging.debug('Writer got obj')
            # Notify write() that object is taken.
            self._taken.release()
            logging.debug('Writer released _taken')
            # Reset flags to ensure a future read / enable / select.
            self._is_selectable = False
            self._is_alting = False
            self._has_selected = True
            logging.debug('reset bools')
        if obj == _POISON:
            self.poison()
            raise ChannelPoison()
        return obj

    def __str__(self):
        return 'Channel using OS pipe for IPC.'

    def checkpoison(self):
        with self._plock:
            if self._poisoned:
                raise ChannelPoison()

    def poison(self):
        """Poison a channel causing all processes using it to terminate.
        """
        with self._plock:
            self._poisoned = True
            # Avoid race conditions on any waiting readers / writers.
            self._available.release() 
            self._taken.release() 

    def suspend(self):
        """Suspend this mobile channel before migrating between processes.
        """
        raise NotImplementedError('Suspend / resume not implemented')

    def resume(self):
        """Resume this mobile channel after migrating between processes.
        """
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
        self.name = uuid.uuid1()
        self._wlock = None	# Write lock.
        self._rlock = None	# Read lock.
        self._available = None
        self._taken = None
        self._is_alting = None
        self._is_selectable = None
        self._has_selected = None
        # Process-safe store.
        file_d, self._fname = tempfile.mkstemp()
        os.close(file_d)
        self._setup()
        return

    def __getstate__(self):
        """Return state required for pickling."""
        state = [mypickle.dumps(self._available, protocol=1),
                 mypickle.dumps(self._taken, protocol=1),
                 mypickle.dumps(self._is_alting, protocol=1),
                 mypickle.dumps(self._is_selectable, protocol=1),
                 mypickle.dumps(self._has_selected, protocol=1),
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
        self._available = mypickle.loads(state[0])
        self._taken = mypickle.loads(state[1])
        self._is_alting = mypickle.loads(state[2])
        self._is_selectable = mypickle.loads(state[3])
        self._has_selected = mypickle.loads(state[4])
        self._fname = state[5]
        if state[6] is not None:
            self.put(state[6])
        return

    def put(self, item):
        """Put C{item} on a process-safe store.
        """
        if self.is_poisoned: raise ChannelPoison()
        file_d = file(self._fname, 'w')
        file_d.write(mypickle.dumps(item, protocol=1))
        file_d.flush()
        file_d.close()
        return

    def get(self):
        """Get a Python object from a process-safe store.
        """
        if self.is_poisoned: raise ChannelPoison()
        stored = ''
        while stored == '':
            file_d = file(self._fname, 'r')
            stored = file_d.read()
            file_d.close()
        # Unlinking here ensures that FileChannel objects exhibit the
        # same semantics as Channel objects.
        os.unlink(self._fname)
        obj = mypickle.loads(stored)
        return obj

    def __del__(self):
        if os.path.exists(self._fname):
            # Necessary if the Channel has been deleted by poisoning.
            os.unlink(self._fname)
        return

    def __str__(self):
        return 'Channel using files for IPC.'

    def suspend(self):
        """Suspend this mobile channel before migrating between processes.
        """
        raise NotImplementedError('Suspend / resume not implemented')

    def resume(self):
        """Suspend this mobile channel after migrating between processes.
        """
        raise NotImplementedError('Suspend / resume not implemented')

    
class NetworkChannel(Channel):
    """Network channels ...
    """
    
    def __init__(self):
        self.name = Channel.NAMEFACTORY.name()
        self._wlock = None	# Write lock.
        self._rlock = None	# Read lock.
        self._available = None
        self._taken = None
        self._is_alting = None
        self._is_selectable = None
        self._has_selected = None
        # Process-safe store.
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._setup()
        return

    def __getstate__(self):
        """Return state required for pickling."""
        state = [mypickle.dumps(self._available, protocol=1),
                 mypickle.dumps(self._taken, protocol=1),
                 mypickle.dumps(self._is_alting, protocol=1),
                 mypickle.dumps(self._is_selectable, protocol=1),
                 mypickle.dumps(self._has_selected, protocol=1),
                 self._fname]
        if self._available.get_value() > 0:
            obj = self.get()
        else:
            obj = None
        state.append(obj)
        return state

    def __setstate__(self, state):
        """Restore object state after unpickling."""
        self._wlock = processing.RLock()	# Write lock.
        self._rlock = processing.RLock()	# Read lock.
        self._available = mypickle.loads(state[0])
        self._taken = mypickle.loads(state[1])
        self._is_alting = mypickle.loads(state[2])
        self._is_selectable = mypickle.loads(state[3])
        self._has_selected = mypickle.loads(state[4])
        if state[5] is not None:
            self.put(state[5])
        return

    def put(self, item):
        """Put C{item} on a process-safe store.
        """
        if self.is_poisoned: raise ChannelPoison()
        self.sock.sendto(mypickle.dumps(item, protocol=1),
                         (_HOST, _CHANNEL_PORT))
        return

    def get(self):
        """Get a Python object from a process-safe store.
        """
        if self.is_poisoned: raise ChannelPoison()
        data = self.sock.recv(_BUFFSIZE)
        obj = mypickle.loads(data)
        return obj

    def __del__(self):
        self.sock.close()
        del self
        return
    
    def __str__(self):
        return 'Channel using sockets for IPC.'

    def suspend(self):
        """Suspend this mobile channel before migrating between processes.
        """
        raise NotImplementedError('Suspend / resume not implemented')

    def resume(self):
        """Suspend this mobile channel after migrating between processes.
        """
        raise NotImplementedError('Suspend / resume not implemented')


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


def forever(func):
    """Decorator to turn a function into a CSP server process.

    It is preferable to use this rather than @process, to enable the
    CSP tracer to terminate correctly and produce a CSP model, or
    other debugging information.
    """
    
    @wraps(func)
    def _call(*args, **kwargs):
        """Call the target function."""
        return CSPServer(func, *args, **kwargs)
    return _call


### List of CSP based types (class names). Used by _is_csp_type.
_CSPTYPES = [CSPProcess, Par, Seq, Alt]


def _is_csp_type(name):
    """Return True if name is any type of CSP process."""
    for typ in _CSPTYPES:
        if isinstance(name, typ):
            return True
    return False

