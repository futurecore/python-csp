from unittest import TestCase, main
import tempfile
from csp.csp import process, CSP_IMPLEMENTATION

if CSP_IMPLEMENTATION == 'os_thread':
    from threading import Event
else:
    from multiprocessing import Event

class BaseCspTest(TestCase):
    """Provides an output mechanism for asserting the output of
    parallel running processes or threads. Python's builtin datatypes
    will be copied for each process. Instead we use a file here."""

    def setUp(self):
        self.outpipe = tempfile.TemporaryFile(mode='wt+')
        self.events = []

    def proc(self, x):
        event = Event()
        self.events.append(event)
        def tester(event):
            self.outpipe.write(str(x))
            self.outpipe.flush()
            event.set()
        return process(tester)(event)

    def output(self):
        for ev in self.events:
            ev.wait()
        self.outpipe.seek(0)
        return self.outpipe.read()

