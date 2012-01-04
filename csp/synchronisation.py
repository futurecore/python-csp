#!/usr/bin/env python

"""Primitives for IPC syncrhonisation.

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

import mmap
import os
import sys

try:
    import cPickle as pickle # Only available in Python 2.x
except ImportError:
    import pickle

if sys.platform != 'win32':
    import posix_ipc # POSIX-specific IPC
else:
    raise NotImplementedError()
#    import win32api        # TODO
#    import multiprocessing # TODO stop-gap


if sys.platform != 'win32':

    SemNotAvailable = posix_ipc.BusyError
    
    class Semaphore(object):
        """This class provides an interface to OS-provided semaphores.

        The API to 
        """

        def __init__(self, name, initial_value=0, create=True):
            self.name = name
            if create:
                self.sem = posix_ipc.Semaphore(self.name,
                                               flags=posix_ipc.O_CREAT,
                                               initial_value=initial_value)
            else:
                self.sem = posix_ipc.Semaphore(self.name)                
            self._make_methods()
            return

        def _make_methods(self):
            self.acquire = self.sem.acquire
            self.release = self.sem.release
            return

        def value(self):
            return self.sem.value
        
        def __setstate__(self, newdict):
            newdict['sem'] = posix_ipc.Semaphore(newdict['name'])
            self.__dict__.update(newdict)
            self._make_methods()
            return

        def __getstate__(self):
            newdict = self.__dict__.copy()
            del newdict['sem']
            del newdict['acquire']
            del newdict['release']
            return

        def __del__(self):
            try:
                self.sem.unlink()
            except Exception, e:
                pass
            return

    
    class Value(object):
        """Process-safe Python values, stored in shared memory.

        This class is similar to the Value class in the
        multiprocessing library. It should be used for storing a
        single, simple, fixed-size Python type such as an int or
        float. For larger or variable-sized data use the SharedMemory
        class.

        Note that we are using POSIX semaphores here to provide a simple
        lock to a portion of shared memory. Calls to
        self.semaphore.{acquire,release} can be replaced with calls to
        fcntl.fcntl.(fd,{LOCK_EX,LOCK_UN}). However, fcntl is considerably
        slower than using semaphores.
        """

        def __init__(self, name, value=0, ty=None, create=True):
            self.name = name
            self.ty = ty
            if create:
                self.semaphore = posix_ipc.Semaphore(self.name + 'semaphore',
                                                     flags=posix_ipc.O_CREAT,
                                                     initial_value=0)
                memory = posix_ipc.SharedMemory(self.name, posix_ipc.O_CREX,
                                                size=sys.getsizeof(value))
            else:
                self.semaphore = posix_ipc.Semaphore(self.name + 'semaphore')
                memory = posix_ipc.SharedMemory(self.name)
            self.mapfile = mmap.mmap(memory.fd, memory.size)
            os.close(memory.fd)
            self.mapfile.seek(0)
            pickle.dump(value, self.mapfile, protocol=2)
            self.semaphore.release()
            return

        def __del__(self):
            if not self:
                return
            self.mapfile.close()
            self.semaphore.close()
            memory = posix_ipc.SharedMemory(self.name)
            memory.close_fd()
            return

        def __getstate__(self):
            """Called when this channel is pickled, this makes the channel mobile.
            """
            newdict = self.__dict__.copy()
            del newdict['semaphore']
            del newdict['mapfile']
            return newdict

        def __setstate__(self, newdict):
            """Called when this channel is unpickled, this makes the channel mobile.
            """
            memory = posix_ipc.SharedMemory(newdict['name'])
            sem = posix_ipc.Semaphore(newdict['name'] + 'semaphore')
            newdict['semaphore'] = sem
            newdict['mapfile'] = mmap.mmap(memory.fd, memory.size)
            os.close(memory.fd)
            self.__dict__.update(newdict)
            return

        def get(self):
            self.semaphore.acquire()
            self.mapfile.seek(0)
            value = pickle.load(self.mapfile)
            self.semaphore.release()
            if self.ty is None:
                return value
            else:
                return self.ty(value)

        def set(self, value):
            self.semaphore.acquire()
            self.mapfile.seek(0)
            pickle.dump(value, self.mapfile, protocol=2)
            self.semaphore.release()
            return


    class SharedMemory(object):
        """
        """

        def __init__(self, name, size=posix_ipc.PAGE_SIZE, create=True):
            self.name = name
            self.size = size
            if create:
                memory = posix_ipc.SharedMemory(self.name, posix_ipc.O_CREX,
                                                size=self.size)
            else:
                memory = posix_ipc.SharedMemory(self.name)
            self.mapfile = mmap.mmap(memory.fd, memory.size)
            os.close(memory.fd)
            return

        def __getstate__(self):
            """Called when this channel is pickled, this makes the channel mobile.
            """
            newdict = self.__dict__.copy()
            del newdict['mapfile']
            return newdict

        def __setstate__(self, newdict):
            """Called when this channel is unpickled, this makes the channel mobile.
            """
            memory = posix_ipc.SharedMemory(newdict['name'],
                                            size=newdict['size'])
            newdict['mapfile'] = mmap.mmap(memory.fd, memory.size)
            os.close(memory.fd)
            self.__dict__.update(newdict)
            return
    
        def put(self, item):
            """Put C{item} on a process-safe store.
            """
            # TODO: Deal with the case where len(item) > size(self.mapfile)
            self.mapfile.seek(0)
            pickle.dump(item, self.mapfile, protocol=2)
            return

        def get(self):
            """Get a Python object from a process-safe store.
            """
            # TODO: Deal with the case where len(item) > size(self.mapfile)
            self.mapfile.seek(0)
            return pickle.load(self.mapfile)

        def __del__(self):
            try:
                self.mapfile.close()
                memory = posix_ipc.SharedMemory(self.name)
                memory.unlink()
            except:
                pass
            return    


    class Lock(object): # FIXME FINISH
        """Named locks implemented as bounded, POSIX semaphore.
        """

        def __init__(self, name, create=True):
            self.name = name
            if create:
                self.semaphore = posix_ipc.Semaphore(name + 'semaphore', flags=posix_ipc.O_CREAT, initial_value=1)
            else:
                self.semaphore = posix_ipc.Semaphore(name + 'semaphore')
            return

        def __del__(self):
            self.semaphore.close()
            return

        def __enter__(self):
            self.semaphore.acquire()
            return

        def __exit__(self, exc_type, exc_value, traceback):
            self.semaphore.release()
            return

        def __getstate__(self):
            """Called when this lock is pickled.
            """
            newdict = self.__dict__.copy()
            del newdict['semaphore']
            return newdict

        def __setstate__(self, newdict):
            """Called when this lock is unpickled.
            """
            semaphore = posix_ipc.Semaphore(newdict['name'] + 'semaphore')
            newdict['semaphore'] = semaphore
            self.__dict__.update(newdict)
            return

else:
    # TODO: Write win32 version of these classes.
    raise NotImplementedError()

