"""
Boids simulation using python-csp and pygame.

Part 2 -- Adding movement to the boids.

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
along with this program; if not, write to the Free Software
"""

from csp.cspprocess import *
from pygame.locals import *
import copy
import pygame

__author__ = 'Sarah Mount <s.mount@wlv.ac.uk>'
__date__ = 'October 2009'

NUMBOIDS = 100                # Number of boids in simulation.
FILENAME = 'boids.png'        # Screenshot file.
FGCOL = (137, 192, 210, 100)  # Foreground colour.
BGCOL = pygame.Color('black') # Background colour.
FPS = 60                      # Maximum frames per second.
SIZE = (800, 600)             # Screen size.
CAPTION = 'python-csp example: Boids'

class Boid(object):
    def __init__(self, poschan):
        self.centre = [random.randint(0, SIZE[0]), random.randint(0, SIZE[1])]
        self.poschan = poschan        
        return
    def simulate(self, _process=None):
        while True:
            self.centre = random.randint(0, SIZE[0]), random.randint(0, SIZE[1])
            self.poschan.write(self.centre)
        return

@process
def drawboids(screen, poschans, _process=None):
    clock = pygame.time.Clock()
    dirty, last = [], []
    chansize = len(poschans)
    while True:
        ms_elapsed = clock.tick(FPS)
#        print ms_elapsed
        dirty = last
        for rect in last: screen.fill(BGCOL, rect)
        last = []
        for channel in poschans:
            x, y = channel.read()
            rect = pygame.draw.circle(screen, FGCOL, (int(x), int(y)), 2, 0)
            dirty.append(rect)
            last.append(rect)
        pygame.display.update(dirty)     # Update dirty rects.
        for event in pygame.event.get(): # Process events.
            if event.type == pygame.QUIT:
                for chan in poschans: chan.poison()
                pygame.quit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                pygame.image.save(screen, FILENAME)
                print 'Saving boids in:', FILENAME        
    return

def main():
    pygame.init()
    screen = pygame.display.set_mode((SIZE[0], SIZE[1]), 0)
    pygame.display.set_caption(CAPTION)
    # Set up channels for reporting boid positions / velocities.
    poschans = [Channel() for i in range(NUMBOIDS)]
    boids = [Boid(poschans[i]) for i in range(NUMBOIDS)]
    # Draw channel for the drawboids process.
    drawchan = Channel()
    # Generate a list of all processes in the simulation.
    procs = [CSPProcess(boids[i].simulate) for i in range(NUMBOIDS)]
    procs.append(drawboids(screen, poschans)) # Drawing process.
    simulation = Par(*procs)                  # Start simulation.
    simulation.start()
    return

if __name__ == '__main__':
    main()
