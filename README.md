python-csp: Communicating Sequential Processes for Python
=========================================================

Copyright (C) Sarah Mount, 2009 under the GNU GPL v2. See the file LICENSE for
more details.

Installation
------------

python-csp can be installed using PIP (PIP Installs Python):

    $ sudo pip install python-csp

or from a source distribution using setup.py:

    $ sudo python setup.py install


Introduction
------------

python-csp adds C.A.R. (Tony) Hoare's Communicating Sequential Processes to 
Python. A brief example:

```python
>>> @process
... def writer(channel, n):
...      for i in xrange(n):
...              channel.write(i)
...      channel.poison()
...      return
... 
>>> @process
... def reader(channel):
...      while True:
...              print channel.read()
... 
>>> chan = Channel()
>>> Par(reader(chan), writer(chan, 5)).start()
0
1
2
3
4
>>>
```

Documentation.
-------------

There are several sources of documentation for python-csp:

 * If you are running the python-csp shell, type "info csp" to list available in-shell help.

 * A user guide exists in the `tutorial/` directory of the source.

 * `examples/` contains some larger example programs.


Publications.
------------

S. Mount, M. Hammoudeh, S. Wilson, R. Newman (2009) CSP as a Domain-Specific 
Language Embedded in Python and Jython. In Proceedings of Communicating Process
Architectures 2009. Eindoven, Netherlands. 1st -- 4th November 2009. Published 
IOS Press.
