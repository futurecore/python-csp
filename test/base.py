from unittest import TestCase, main
import tempfile
from csp.csp import process

class BaseCspTest(TestCase):
    """Provides an output mechanism for asserting the output of
    parallel running processes or threads. Python's builtin datatypes
    will be copied for each process. Instead we use a file here."""

    def setUp(self):
        self.outpipe = tempfile.TemporaryFile(mode='wt+')

    def proc(self, x):
        def tester():
            self.outpipe.write(str(x))
            self.outpipe.flush()
        return process(tester)()

    def source(self, data, channel_out):
        def tester(cout):
            for x in data:
                cout.write(x)
        return process(tester)(channel_out)

    def sink(self, length, channel_in):
        def tester(length, cin):
            for ii in range(length):
                x = cin.read()
                self.outpipe.write(str(x))
            self.outpipe.flush()
        return process(tester)(length, channel_in)

    def output(self):
        self.outpipe.seek(0)
        return self.outpipe.read()

