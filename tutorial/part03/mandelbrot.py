#!/usr/bin/env python

# Mandelbrot set computed in parallel using python-csp.
# Multiple-producer, single consumer architecture.

# Copyright (C) Sarah Mount, 2009.

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have rceeived a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA


from csp.csp import *
import math
import numpy
import pygame

__author__ = 'Sarah Mount <s.mount@wlv.ac.uk>'
__date__ = 'December 2008'

MAXITER = 100
"""@var: Number of iterations used to determine each pixel of the
fractal image.
@see: L{mandelbrot}
"""


def get_colour(mag, cmin=0, cmax=100):
    """Given a float, returns an RGB triple.
    Recipe 9.10 from the Python Cookbook.

    @type mag: C{int}
    @param mag: Magnitude value from which to calculate RGB triple.
    @type cmin: C{int}
    @keyword cmin: Minimum possible value for C{mag}.
    @type cmax: C{int}
    @keyword cmax: Maximum possible value for C{mag}.
    @rtype: C{tuple}
    @return: An integer tuple representing an RGB value.
    """
    assert cmin != cmax
    a = float(mag-cmin)/(cmax-cmin)
    blue = min((max((4*(0.75-a), 0.)), 1.))
    red = min((max((4*(a-0.25), 0.)), 1.))
    green = min((max((4*math.fabs(a-0.5)-1., 0)), 1.))
    return int(255*red), int(255*green), int(255*blue)


@process
def mandelbrot(xcoord, dimension, cout, acorn=-2.0, bcorn=-1.250):
    """Calculate pixel values for a single column of a Mandelbrot set.

    Writes an image column to C{cout}. An image column is a list of
    RGB triples. The list should be of length C{height}. Uses the
    normalized iteration count algorithm to smooth the colour
    gradients of the area outside the set.

    readset =
    writeset = cout
    
    @type xcoord: C{int}
    @param xcoord: x-coordinate of this image column.
    @type width: C{int}
    @param width: Width of the overall Mandelbrot fractal.
    @type height: C{int}
    @param height: Height of the overall Mandelbrot fractal.
    @type cout: L{csp.csp.Channel}
    @param cout: Channel down which image column will be sent.
    @type acorn: C{float}
    @keyword acorn: Seed value for fractal generation (real part).
    @type bcorn: C{float}
    @keyword bcorn: Seed value for fractal generation (imaginary part).
    """
    (width, height) = dimension
    # nu implements the normalized iteration count algorithm
    nu = lambda zz, n: n + 1 - math.log(math.log(abs(zz)))/math.log(2)
    imgcolumn = [0. for i in range(height)]
    for ycoord in range(height):
        z = complex(0., 0.)
        c = complex(acorn + xcoord*2.5/float(width),
                    bcorn + ycoord*2.5/float(height))
        for i in range(MAXITER):
            z = complex(z.real**2 - z.imag**2 + c.real,
                        2*z.real*z.imag + c.imag)
            if abs(z)**2 > 4:
                break
        if i == MAXITER - 1: # Point lies inside the Mandelbrot set.
            colour = (0, 0, 0)
        else: # Point lies outside the Mandelbrot set.
            colour = get_colour(nu(z, i), cmax=MAXITER)
        imgcolumn[ycoord] = colour
    cout.write((xcoord, imgcolumn))
    return


@process
def consume(size, filename, cins):
    """Consumer process to aggregate image data for Mandelbrot fractal.

    readset = cins
    writeset =
    
    @type size: C{tuple}
    @param size: Width and height of generated fractal image.
    @type filename: C{str}
    @param filename: File in which to save generated fractal image.
    @type cins: C{list}
    @param cins: Input channels from which image columns will be read.
    """
    # Create initial pixel data
    pixmap = numpy.zeros((size[0], size[1], 3), dtype=numpy.int8)
    pygame.init()
    screen = pygame.display.set_mode((size[0], size[1]), 0)
    pygame.display.set_caption('python-csp Mandelbrot fractal example.')
    # Wait on channel events
    gen = len(cins) * Alt(*cins)
    for i in range(len(cins)):
        xcoord, column = next(gen)
        # Update column of blit buffer
        pixmap[xcoord] = column
        # Update image on screen.
        pygame.surfarray.blit_array(screen, pixmap)
        pygame.display.update(xcoord, 0, 1, size[1])
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                pygame.image.save(screen, filename)
            elif event.type == pygame.QUIT:
                for channel in cins:
                    channel.poison()
                pygame.quit()

@process
def main(size, filename):
    """Manage all processes and channels required to generate fractal.

    @type size: C{tuple}
    @param size: Size of generated Mandelbrot fractal image.
    @type filename: C{str}
    @param filename: Name of file in which to store generated fractal image.
    """
    channels, processes = [], []
    for x in range(size[0]):  # One producer + channel for each image column.
        channels.append(Channel())
        processes.append(mandelbrot(x, size, channels[x]))
    processes.insert(0, consume(size, filename, channels))
    mandel = Par(*processes).start()
    return

if __name__ == '__main__':
    size = (320, 240)
    main(size, 'manelbrot.png').start()
