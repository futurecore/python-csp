"""
Boids simulation using python-csp and pygame.

Part4 -- Adding full flocking behaviour.

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

from csp.csp import *

import math
import operator
from functools import reduce

__author__ = 'Sarah Mount <s.mount@wlv.ac.uk>'
__date__ = 'October 2009'


def distance(first_point, second_point): (x1, y1) = first_point; (x2, y2) = second_point; return math.sqrt((x1-x2)**2 + (y1-y2)**2)

def dot_add(first_point, second_point): (x1, y1) = first_point; (x2, y2) = second_point; return [x1 + x2, y1 + y2]

def dot_minus(first_point, second_point): (x1, y1) = first_point; (x2, y2) = second_point; return [x1 - x2, y1 - y2]

def dot_prod(first_point, second_point): (x1, y1) = first_point; (x2, y2) = second_point; return [x1 * x2, y1 * y2]

def scale(point, scalar): (x, y) = point; return [x * scalar, y * scalar]


def match_neighbour_velocities(near_vel):
    xs, ys = list(list(zip(*near_vel)))
    n = len(near_vel)
    return [reduce(operator.add, xs) / n, reduce(operator.add, ys) / n]

def avoid_collision(near_pos):
    VCLOSE = 7        # Boids are very close if they are within VCLOSE pixels.
    isclose = lambda x_y: math.sqrt(x_y[0]**2 + x_y[1]**2) < VCLOSE
    vclose = list(filter(isclose, near_pos))
    if len(vclose) == 0: return (0.0, 0.0)
    neg_vclose = [dot_prod((-1.0, -1.0), vector) for vector in vclose]
    close_x, close_y = list(zip(*neg_vclose))
    return (reduce(operator.add, close_x), reduce(operator.add, close_y))

def stay_with_flock(near_pos, numnear):
    xs, ys = list(zip(*near_pos))
    return [reduce(operator.add, xs) / numnear,
            reduce(operator.add, ys) / numnear]

def apply_speed_limit(velocity):
    SPEED_LIMIT = 7.0 # Velocity limit (applies to both X and Y directions).
    if velocity[0] ** 2 + velocity[1] ** 2 > SPEED_LIMIT ** 2:
        slowdown = (SPEED_LIMIT ** 2 /
                    (velocity[0] ** 2 + velocity[1] ** 2))
        velocity = scale(velocity, slowdown)
    return velocity


@process
def simulate(infochan, SIZE):
    """
    readset = infochan
    writeset = infochan
    """
    COHESION = 0.03   # Cohesion weight.
    AVOIDANCE = 0.25  # Separation weight.
    ALIGNMENT = 0.120 # Alignment weight.
    ACCEL = 0.8       # Ideal acceleration weight.

    centre = [random.randint(0, SIZE[0]), random.randint(0, SIZE[1])]
    default_velocity = [random.choice((-1.0, 0.0, 1.0)),
                        random.choice((-1.0, 0.0, 1.0))]
    velocity = default_velocity

    while True:
        infochan.write((centre, velocity))
        possible_flockmates = infochan.read()
        if not possible_flockmates:
            velocity = default_velocity
        else:
            near_pos, near_vel = list(zip(*possible_flockmates))
            numnear = len(near_pos)
            accel = scale(match_neighbour_velocities(near_vel), ALIGNMENT)
            accel = dot_add(accel, scale(avoid_collision(near_pos), AVOIDANCE))
            accel = dot_add(accel, scale(stay_with_flock(near_pos, numnear), COHESION))
            velocity = dot_add(velocity, scale(accel, ACCEL))
            velocity = apply_speed_limit(velocity)
        centre = dot_add(centre, velocity)
        # Wrap the screen.
        if centre[0]<0: centre[0] += SIZE[0]
        elif centre[0]>SIZE[0]: centre[0] -= SIZE[0]
        if centre[1]<0: centre[1] += SIZE[1]
        elif centre[1]>SIZE[1]: centre[1] -= SIZE[1]
    return


def nearby(first_point, second_point):
    (pos1, vel1) = first_point
    (pos2, vel2) = second_point
    if pos1 == pos2 and vel1 == vel2: return False
    return distance(pos1, pos2) <= 20


@process
def FlockManager(channels, drawchan, NUMBOIDS):
    """
    readset = channels
    writeset = drawchan, channels
    """
    info = [(0,0) for i in range(len(channels))]
    relify = lambda x_y_vel: ([info[i][0][0]-x_y_vel[0][0], info[i][0][1]-x_y_vel[0][1]], x_y_vel[1])
    while True:
        for i in range(NUMBOIDS): info[i] = channels[i].read()
        drawchan.write(info)
        for i in range(NUMBOIDS):
            near = [posvel for posvel in info if nearby(info[i], posvel)]
            rel = list(map(relify, near))
            channels[i].write(rel)
    return


@process
def drawboids(drawchan, SIZE):
    """
    readset = drawchan
    writeset = 
    """
    import pygame

    FGCOL = (137, 192, 210, 100)  # Foreground colour.
    BGCOL = pygame.Color('black') # Background colour.
    FPS = 60                      # Maximum frames per second.
    CAPTION = 'python-csp example: Boids'
    FILENAME = 'boids.png'        # Screenshot file.
    QUIT = False
    
    clock = pygame.time.Clock()
    dirty, last = [], []

    pygame.init()
    screen = pygame.display.set_mode((SIZE[0], SIZE[1]), 0)
    pygame.display.set_caption(CAPTION)

    while not QUIT:
        ms_elapsed = clock.tick(FPS)
#        print ms_elapsed
        dirty = last
        for rect in last: screen.fill(BGCOL, rect)
        last = []
        positions, vels = list(zip(*drawchan.read()))
        for (x, y) in positions:
            rect = pygame.draw.circle(screen, FGCOL, (int(x), int(y)), 2, 0)
            dirty.append(rect)
            last.append(rect)
        pygame.display.update(dirty)     # Update dirty rects.
        for event in pygame.event.get(): # Process events.
            if event.type == pygame.QUIT:
                QUIT = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                pygame.image.save(screen, FILENAME)
                print('Saving boids in:' + str(FILENAME))
    drawchan.poison()
    pygame.quit()
    return


@process
def main():
    NUMBOIDS = 50                # Number of boids in simulation.
    SIZE = (800, 600)             # Screen size.
    # Set up channels for reporting boid positions / velocities.
    infochans = [Channel() for i in range(NUMBOIDS)]
    # Draw channel for the drawboids process.
    drawchan = Channel()
	# Flock manager.
    fm = FlockManager(infochans, drawchan, NUMBOIDS)
    # Generate a list of all processes in the simulation.
    procs = [simulate(infochans[i], SIZE) for i in range(NUMBOIDS)]
    procs.append(fm)
    procs.append(drawboids(drawchan, SIZE)) # Drawing process.
    simulation = Par(*procs)                # Start simulation.
    simulation.start()
    return


if __name__ == '__main__':
    main().start()
