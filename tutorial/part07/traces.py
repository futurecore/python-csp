#!/usr/bin/env python

#
# Example oscilloscope traces.
#

import sys
from csp.csp import *
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
    channels = Channel(), Channel()
    par = Par(GenerateFloats(channels[0]),
              Sin(channels[0], channels[1]),
              Oscilloscope(channels[1]))
    par.start()
    return    


def trace_cos():
    """Plot a cosine wave on the oscilloscope.
    """
    channels = Channel(), Channel()
    par = Par(GenerateFloats(channels[0]),
              Cos(channels[0], channels[1]),
              Oscilloscope(channels[1]))
    par.start()
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

EXAMPLES = {}
for name, func in globals().items():
    if name.startswith('trace_'):
        EXAMPLES[name[6:]] = func

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Syntax: python {0} {1}'.format(sys.argv[0],
                                              ' | '.join(EXAMPLES.keys())))
        for name, func in EXAMPLES.items():
            print(' {0:<9} {1}'.format(name, func.func_doc.strip()))
    elif sys.argv[1] not in EXAMPLES:
        print('Unknown example {0}'.format(sys.argv[1]))
    else:
        print('Use cursor up/down for scaling, s for save and q for quit')
        EXAMPLES[sys.argv[1]]()

