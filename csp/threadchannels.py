__author__ = 'Sarah Mount <s.mount@wlv.ac.uk>'
__date__ = 'June 2009'

#CHDEBUG = True
CHDEBUG = False


def _chdebug(*args):
    """Customised debug logging.

    FIXME: Replace this with the builtin logging module.
    """
    smap = map(str, args)
    if CHDEBUG:
        print 'CHDEBUG:', ' '.join(smap)

import socket
import sys
import tempfile
import threading
import uuid

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
        _chdebug('Alt THINKS _is_selectable IS: ' +
               str(self._is_selectable))
        self.checkpoison()
        return self._is_selectable

    def write(self, obj):
        """Write a Python object to this channel.
        """
        self.checkpoison()
        _chdebug('+++ Write on Channel %s started.' % self.name)        
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
            _chdebug('++++ Writer on Channel %s: _available: %i _taken: %i. ' %
                   (self.name, self._available._Semaphore__value,
                    self._taken._Semaphore__value))
            # Block until the object has been read.
            self._taken.acquire()
            # Remove the object from the channel.
        _chdebug('+++ Write on Channel %s finished.' % self.name)
        return

    def read(self):
        """Read (and return) a Python object from this channel.
        """
        # FIXME: These assertions sometimes fail...why?
#        assert self._is_alting.value == Channel.FALSE
#        assert self._is_selectable.value == Channel.FALSE
        self.checkpoison()
        _chdebug('+++ Read on Channel %s started.' % self.name)
        with self._rlock: # Protect from races between multiple readers.
            # Block until an item is in the Channel.
            _chdebug('++++ Reader on Channel %s: _available: %i _taken: %i. ' %
                   (self.name, self._available._Semaphore__value,
                    self._taken._Semaphore__value))
            self._available.acquire()
            # Get the item.
            obj = self.get()
            # Announce the item has been read.
            self._taken.release()
        _chdebug('+++ Read on Channel %s finished.' % self.name)
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
        _chdebug('Enable on guard', self.name, '_is_selectable:',
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
        _chdebug('channel select starting')
        assert self._is_selectable == True
        with self._rlock:
            _chdebug('got read lock on channel',
                   self.name, '_available: ',
                   self._available._Semaphore__value)
            # Obtain object on Channel.
            obj = self.get()
            _chdebug('Writer got obj')
            # Notify write() that object is taken.
            self._taken.release()
            _chdebug('Writer released _taken')
            # Reset flags to ensure a future read / enable / select.
            self._is_selectable = False
            self._is_alting = False
            self._has_selected = True
            _chdebug('reset bools')
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
        self.name = Channel.NAMEFACTORY.name()
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
