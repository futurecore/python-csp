"""
Test for Python-CSP's builtin functions (processes/threads).

Most if not all of the builtins accept two channel arguments: One to
receive the input from, and one to write the output to. After the
writing for an input value is done, the builtin `yield`s and continues
to run.
"""

import sys
import unittest

sys.path.insert(0, "..")

import csp.os_process
import csp.os_thread
csp.os_thread.set_debug(True)
import csp.builtins as builtins


class TestBuiltinsWithProcesses(unittest.TestCase):
    csp_process = csp.os_process

    def setUp(self):
        csp = self.csp_process
        # Get us some channels for later use.
        self.spare_channels = [csp.Channel() for i in range(3)]

    def tearDown(self):
        # Destroy channels and processes; ignore result.
        [channel.poison() for channel in self.spare_channels]
        self.spare_channels[:] = []

    #
    # The following three methods return processes factories to be started
    #  later in parallel.
    #
    def producer(self):
        @self.csp_process.process
        def _producer(channel, values):
            for value in values:
                channel.write(value)
        return _producer

    def consumer(self):
        @self.csp_process.process
        def _consumer(channel, reads, result_channel):
            result = []
            for i in range(reads):
                value = channel.read()
                result.append(value)
            result_channel.write(result)
        return _consumer

    def coordinator(self):
        @self.csp_process.process
        def _coordinator(in_channel, out_channel, result_channel,
                         in_data, builtin, builtin_args, excess_reads):
            # Use positional arguments if requested.
            if builtin_args is None:
                called_builtin = builtin(in_channel, out_channel)
            else:
                called_builtin = builtin(in_channel, out_channel,
                                         *builtin_args)
            # Start producer, builtin and consumer in parallel.
            parallel_processes = self.csp_process.Par(
              self.producer()(in_channel, in_data),
              called_builtin,
              self.consumer()(out_channel, reads=len(in_data)+excess_reads,
                              result_channel=result_channel),
              )
            parallel_processes.start()
        return _coordinator

    #
    # Helper methods.
    #
    def feedBuiltin(self, in_data, builtin, builtin_args=None, excess_reads=0):
        """Feed the data from `in_data` into the builtin CSPProcess
        (process/thread) and return a sequence of the corresponding
        output values.

        If `builtin_args` isn't `None`, use this tuple as the
        positional arguments to the builtin. If `excess_reads` is
        greater than 0, read this many values after reading output
        values corresponding to the input and include them in the
        returned output data.
        """
        in_channel, out_channel, result_channel = self.spare_channels[:3]
        coordinator = self.coordinator()(in_channel, out_channel,
                                         result_channel, in_data,
                                         builtin, builtin_args,
                                         excess_reads)
        coordinator.start()
        result = result_channel.read()
        return result

    def assertListsAlmostEqual(self, list1, list2, msg=None):
        """Compare corresponding list elements with
        `self.assertAlmostEqual` and fail with message `msg` if
        a comparison fails.
        """
        for item1, item2 in zip(list1, list2):
            self.assertAlmostEqual(item1, item2)

    def feedUnaryFloatOperation(self, in_data, expected_out_data, builtin):
        """Test an unary floating point operation `builtin`, for
        example `builtins.Sin`. Check if items in the sequence
        `in_data` have corresponding results in `expected_out_data`.
        """
        out_data = self.feedBuiltin(in_data, builtin)
        self.assertListsAlmostEqual(out_data, expected_out_data)

    #XXX Something like this is already defined in Python 2.7.
    def assertListsEqual(self, list1, list2, msg=None):
        """Similar to `assertListsAlmostEqual`, but compare exactly."""
        for item1, item2 in zip(list1, list2):
            self.assertEqual(item1, item2)

    def feedUnaryOperation(self, in_data, expected_out_data, builtin,
                           builtin_args=None, excess_reads=0):
        """Test an unary floating point operation `builtin`, for
        example `builtins.Sin`. Check if items in the sequence
        `in_data` have corresponding results in `expected_out_data`.

        If `builtins_args` is given and not `None`, use the tuple as
        the positional arguments in the call of `builtin`. If the
        integer `excess_reads` is greater than 0, read this many
        additional bytes after `len(in_data)` reads.
        """
        # `args` is handled appropriately by `feedBuiltin`.
        out_data = self.feedBuiltin(in_data, builtin, builtin_args,
                                    excess_reads)
        self.assertListsEqual(out_data, expected_out_data)

    #
    # Test unary builtins which accept and deliver float values.
    #
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

    def testSucc(self):
        in_data = [0.0, 1.1, 99.123, 1e4, -1.0]
        expected_data = [1.0, 2.1, 100.123, 1e4+1.0, 0.0]
        self.feedUnaryFloatOperation(in_data, expected_data, builtins.Succ)

    def testPred(self):
        in_data = [1.0, 2.1, 100.123, 1e4+1.0, 0.0]
        expected_data = [0.0, 1.1, 99.123, 1e4, -1.0]
        self.feedUnaryFloatOperation(in_data, expected_data, builtins.Pred)

    #
    # Test unary builtins accepting and delivering arbitrary data.
    #
    def testPrefix(self):
        in_data = [1, 2, -3, "a", u"abc", ()]
        expected_data = [7] + in_data
        self.feedUnaryOperation(in_data, expected_data, builtins.Prefix,
                                builtin_args=(7,))

    def testId(self):
        in_data = [1, 2, -3, "a", u"abc", ()]
        expected_data = in_data
        self.feedUnaryOperation(in_data, expected_data, builtins.Id)

#
# FIXME: This shows up a synchronisation bug. Set the debug flag to
# see the gory details: csp.os_thread.set_debug(True)
#
class TestBuiltinsWithThreads(TestBuiltinsWithProcesses):
     csp_process = csp.os_thread


if __name__ == '__main__':
    unittest.main()
#    unittest.main(TestBuiltinsWithThreads, 'testId')
#    unittest.main(TestBuiltinsWithThreads, 'testSin')

