#!/usr/bin/env python

"""Communicating sequential processes, in Python.

When using CSP Python as a DSL, this module will normally be imported
via the statement 'from csp.csp import *' and should not be imported directly.

Copyright (C) Sarah Mount, 2008-10.

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

__author__ = 'Sarah Mount <s.mount@wlv.ac.uk>'
__date__ = '2010-05-16'

#DEBUG = True
DEBUG = False

from functools import wraps # Easy decorators

import copy
import gc
import inspect
import logging
import os
import random
import sys
import tempfile
import time
import uuid
try:
    import cPickle as pickle    # Faster, only in Python 2.x
except ImportError:
    import pickle

try: # Python optimisation compiler
    import psyco
    psyco.full()
except ImportError:
    print ( 'No available optimisation' )

# Multiprocessing libary -- name changed between versions.
try:
    # Version 2.6 and above
    import multiprocessing as processing
    if sys.platform == 'win32':
        import multiprocessing.reduction
except ImportError:
    raise ImportError('No library available for multiprocessing.\n'+
                      'csp.os_process is only compatible with Python 2. 6 and above.')

### Names exported by this module
__all__ = ['set_debug', 'CSPProcess', 'CSPServer', 'Alt',
           'Par', 'Seq', 'Guard', 'Channel', 'FileChannel',
           'process', 'forever', 'Skip', '_CSPTYPES']

### Seeded random number generator (16 bytes)

_RANGEN = random.Random(os.urandom(16))


### CONSTANTS

_BUFFSIZE = 1024


class CorruptedData(Exception):
    """Used to verify that data has come from an honest source.
    """

    def __str__(self):
        return 'Data sent with incorrect authentication key.'


class NoGuardInAlt(Exception):
    """Raised when an Alt has no guards to select.
    """

    def __str__(self):
        return 'Every Alt must have at least one guard.'


### Special constants / exceptions for termination and mobility
### Better not to use classes/objects here or pickle will get confused
### by the way that csp.__init__ manages the namespace.

_POISON = ';;;__POISON__;;;'
"""Used as special data sent down a channel to invoke termination."""


class ChannelPoison(Exception):
    """Used to poison a processes and propagate to all known channels.
    """

    def __str__(self):
        return 'Posioned channel exception.'


### DEBUGGING

def set_debug(status):
    global DEBUG
    DEBUG = status
    logging.basicConfig(level=logging.NOTSET,
                        stream=sys.stdout)
    logging.info("Using multiprocessing version of python-csp.")


### Fundamental CSP concepts -- Processes, Channels, Guards

class _CSPOpMixin(object):
    """Mixin class used for operator overloading in CSP process types.
    """

    def __init__(self):
        return

    def spawn(self):
        """Start only if self is not running."""
        if not self._popen:
            processing.Process.start(self)

    def start(self):
        """Start only if self is not running."""
        if not self._popen:
            try:
                processing.Process.start(self)
                processing.Process.join(self)
            except KeyboardInterrupt:
                sys.exit()

    def join(self):
        """Join only if self is running."""
        if self._popen:
            processing.Process.join(self)

    def referent_visitor(self, referents):
        for obj in referents:
            if obj is self or obj is None:
                continue
            if isinstance(obj, Channel):
                obj.poison()
            elif ((hasattr(obj, '__getitem__') or hasattr(obj, '__iter__')) and
                  not isinstance(obj, str)):
                self.referent_visitor(obj)
            elif isinstance(obj, CSPProcess):
                self.referent_visitor(obj.args + tuple(obj.kwargs.values()))
            elif hasattr(obj, '__dict__'):
                self.referent_visitor(list(obj.__dict__.values()))

    def terminate(self):
        """Terminate only if self is running."""
        if self._popen is not None:
            processing.Process.terminate(self)

    def __gt__(self, other):
        """Implementation of CSP Seq."""
        assert _is_csp_type(other)
        seq = Seq(self, other)
        seq.start()
        return seq

    def __mul__(self, n):
        assert n > 0
        procs = [self]
        for i in range(n-1):
            procs.append(copy.copy(self))
        Seq(*procs).start()

    def __rmul__(self, n):
        assert n > 0
        procs = [self]
        for i in range(n-1):
            procs.append(copy.copy(self))
        Seq(*procs).start()


class CSPProcess(processing.Process, _CSPOpMixin):
    """Implementation of CSP processes.
    Not intended to be used in client code. Use @process instead.
    """

    def __init__(self, func, *args, **kwargs):
        processing.Process.__init__(self,
                                    target=func,
                                    args=(args),
                                    kwargs=kwargs)
        assert inspect.isfunction(func) # Check we aren't using objects
        assert not inspect.ismethod(func) # Check we aren't using objects

        _CSPOpMixin.__init__(self)
        for arg in list(self._args) + list(self._kwargs.values()):
            if _is_csp_type(arg):
                arg.enclosing = self
        self.enclosing = None

    def getName(self):
        return self._name

    def getPid(self):
        return self._parent_pid

    def __floordiv__(self, proclist):
        """
        Run this process in parallel with a list of others.
        """
        par = Par(self, *list(proclist))
        par.start()

    def __str__(self):
        return 'CSPProcess running in PID %s' % self.getPid()

    def run(self): #, event=None):
        """Called automatically when the L{start} methods is called.
        """
        try:
            self._target(*self._args, **self._kwargs)
        except ChannelPoison:
            logging.debug('%s got ChannelPoison exception in %g' %
                          (str(self), self.getPid()))
            self.referent_visitor(self._args + tuple(self._kwargs.values()))
#            if self._popen is not None: self.terminate()
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
        if gc is not None:
            gc.collect()


class CSPServer(CSPProcess):
    """Implementation of CSP server processes.
    Not intended to be used in client code. Use @forever instead.
    """

    def __init__(self, func, *args, **kwargs):
        CSPProcess.__init__(self, func, *args, **kwargs)

    def __str__(self):
        return 'CSPServer running in PID %s' % self.getPid()

    def run(self): #, event=None):
        """Called automatically when the L{start} methods is called.
        """
        try:
            generator = self._target(*self._args, **self._kwargs)
            while sys.gettrace() is None:
                next(generator)
            else:
                # If the tracer is running execute the target only once.
                next(generator)
                logging.info('Server process detected a tracer running.')
                # Be explicit.
                return None
        except ChannelPoison:
            logging.debug('%s in %g got ChannelPoison exception' %
                          (str(self), self.getPid()))
            self.referent_visitor(self._args + tuple(self._kwargs.values()))
#            if self._popen is not None: self.terminate()
        except KeyboardInterrupt:
            sys.exit()
        except Exception:
            typ, excn, tback = sys.exc_info()
            sys.excepthook(typ, excn, tback)


class Alt(_CSPOpMixin):
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
        logging.debug(str(type(self.last_selected)))
        self.last_selected.disable() # Just in case
        try:
            self.last_selected.poison()
        except Exception:
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
            logging.debug('Alt Selecting unique guard: %s' %
                          self.guards[0].name)
            self.last_selected = self.guards[0]
            while not self.guards[0].is_selectable():
                self.guards[0].enable()
            return self.guards[0].select()
        return None

    def select(self):
        """Randomly select from ready guards."""
        if len(self.guards) < 2:
            return self._preselect()
        ready = []
        while len(ready) == 0:
            for guard in self.guards:
                guard.enable()
                logging.debug('Alt enabled all guards')
            time.sleep(0.01) # Not sure about this.
            ready = [guard for guard in self.guards if guard.is_selectable()]
            logging.debug('Alt got %i items to choose from out of %i' %
                          (len(ready), len(self.guards)))
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
        ready = []
        while len(ready) == 0:
            for guard in self.guards:
                guard.enable()
                logging.debug('Alt enabled all guards')
            time.sleep(0.1) # Not sure about this.
            ready = [guard for guard in self.guards if guard.is_selectable()]
            logging.debug('Alt got %i items to choose from, out of %i' %
                          (len(ready), len(self.guards)))
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
        ready = []
        while len(ready) == 0:
            for guard in self.guards:
                guard.enable()
                logging.debug('Alt enabled all guards')
            time.sleep(0.01) # Not sure about this.
            ready = [guard for guard in self.guards if guard.is_selectable()]
            logging.debug('Alt got %i items to choose from, out of %i' %
                          (len(ready), len(self.guards)))
        self.last_selected = ready[0]
        for guard in ready[1:]:
            guard.disable()
        return ready[0].select()

    def __mul__(self, n):
        assert n > 0
        for i in range(n):
            yield self.select()

    def __rmul__(self, n):
        assert n > 0
        for i in range(n):
            yield self.select()


class Par(processing.Process, _CSPOpMixin):
    """Run CSP processes in parallel.
    """

    def __init__(self, *procs, **kwargs):
        super(Par, self).__init__(None)
        self.procs = []
        for proc in procs:
            # FIXME: only catches shallow nesting.
            if isinstance(proc, Par):
                self.procs += proc.procs
            else:
                self.procs.append(proc)
        for proc in self.procs:
            proc.enclosing = self
        logging.debug('%i processes in Par:' % len(self.procs))

    def __ifloordiv__(self, proclist):
        """
        Run this Par in parallel with a list of others.
        """
        assert hasattr(proclist, '__iter__')
        self.procs = []
        for proc in proclist:
            # FIXME: only catches shallow nesting.
            if isinstance(proc, Par):
                self.procs += proc.procs
            else:
                self.procs.append(proc)
        for proc in self.procs:
            proc.enclosing = self
        logging.debug('%i processes added to Par by //=:' % len(self.procs))
        self.start()

    def __str__(self):
        return 'CSP Par running in process %i.' % self.getPid()

    def terminate(self):
        """Terminate the execution of this process.
        FIXME: Should not be recursive. Is this ever called?!
        """
        for proc in self.procs:
            proc.terminate()
        if self._popen:
            self.terminate()

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
                proc.join()
        except ChannelPoison:
            logging.debug('%s got ChannelPoison exception in %g' %
                          (str(self), self.getPid()))
            self.referent_visitor(self._args + tuple(self._kwargs.values()))
#            if self._popen is not None: self.terminate()
        except KeyboardInterrupt:
            sys.exit()
        except Exception:
            typ, excn, tback = sys.exc_info()
            sys.excepthook(typ, excn, tback)

    def __len__(self):
        return len(self.procs)

    def __getitem__(self, index):
        try:
            return self.procs[index]
        except IndexError:
            raise IndexError

    def __setitem__(self, index, value):
        assert isinstance(value, CSPProcess)
        self.procs[index] = value

    def __contains__(self, proc):
        return proc in self.procs


class Seq(processing.Process, _CSPOpMixin):
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

    def __str__(self):
        return 'CSP Seq running in process %i.' % self.getPid()

    def start(self):
        """Start this process running.
        """
        try:
            for proc in self.procs:
                _CSPOpMixin.start(proc)
                proc.join()
        except ChannelPoison:
            logging.debug('%s got ChannelPoison exception in %g' %
                          (str(self), self.getPid()))
            self.referent_visitor(self._args + tuple(self._kwargs.values()))
            if self._popen is not None: self.terminate()
        except KeyboardInterrupt:
            sys.exit()
        except Exception:
            typ, excn, tback = sys.exc_info()
            sys.excepthook(typ, excn, tback)


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
        return Alt(self, other).select()

    def __ror__(self, other):
        assert isinstance(other, Guard)
        return Alt(self, other).select()


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
    constructor and override L{put}, L{get}, L{__del__}.
    """

    TRUE = 1
    FALSE = 0

    def __init__(self):
        self.name = uuid.uuid1()
        self._wlock = None       # Write lock protects from races between writers.
        self._rlock = None       # Read lock protects from races between readers.
        self._plock = None
        self._available = None     # Released if writer has made data available.
        self._taken = None         # Released if reader has taken data.
        self._is_alting = None     # True if engaged in an Alt synchronisation.
        self._is_selectable = None # True if can be selected by an Alt.
        self._has_selected = None  # True if already been committed to select.
        self._itemr, self._itemw = os.pipe()
        self._poisoned = None
        self._setup()
        super(Channel, self).__init__()
        logging.debug('Channel created: %s' % self.name)

    def _setup(self):
        """Set up synchronisation.

        MUST be called in __init__ of this class and all subclasses.
        """
        # Process-safe synchronisation.
        self._wlock = processing.RLock()    # Write lock.
        self._rlock = processing.RLock()    # Read lock.
        self._plock = processing.Lock()  # Fix poisoning.
        self._available = processing.Semaphore(0)
        self._taken = processing.Semaphore(0)
        # Process-safe synchronisation for CSP Select / Occam Alt.
        self._is_alting = processing.Value('h', Channel.FALSE,
                                           lock=processing.Lock())
        self._is_selectable = processing.Value('h', Channel.FALSE,
                                               lock=processing.Lock())
        # Kludge to say a select has finished (to prevent the channel
        # from being re-enabled). If values were really process safe
        # we could just have writers set _is_selectable and read that.
        self._has_selected = processing.Value('h', Channel.FALSE,
                                              lock=processing.Lock())
        # Is this channel poisoned?
        self._poisoned = processing.Value('h', Channel.FALSE,
                                          lock=processing.Lock())

    def put(self, item):
        """Put C{item} on a process-safe store.
        """
        self.checkpoison()
        os.write(self._itemw, pickle.dumps(item, protocol=1))

    def get(self):
        """Get a Python object from a process-safe store.
        """
        self.checkpoison()
        data = []
        while True:
            sval = os.read(self._itemr, _BUFFSIZE)
            logging.debug('Read from OS pipe')
            if not sval:
                break
            data.append(sval)
#            logging.debug('Pipe got data: %i, %s' % (len(sval), sval))
            if len(sval) < _BUFFSIZE:
                break
        logging.debug('Left read loop')
        logging.debug('About to unmarshall this data: %s' % b''.join(data)) 
        obj = None if data == [] else pickle.loads(b''.join(data))
        logging.debug('pickle library has unmarshalled data.')
        return obj

    def __del__(self):
        try:
            os.close(self._itemr)
            os.close(self._itemw)
        except:
            pass

    def is_selectable(self):
        """Test whether Alt can select this channel.
        """
        logging.debug('Alt THINKS _is_selectable IS: %s' %
                      str(self._is_selectable.value == Channel.TRUE))
        self.checkpoison()
        return self._is_selectable.value == Channel.TRUE

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
            self._has_selected.value = Channel.FALSE
            # Make the object available to the reader.
            self.put(obj)
            # Announce the object has been released to the reader.
            self._available.release()
            logging.debug('++++ Writer on Channel %s: _available: %i _taken: %i. ' %
                          (self.name, self._available.get_value(),
                           self._taken.get_value()))
            # Block until the object has been read.
            self._taken.acquire()
            # Remove the object from the channel.
        logging.debug('+++ Write on Channel %s finished.' % self.name)

    def read(self):
        """Read (and return) a Python object from this channel.
        """
#        assert self._is_alting.value == Channel.FALSE
#        assert self._is_selectable.value == Channel.FALSE
        self.checkpoison()
        logging.debug('+++ Read on Channel %s started.' % self.name)
        with self._rlock: # Protect from races between multiple readers.
            # Block until an item is in the Channel.
            logging.debug('++++ Reader on Channel %s: _available: %i _taken: %i. ' %
                          (self.name, self._available.get_value(),
                           self._taken.get_value()))
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
        if (self._has_selected.value == Channel.TRUE or
            self._is_selectable.value == Channel.TRUE):
            # Be explicit.
            return None
        self._is_alting.value = Channel.TRUE
        with self._rlock:
            # Attempt to acquire _available.
            time.sleep(0.00001) # Won't work without this -- why?
            if self._available.acquire(block=False):
                self._is_selectable.value = Channel.TRUE
            else:
                self._is_selectable.value = Channel.FALSE
        logging.debug('Enable on guard %s _is_selectable: %s _available: %s' %
                      (self.name, str(self._is_selectable.value),
                       str(self._available.get_value())))

    def disable(self):
        """Disable this channel for Alt selection.

        MUST be called after L{enable} if this channel is not selected.
        """
        self.checkpoison()
        self._is_alting.value = Channel.FALSE
        if self._is_selectable.value == Channel.TRUE:
            with self._rlock:
                self._available.release()
            self._is_selectable.value = Channel.FALSE

    def select(self):
        """Complete a Channel read for an Alt select.
        """
        self.checkpoison()
        logging.debug('channel select starting')
        assert self._is_selectable.value == Channel.TRUE
        with self._rlock:
            logging.debug('got read lock on channel %s _available: %s' %
                          (self.name, str(self._available.get_value())))
            # Obtain object on Channel.
            obj = self.get()
            logging.debug('got obj')
            # Notify write() that object is taken.
            self._taken.release()
            logging.debug('released _taken')
            # Reset flags to ensure a future read / enable / select.
            self._is_selectable.value = Channel.FALSE
            self._is_alting.value = Channel.FALSE
            self._has_selected.value = Channel.TRUE
            logging.debug('reset bools')
        if obj == _POISON:
            self.poison()
            raise ChannelPoison()
        return obj

    def __str__(self):
        return 'Channel using OS pipe for IPC.'

    def checkpoison(self):
        with self._plock:
            if self._poisoned.value == Channel.TRUE:
                logging.debug('%s is poisoned. Raising ChannelPoison()' % self.name)
                raise ChannelPoison()

    def poison(self):
        """Poison a channel causing all processes using it to terminate.
        """
        with self._plock:
            self._poisoned.value = Channel.TRUE
            # Avoid race conditions on any waiting readers / writers.
            self._available.release() 
            self._taken.release()


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

    def put(self, item):
        """Put C{item} on a process-safe store.
        """
        file_d = file(self._fname, 'w')
        file_d.write(pickle.dumps(item, protocol=1))
        file_d.flush()
        file_d.close()

    def get(self):
        """Get a Python object from a process-safe store.
        """
        stored = ''
        while stored == '':
            file_d = file(self._fname, 'r')
            stored = file_d.read()
            file_d.close()
        # Unlinking here ensures that FileChannel objects exhibit the
        # same semantics as Channel objects.
        os.unlink(self._fname)
        obj = pickle.loads(stored)
        return obj

    def __del__(self):
        try:
            # Necessary if the Channel has been deleted by poisoning.
            os.unlink(self._fname)
        except:
            pass

    def __str__(self):
        return 'Channel using files for IPC.'


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


def _is_csp_type(obj):
    """Return True if obj is any type of CSP process."""
    return isinstance(obj, tuple(_CSPTYPES))


def _nop():
    pass


class Skip(CSPProcess, Guard):
    """Guard which will always return C{True}. Useful in L{Alt}s where
    the programmer wants to ensure that L{Alt.select} will always
    synchronise with at least one guard.
    """

    def __init__(self):
        Guard.__init__(self)
        CSPProcess.__init__(self, _nop)
        self.name = '__Skip__'

    def is_selectable(self):
        """Skip is always selectable."""
        return True

    def enable(self):
        """Has no effect."""
        pass

    def disable(self):
        """Has no effect."""
        pass

    def select(self):
        """Has no effect."""
        return 'Skip'

    def __str__(self):
        return 'Skip guard is always selectable / process does nothing.'

