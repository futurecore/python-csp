import unittest
import csp.builtins as builtins
from math import pi

class MockInputChannel():
    def __init__(self, data):
        self.data = data[:]
    def read(self):
        if not self.data:
            raise StopIteration()
        return self.data.pop(0)

class MockOutputChannel():
    def __init__(self):
        self.data = []
    def write(self, value):
        self.data.append(value)


class TestUnaryBuiltins(unittest.TestCase):

    def with_values(self, builtin, input, expected_output, **func_args):
        in_channel = MockInputChannel(input)
        out_channel = MockOutputChannel()
        process = builtin.wrapped_function(in_channel, out_channel, **func_args)
        for _x in process: pass
        for ii, value in enumerate(expected_output):
            if isinstance(value, float):
                self.assertAlmostEqual(out_channel.data[ii], value)
            else:
                self.assertEqual(out_channel.data[ii], value)

    def testId(self):
        input_data = [3, -8l, 4.2, (), 'abc']
        self.with_values(builtins.Id, input_data, input_data)

    def testPrinter(self):
        input_data = [3, -8l, 4.2, (), 'abc']
        self.with_values(builtins.Printer, input_data,
                                           [str(x) + '\n' for x in input_data])

    def testUnaryOperatorBuilder(self):
        self.with_values(builtins.unop(lambda x: x*2 - 3),
                                            [1, 2, 3, 4], [-1, 1, 3, 5])



class TestUnaryConvenienceOperators(TestUnaryBuiltins):

    def testSin(self):
        self.with_values(builtins.Sin, [0, 1, 100, -1, -100, pi/2],
                         [0, 0.8414709848078965, -0.50636564110975879,
                             -0.8414709848078965, 0.50636564110975879, 1])

    def testCos(self):
        self.with_values(builtins.Cos, [0, 1, 100, -1, -100, pi],
                         [1, 0.54030230586813977, 0.86231887228768389,
                             0.54030230586813977, 0.86231887228768389, -1])

    def testSucc(self):
        self.with_values(builtins.Succ, [-1, 40l, 1e4, 4.2],
                                        [0, 41l, 1e4+1, 5.2])

    def testPred(self):
        self.with_values(builtins.Pred, [1, 40l, 1e4, 4.2],
                                        [0, 39l, 1e4-1, 3.2])

    def testPrefix(self):
        input_data = [3, -8l, 4.2, (), 'abc']
        self.with_values(builtins.Prefix, input_data,
                                        [7] + input_data, prefix_item=7)

    def testMult(self):
        self.with_values(builtins.Mult, [1, 5, -30, 0, 100],
                                        [3, 15, -90, 0, 300], scale=3)

    def testSign(self):
        self.with_values(builtins.Sign, ['a', 4, ()],
                                        ['_a', '_4', '_()'], prefix='_')

    def testNot(self):
        self.with_values(builtins.Not, [0, 5, -5], [-1, -6, 4])

    def testLnot(self):
        self.with_values(builtins.Lnot, [(1, 2, 3), 3, 0, True, False],
                                        [False, False, True, False, True])

    def testNeg(self):
        self.with_values(builtins.Neg, [0, 1, -2], [0, -1, 2])

# def FixedDelay(cin, cout, delay):

class TestSources(unittest.TestCase):

    def with_values(self, builtin, expected_output, **func_args):
        out_channel = MockOutputChannel()
        process = builtin.wrapped_function(out_channel, **func_args)
        for ii, value in enumerate(expected_output):
            process.next()
            if isinstance(value, float):
                self.assertAlmostEqual(out_channel.data[ii], value)
            else:
                self.assertEqual(out_channel.data[ii], value)

    def testGenerateFloats(self):
        self.with_values(builtins.GenerateFloats,
                         [0, 0.1, 0.2, 0.3, 0.4], increment=0.1)
        self.with_values(builtins.GenerateFloats,
                         [0, 1, 2, 3, 4], increment=1)

    def testZeroes(self):
        self.with_values(builtins.Zeroes, [0, 0, 0, 0, 0])

    def testGenerate(self):
        self.with_values(builtins.Generate, range(1000))

    def testFibonacci(self):
        self.with_values(builtins.Fibonacci, [1, 1, 2, 3, 5, 8, 13, 21])

#    def testClock(self):


class TestSink(unittest.TestCase):

    def testBlackhole(self):
        in_channel = MockInputChannel(list(range(1000)))
        process = builtins.Blackhole.wrapped_function(in_channel)
        for _x in range(1000):
            process.next()
        self.assertEqual(in_channel.data, [])


class TestBinaryBuiltins(unittest.TestCase):

    def with_values(self, builtin, input1, input2, expected_output):
        in_channel1 = MockInputChannel(input1)
        in_channel2 = MockInputChannel(input2)
        out_channel = MockOutputChannel()
        process = builtin.wrapped_function(in_channel1, in_channel2,
                                           out_channel)
        for _x in process: pass
        for ii, value in enumerate(expected_output):
            if isinstance(value, float):
                self.assertAlmostEqual(out_channel.data[ii], value)
            else:
                self.assertEqual(out_channel.data[ii], value)

    def testMux2(self):
        self.with_values(builtins.Mux2, [1, 2, 3], [4, 5, 6],
                                        [1, 4, 2, 5, 3, 6])

    def testBinaryOperatorBuilder(self):
        self.with_values(builtins.binop(lambda x, y: x + 2*y),
                        [1, 2, 3], [4, 5, 6], [9, 12, 15])


class TestBinaryConvenienceOperators(TestBinaryBuiltins):

    def testPlus(self):
        self.with_values(builtins.Plus, [1, 2, 3], [4, 4, 4],
                                        [5, 6, 7])
    def testSub(self):
        self.with_values(builtins.Sub, [1, 2, 3], [1, 2, 3],
                                        [0, 0, 0])
    def testMul(self):
        self.with_values(builtins.Mul, [1, 2, 3], [3, 2, 1],
                                        [3, 4, 3])
    def testDiv(self):
        self.with_values(builtins.Div, [1, 4, 9], [1, 2, 10],
                                        [1, 2, 0.9])
    def testFloorDiv(self):
        self.with_values(builtins.FloorDiv, [1, 4, 9], [1, 2, 10],
                                        [1, 2, 0])
    def testMod(self):
        self.with_values(builtins.Mod, [0, 3, 4, 5], [4, 4, 4, 4],
                                        [0, 3, 0, 1])
    def testPow(self):
        self.with_values(builtins.Pow, [1, 2, 3], [0, 1, 2],
                                        [1, 2, 9])

    def testLand(self):
        self.with_values(builtins.Land, [True, True, False, False],
                                        [True, False, True, False],
                                        [True, False, False, False])
    def testLor(self):
        self.with_values(builtins.Lor, [True, True, False, False],
                                       [True, False, True, False],
                                       [True, True, True, False])
    def testLnand(self):
        self.with_values(builtins.Lnand, [True, True, False, False],
                                         [True, False, True, False],
                                         [False, True, True, True])
    def testLnor(self):
        self.with_values(builtins.Lnor, [True, True, False, False],
                                        [True, False, True, False],
                                        [False, False, False, True])
    def testLxor(self):
        self.with_values(builtins.Lxor, [True, True, False, False],
                                        [True, False, True, False],
                                        [False, True, True, False])
    def testLShift(self):
        self.with_values(builtins.LShift, [0, 2, 65], [2, 0, 3],
                                          [0, 2, 520])
    def testRShift(self):
        self.with_values(builtins.RShift, [0, 2, 65], [2, 0, 3],
                                          [0, 2, 8])
    def testAnd(self):
        self.with_values(builtins.And, [0, 1, 1, 2, 2], [127, 3, 2, 3, 2],
                                        [0, 1, 0, 2, 2])
    def testOr(self):
        self.with_values(builtins.Or, [0, 1, 1, 2, 2], [127, 3, 2, 3, 2],
                                        [127, 3, 3, 3, 2])
    def testNand(self):
        self.with_values(builtins.Nand, [0, 1, 1, 2, 2], [127, 3, 2, 3, 2],
                                        [-1, -2, -1, -3, -3])
    def testNor(self):
        self.with_values(builtins.Nor, [0, 1, 1, 2, 2], [127, 3, 2, 3, 2],
                                        [-128, -4, -4, -4, -3])
    def testXor(self):
        self.with_values(builtins.Xor, [0, 1, 1, 2, 2], [127, 3, 2, 3, 2],
                                        [127, 2, 3, 1, 0])
    def testEq(self):
        self.with_values(builtins.Eq, [1, 2, 3], [1, 2.0, 4],
                                        [True, True, False])
    def testNe(self):
        self.with_values(builtins.Ne, [1, 2, 3], [1, 2.0, 4],
                                        [False, False, True])
    def testGeq(self):
        self.with_values(builtins.Geq, [1, 2, 3, 4], [1.1, 2, 2, 5],
                                        [False, True, True, False])
    def testLeq(self):
        self.with_values(builtins.Leq, [1, 2, 3, 4], [1.1, 2, 2, 5],
                                        [True, True, False, True])


from itertools import izip_longest
class TestDemultiplexing(unittest.TestCase):

    def with_values(self, builtin, input, output1, output2):
        in_channel = MockInputChannel(input)
        out_channel1 = MockOutputChannel()
        out_channel2 = MockOutputChannel()
        process = builtin.wrapped_function(in_channel,
                                        out_channel1, out_channel2)
        for _x in process: pass
        for ii, (v1, v2) in enumerate(izip_longest(output1, output2)):
            if v1 is not None:
                self.assertEqual(out_channel1.data[ii], v1)
            if v2 is not None:
                self.assertEqual(out_channel2.data[ii], v2)

    def testSplitter(self):
        input = range(100)
        self.with_values(builtins.Splitter, input, input, input)


