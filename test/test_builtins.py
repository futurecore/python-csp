"""
Test for Python-CSP's builtin functions (processes/threads).

Most if not all of the builtins accept two channel arguments: One to
receive the input from, and one to write the output to. After the
writing for an input value is done, the builtin `yield`s and continues
to run.
"""

import unittest

# Make shortcuts. Don't use `from ... import *`, so we can still
#  access both the process and the threading variety
import csp.cspprocess
import csp.cspthread
import csp.builtins as builtins


class TestBuiltinsWithProcesses(unittest.TestCase):
    csp_process = csp.cspprocess

    def feed_builtin(self, in_data, builtin):
        """Feed the data from `in_data` into the builtin CSPProcess
        (process/thread) and return a sequence of the corresponding
        output values.
        """
        csp = self.csp_process
        in_channel = csp.Channel()
        out_channel = csp.Channel()
        started_builtin = builtin(in_channel, out_channel).start()
        out_data = []
        for data_item in in_data:
            in_channel.write(data_item)
            out_data.append(out_channel.read())
        return out_data

    def test_sin(self):
        print self.feed_builtin([0, 0.1], builtins.Sin)


# class TestBuiltinsWithThreads(unittest.TestCase):
#     csp_process = csp.cspthread


if __name__ == '__main__':
    unittest.main()
