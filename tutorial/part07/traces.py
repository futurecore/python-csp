#! /usr/bin/env python3

#
# Example oscilloscope traces.
#

from csp.cspprocess import *
from csp.builtins import Sin, Cos, GenerateFloats, Mux2, Delta2
from oscilloscope import Oscilloscope


@forever
def Random(outchan):
    """Random process.

    Generates random data and writes it to outchan.
    """
    import random
    while True:
        outchan.write(random.random())
        yield
    return


def trace_random():
    """Test the Oscilloscope with random data.
    """
    channel = Channel()
    par = Par(Random(channel), Oscilloscope(channel))
    par.start()
    return


def trace_sin():
    """Plot a sine wave on the oscilloscope.
    """
    channel = Channel()
    Par(Sin(channel), Oscilloscope(channel)).start()
    return    


def trace_cos():
    """Plot a cosine wave on the oscilloscope.
    """
    channel = Channel()
    Par(Cos(channel), Oscilloscope(channel)).start()
    return    


def trace_mux():
    """Plot sine and cosine waves on the oscilloscope.
    """
    channels = [Channel() for i in range(6)]
    par = Par(GenerateFloats(channels[0]),
              Delta2(channels[0], channels[1], channels[2]),
              Cos(channels[1], channels[3]),
              Sin(channels[2], channels[4]),
              Mux2(channels[3], channels[4], channels[5]),
              Oscilloscope(channels[5]))
    par.start()
    return    


if __name__ == '__main__':
    trace_mux()
#    trace_cos()
#    trace_sin()
#    trace_random()

