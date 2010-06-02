#! /usr/bin/env python3

"""
Simple oscilloscope traces for python-csp.
Requires Pygame.

Features:
    * Press 's' to save an oscilloscope trace as a PNG.
    * Press UP and DOWN to scale the input more / less.

Copyright (C) Sarah Mount, 2009.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have rceeived a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


from csp.cspprocess import *

import copy
import Numeric
import pygame


__author__ = 'Sarah Mount <s.mount@wlv.ac.uk>'
__date__ = 'November 2009'
__version__ = '0.2'


@forever
def Oscilloscope(inchan, scale=1.0, _process=None):
    # Constants
    WIDTH, HEIGHT = 512, 256
    TRACE, GREY = (80, 255, 100), (110, 110, 110)
    caption = 'Oscilloscope'
    filename = caption + '.png'
    # Open window
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), 0)
    pygame.display.set_caption(caption)
    # Create a blank chart with vertical ticks, etc
    blank = Numeric.zeros((WIDTH, HEIGHT, 3))
    # Draw x-axis
    xaxis = HEIGHT/2
    blank[::, xaxis] = GREY
    # Draw vertical ticks
    vticks = [-100, -50, +50, +100]
    for vtick in vticks: blank[::5, xaxis + vtick] = GREY # Horizontals
    for vtick in vticks: blank[::50, ::5] = GREY          # Verticals
    # Draw the 'blank' screen.
    pygame.surfarray.blit_array(screen, blank)      # Blit the screen buffer
    pygame.display.flip()                           # Flip the double buffer
    # ydata stores data for the trace.
    ydata = [0.0 for i in range(WIDTH)] # assert len(ydata) <= WIDTH
    QUIT = False
    while not QUIT:
        pixels = copy.copy(blank)
        ydata.append(inchan.read() * scale)
        ydata.pop(0)
        for x in range(WIDTH):
            try: pixels[x][xaxis - int(ydata[x])] = TRACE
            except: pass
        pygame.surfarray.blit_array(screen, pixels)     # Blit the screen buffer
        pygame.display.flip()                           # Flip the double buffer
        #pygame.display.update(0, xaxis-100, WIDTH, 201) # Flip the double buffer
        del pixels # Use constant space.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                QUIT = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                pygame.image.save(screen, filename)
                print('Saving oscope image in:' + str ( filename ) )
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                scale += 10.0
                print('Oscilloscope scaling by %f' % scale)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                if scale - 10.0 > 0.0: scale -= 10.0
                print('Oscilloscope scaling by %f' % scale)
        yield
    inchan.poison()
    pygame.display.quit()
    return


@forever
def MultipleOscilloscope(inchannels, _process=None):
    # TODO: add multiple Oscilloscope traces.
    # Place and size the traces automatically:
    # >>> pygame.display.list_modes()
    # [(1024, 600), (800, 600), (720, 400), (640, 480), (640, 400), (640, 350)]
    # >>> 
    raise NotImplementedError('Not implemented just yet...')


@forever
def __Random(outchan, _process=None):
    """Random process.

    Generates random data and writes it to outchan.
    """
    import random
    while True:
        outchan.write(random.random())
        yield
    return


def __test_random():
    """Test the Oscilloscope with random data.
    """
    channel = Channel()
    par = Par(__Random(channel), Oscilloscope(channel))
    par.start()
    return


def __test_sin():
    """Plot a sine wave on the oscilloscope.
    """
    channel = Channel()
    Par(dsp.Sin(channel), Oscilloscope(channel)).start()
    return    


def __test_cos():
    """Plot a cosine wave on the oscilloscope.
    """
    channel = Channel()
    Par(dsp.Cos(channel), Oscilloscope(channel)).start()
    return    


def __test_mux():
    """Plot sine and cosine waves on the oscilloscope.
    """
    import dsp
    from csp.builtins import Delta2, Mux2
    channels = [Channel() for i in range(6)]
    par = Par(dsp.GenerateFloats(channels[0]),
              Delta2(channels[0], channels[1], channels[2]),
              dsp.Cos(channels[1], channels[3]),
              dsp.Sin(channels[2], channels[4]),
              Mux2(channels[3], channels[4], channels[5]),
              Oscilloscope(channels[5]))
    par.start()
    return    


def __test_tan():
    """Plot a tangent wave on the oscilloscope.
    """
    import dsp
    channels = [Channel() for i in range(2)]
    par = Par(dsp.GenerateFloats(channels[0]),
              dsp.Tan(channels[0], channels[1]),
              Oscilloscope(channels[1]))
    par.start()
    return    


if __name__ == '__main__':
#    __test_tan()
    __test_mux()
#    __test_cos()
#    __test_sin()
#    __test_random()

