"""
Boids simulation using python-csp and pygame.

Part4 -- Adding fullt flocking behaviour.

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

NEARBY = 50.0     # Boids are neighbours if they are within NEARBY pixels.
VCLOSE = 7        # Boids are very close if they are within VCLOSE pixels.
COHESION = 0.03   # Cohesion weight.
AVOIDANCE = 0.25  # Separation weight.
ALIGNMENT = 0.120 # Alignment weight.
ACCEL = 0.8       # Ideal acceleration weight.
SPEED_LIMIT = 7.0 # Velocity limit (applies to both X and Y directions).

def distance((x1, y1), (x2, y2)): return math.sqrt((x1-x2)**2 + (y1-y2)**2)

def dot_add((x1, y1), (x2, y2)): return [x1 + x2, y1 + y2]

def dot_minus((x1, y1), (x2, y2)): return [x1 - x2, y1 - y2]

def dot_prod((x1, y1), (x2, y2)): return [x1 * x2, y1 * y2]

def scale((x, y), scalar): return [x * scalar, y * scalar]

class Boid(object):
    def __init__(self, infochan):
        self.infochan = infochan
        self.centre = [random.randint(0, SIZE[0]), random.randint(0, SIZE[1])]
        self.default_velocity = scale(dot_minus(self.centre, (100.0, 100.0)), 0.01)
        self.velocity = self.default_velocity
        return
    def match_neighbour_velocities(self):
        xs, ys = zip(*self.near_vel)
        mean = [reduce(operator.add, xs) / self.numnear,
                reduce(operator.add, ys) / self.numnear]
        return dot_minus(mean, self.velocity)
    def avoid_collision(self):
        isclose = lambda (x,y): math.sqrt(x**2 + y**2) < VCLOSE
        vclose = filter(isclose, self.near_pos)
        if len(vclose) == 0: return (0.0, 0.0)
        neg_vclose = map(lambda vector: dot_prod((-1.0, -1.0), vector), vclose)
        close_x, close_y = zip(*neg_vclose)
        return (reduce(operator.add, close_x), reduce(operator.add, close_y))
    def stay_with_flock(self):
        xs, ys = zip(*self.near_pos)
        return [reduce(operator.add, xs) / self.numnear,
                reduce(operator.add, ys) / self.numnear]
    def apply_speed_limit(self):
        if self.velocity[0] ** 2 + self.velocity[1] ** 2 > SPEED_LIMIT ** 2:
            slowdown = (SPEED_LIMIT ** 2 /
                        (self.velocity[0] ** 2 + self.velocity[1] ** 2))
            self.velocity = scale(self.velocity, slowdown)
        return
    def wrap_screen(self):
        if self.centre[0]<0: self.centre[0] += SIZE[0]
        elif self.centre[0]>SIZE[0]: self.centre[0] -= SIZE[0]
        if self.centre[1]<0: self.centre[1] += SIZE[1]
        elif self.centre[1]>SIZE[1]: self.centre[1] -= SIZE[1]
        return
    def simulate(self, _process=None):
        while True:
            self.infochan.write((self.centre, self.velocity))
            possible_flockmates = self.infochan.read()
            if not possible_flockmates: self.velocity = self.default_velocity
            else:
                self.near_pos, self.near_vel = zip(*possible_flockmates)
                self.numnear = len(self.near_pos)
                accel = scale(self.match_neighbour_velocities(), ALIGNMENT)
                accel = dot_add(accel, scale(self.avoid_collision(), AVOIDANCE))
                accel = dot_add(accel, scale(self.stay_with_flock(), COHESION))
                self.velocity = dot_add(self.velocity, scale(accel, ACCEL))
                self.apply_speed_limit()
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
    def manage_flock(self, _process=None):
        info = [(0,0) for i in range(len(self.channels))]
        relify = lambda ((x,y), vel): ([x-info[i][0][0], y-info[i][0][1]], vel)
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
    global SIZE, COHESION, AVOIDANCE, ALIGNMENT, ACCEL
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

def main():
    pygame.init()
    screen = pygame.display.set_mode((SIZE[0], SIZE[1]), 0)
    pygame.display.set_caption(CAPTION)
    # Set up channels for reporting boid positions / velocities.
    poschans = [Channel() for i in range(NUMBOIDS)]
    boids = [Boid(poschans[i]) for i in range(NUMBOIDS)]
    drawchan = Channel()                      # Draw channel.
    fm = FlockManager(poschans, drawchan)           # Cell object.
    # Generate a list of all processes in the simulation.
    procs = [CSPProcess(boids[i].simulate) for i in range(NUMBOIDS)]
    procs.append(CSPProcess(fm.manage_flock)) # Manager process.
    procs.append(drawboids(screen, drawchan)) # Drawing process.
    simulation = Par(*procs)                  # Start simulation.
    simulation.start()
    return

if __name__ == '__main__':
    main()
