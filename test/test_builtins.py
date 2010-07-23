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

    def setUp(self):
        csp = self.csp_process
        # get us some channels for later use
        self.spare_channels = [csp.Channel() for i in xrange(3)]

    def tearDown(self):
        # ignore result
        [channel.poison() for channel in self.spare_channels]

    def assertListsAlmostEqual(self, list1, list2, msg=None):
        """Compare corresponding list elements with
        `self.assertAlmostEqual` and fail with message `msg` if
        a comparison fails.
        """
        for item1, item2 in zip(list1, list2):
            self.assertAlmostEqual(item1, item2)

    def feedBuiltin(self, in_data, builtin):
        """Feed the data from `in_data` into the builtin CSPProcess
        (process/thread) and return a sequence of the corresponding
        output values.
        """
        csp = self.csp_process
        in_channel, out_channel = self.spare_channels[:2]
        started_builtin = builtin(in_channel, out_channel).start()
        out_data = []
        for data_item in in_data:
            in_channel.write(data_item)
            out_data.append(out_channel.read())
        return out_data

    def feedUnaryFloatOperation(self, in_data, expected_out_data, builtin):
        """Test an unary floating point operation `builtin`, for
        example `builtins.Sin`. Check if items in the sequence
        `in_data` have corresponding results in `expected_out_data`.
        """
        out_data = self.feedBuiltin(in_data, builtin)
        self.assertListsAlmostEqual(out_data, expected_out_data)

    def testSin(self):
        in_data = [0.0, 1.0, 4.0, -1.0, -4.0, 10.0]
        expected_data = [0.0, 0.841470984808, -0.756802495308,
                         -0.841470984808, 0.756802495308, -0.544021110889]
        self.feedUnaryFloatOperation(in_data, expected_data, builtins.Sin)

    def testCos(self):
        in_data = [0.0, 1.0, 4.0, -1.0, -4.0]
        expected_data = [1.0, 0.540302305868, -0.653643620864,
                         0.540302305868, -0.653643620864, -0.839071529076,]
        self.feedUnaryFloatOperation(in_data, expected_data, builtins.Cos)


# class TestBuiltinsWithThreads(TestBuiltinsWithProcesses):
#     csp_process = csp.cspthread


if __name__ == '__main__':
    unittest.main()
