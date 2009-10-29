"""
Boids simulation using python-csp and pygame.

Part3 -- Adding basic flocking behaviour.

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
import math
import operator
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

NEARBY = 20 # Boids are neighbours if they are within NEARBY pixels.

def distance((x1, y1), (x2, y2)):
    return math.sqrt((x1-x2)**2 + (y1-y2)**2)

def dot_add((x1, y1), (x2, y2)):
    return [x1 + x2, y1 + y2]

class Boid(object):
    def __init__(self, infochan):
        self.infochan = infochan
        self.centre = [random.randint(0, SIZE[0]), random.randint(0, SIZE[1])]
        self.default_velocity = [random.choice((-1.0, 0.0, 1.0)),
                                 random.choice((-1.0, 0.0, 1.0))]
        self.velocity = self.default_velocity
        return
    def match_neighbour_velocities(self):
        xs, ys = zip(*self.near_vel)
        n = len(self.near_vel)
        return [reduce(operator.add, xs) / n, reduce(operator.add, ys) / n]
    def wrap_screen(self):
        if self.centre[0]<0: self.centre[0] += SIZE[0]
        elif self.centre[0]>SIZE[0]: self.centre[0] -= SIZE[0]
        if self.centre[1]<0: self.centre[1] += SIZE[1]
        elif self.centre[1]>SIZE[1]: self.centre[1] -= SIZE[1]
        return
    @process
    def simulate(self, _process=None):
        while True:
            self.infochan.write((self.centre, self.velocity))
            possible_flockmates = self.infochan.read()
            if not possible_flockmates:
                self.velocity = self.default_velocity
            else:
                self.near_pos, self.near_vel = zip(*possible_flockmates)
                self.velocity = self.match_neighbour_velocities()
            self.centre = dot_add(self.centre, self.velocity)
            self.wrap_screen()
        return

class FlockManager(object):
    def __init__(self, channels, drawchan):
        self.channels = channels
        self.drawchan = drawchan
        return
    def nearby(self, (pos1, vel1), (pos2, vel2)):
        if pos1 == pos2 and vel1 == vel2: return False
        return distance(pos1, pos2) <= NEARBY
    @process
    def manage_flock(self, _process=None):
        info = [(0,0) for i in range(len(self.channels))]
        relify = lambda ((x,y), vel): ([info[i][0][0]-x, info[i][0][1]-y], vel)
        while True:
            for i in range(NUMBOIDS): info[i] = self.channels[i].read()
            self.drawchan.write(info)
            for i in range(NUMBOIDS):
                near = filter(lambda posvel: self.nearby(info[i], posvel), info)
                rel = map(relify, near)
                self.channels[i].write(rel)
        return

@process
def drawboids(screen, drawchan, _process=None):
    clock = pygame.time.Clock()
    dirty, last = [], []
    while True:
        ms_elapsed = clock.tick(FPS)
#        print ms_elapsed
        dirty = last
        for rect in last: screen.fill(BGCOL, rect)
        last = []
        positions, vels = zip(*drawchan.read())
        for (x, y) in positions:
            rect = pygame.draw.circle(screen, FGCOL, (int(x), int(y)), 2, 0)
            dirty.append(rect)
            last.append(rect)
        pygame.display.update(dirty)     # Update dirty rects.
        for event in pygame.event.get(): # Process events.
            if event.type == pygame.QUIT:
                drawchan.poison()
                pygame.quit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                pygame.image.save(screen, FILENAME)
                print 'Saving boids in:', FILENAME        
    return

@process
def main(_process=None):
    pygame.init()
    screen = pygame.display.set_mode((SIZE[0], SIZE[1]), 0)
    pygame.display.set_caption(CAPTION)
    # Set up channels for reporting boid positions / velocities.
    poschans = [Channel() for i in range(NUMBOIDS)]
    boids = [Boid(poschans[i]) for i in range(NUMBOIDS)]
    drawchan = Channel()                      # Draw channel.
    fm = FlockManager(poschans, drawchan)     # Cell object.
    # Generate a list of all processes in the simulation.
    procs = [boids[i].simulate() for i in range(NUMBOIDS)]
    procs.append(fm.manage_flock())           # Manager process.
    procs.append(drawboids(screen, drawchan)) # Drawing process.
    simulation = Par(*procs)                  # Start simulation.
    simulation.start()
    return

if __name__ == '__main__':
    main().start()
