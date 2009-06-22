#!/usr/bin/env python2.5

from __future__ import division

import copy, math, struct, time
from csp.csp import *
import psyco
psyco.full()

INFINITY = float('infinity')
delta = 0.000000001 # in Java this is java.lang.Math.ulp(1.0)

class Vector(object): # Use numpy arrays instead.
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z
        return
    def __repr__(self):
        return 'Vector(%g, %g, %g)' % (self.x, self.y, self.z)
    def __add__(self, vector):
        return Vector(self.x + vector.x, self.y + vector.y, self.z + vector.z)
    def __sub__(self, vector):
        return Vector(self.x - vector.x, self.y - vector.y, self.z - vector.z)
    def dot(self, vector):
        return self.x * vector.x + self.y * vector.y + self.z * vector.z
    def mag(self):
        return math.sqrt(self.dot(self))
    def scale(self, scalar):
        return Vector(self.x * scalar, self.y * scalar, self.z * scalar)
    def unitise(self):
        return self.scale(1 / self.mag())

class Ray(object):
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction
        return
    def __repr__(self):
        return 'Ray(%s, %s)' % (repr(self.origin), repr(self.direction))

class Hit(object):
    def __init__(self, llambda, normal):
        self.llambda = llambda
        self.normal = normal
        return
    def __repr__(self):
        return 'Hit(%g, %s)' % (self.llambda, repr(self.normal))

class Scene(object):
    def intersect(self, hit, ray):
        raise NotImplementedError('Must be overridden in subclass')
    def sintersect(self, ray):
        raise NotImplementedError('Must be overridden in subclass')
    def bound(self, b): # returns a sphere
        raise NotImplementedError('Must be overridden in subclass')

class Sphere(Scene):
    def __init__(self, centre, radius):
        self.centre = centre # vector type
        self.radius = radius
        return
    def __repr__(self):
        return 'Sphere(%s, %g)' % (repr(self.centre), self.radius)
    def ray(self, ray): # Returns a float
        v = self.centre - ray.origin
        b = v.dot(ray.direction)
        disc = b**2 - v.dot(v) + self.radius**2
        if disc < 0.0: return INFINITY
        d = math.sqrt(disc)
        t2 = b + d
        if t2 < 0.0: return INFINITY
        t1 = b - d
        if t1 > 0: return t1
        return t2
    def sray(self, ray): # Returns a bool
        v = self.centre - ray.origin
        b = v.dot(ray.direction)
        disc = b**2 - v.dot(v) + self.radius**2
        if disc < 0.0: return False
        return b + math.sqrt(disc) >= 0.0
    def intersect(self, hit, ray): # Returns a Vector
        l = self.ray(ray)
        if l >= hit.llambda: return
        n = ray.origin + (ray.direction.scale(l) - self.centre)
        hit.llambda = l
        hit.normal = n.unitise()
        return
    def sintersect(self, ray): # Returns a bool
        return self.sray(ray)
    def bound(self, sphere): # Returns a Sphere
        s = (sphere.centre - self.centre).mag() + self.radius
        if sphere.radius > s:
            return Sphere(sphere.centre, sphere.radius)
        else: return Sphere(sphere.centre, s)

class Group(Scene):
    def __init__(self, bound, objs):
        self.b, self.objs = bound, objs
        return
    def __repr__(self):
        return 'Group(' + repr(self.b) + ', ' + repr(self.objs) + ')'
    def intersect(self, hit, ray): # Calls intersect() on self.objs, updates hit
        l = self.b.ray(ray)
        if l >= hit.llambda: return
        for scene in self.objs:
            scene.intersect(hit, ray)
        return
    def sintersect(self, ray): # Returns a bool
        if not self.b.sray(ray): return False
        for scene in self.objs:
            if scene.sintersect(ray): return True
        return False
    def bound(self, sphere): # Returns a Sphere
        for scene in self.objs:
            sphere = scene.bound(sphere)
        return sphere

def ray_trace(light, ray, scene): # Returns a float representing a colour
    i = Hit(INFINITY, Vector(0.0, 0.0, 0.0))
    scene.intersect(i, ray)
    if i.llambda == INFINITY: return 0.0
    o = ray.origin + (ray.direction.scale(i.llambda) +
                      i.normal.scale(delta))
    g = i.normal.dot(light)
    if g >= 0.0: return 0.0
    sray = Ray(o, light.scale(-1.0))
    if scene.sintersect(sray): return 0.0
    return -g

def create(level, centre, radius): # Returns a Group
    sphere = Sphere(centre, radius)
    if level == 1: return sphere
    x = 3.0 * radius / math.sqrt(12.0)
    objs = [sphere]
    b = Sphere(centre + Vector(0.0, radius, 0.0), 2.0 * radius)
    for dz in (-1, 1):
        for dx in (-1, 1):
            c2 = Vector(centre.x + dx*x, centre.y + x, centre.z + dz*x)
            scene = create(level - 1, c2, radius / 2.0)
            objs.append(scene)
            b = scene.bound(b)
    return Group(b, objs)

def create_run(n, level, ss, filename='scene.pgm'): 
    scene = create(level, Vector(0.0, -1.0, 0.0), 1.0)
    fp = file(filename, 'w')
    fp.write('P5\n%i %i\n255\n' % (n, n))
    channels, procs = [] , []
    sofar = 0
    for y in xrange(0, n, +1):
        for x in xrange(0, n):
            channels.append(Channel())
            procs.append(perpixel(ss,n,x,y,scene,channels[sofar]))
            sofar += 1
            print ' made proccess for pixel ' , y , x
            

    rayy = Par(*procs)
    rayy.start()
    print len(procs)
    alt = Alt(*channels)
     
    while len(alt.guards) >0:   
        print 'top of loop, #guards:', len(alt.guards)
        if len(alt.guards) == 1:
            print 'can only read from channel', alt.guards[0].name
        chn = alt.select() 
        fp.write(struct.pack('B', chn))
        print 'About to poison ' ,alt.lastSelected.name
        alt.poison() 
        print len(alt.guards) 
    print 'about to close'        
    fp.close()
    return

@process
def perpixel(ss,n,x,y,scene,chnl,_process=None):
    g = 0.0
    for dx in xrange(0, ss):
        for dy in xrange(0, ss):
            d = Vector(x + dx * 1.0 / ss - n / 2.0,
                       y + dy * 1.0 / ss - n / 2.0,
                       n)
            ray = Ray(Vector(0.0, 0.0, -4.0), d.unitise())
            g += ray_trace(Vector(-1.0, -3.0, 2.0).unitise(),
                           ray, scene)    
    print 'Value ' ,    int(0.5 + 255.0 * g / ss**2), 'writing to:', chnl.name
    chnl.write(int(0.5 + 255.0 * g / ss**2))
    _process._terminate()
    return

def run(n, scene, ss, filename='scene.pgm'):
    """Ray trace an given scene and write the results to a .pgm file.
    """
    fp = file(filename, 'w')
    fp.write('P5\n%i %i\n255\n' % (n, n))
    for y in xrange(n-1, -1, -1):
        for x in xrange(0, n):
            g = 0.0
            for dx in xrange(0, ss):
                for dy in xrange(0, ss):
                    d = Vector(x + dx * 1.0 / ss - n / 2.0,
                               y + dy * 1.0 / ss - n / 2.0,
                               n)
                    ray = Ray(Vector(0.0, 0.0, -4.0), d.unitise())
                    g += ray_trace(Vector(-1.0, -3.0, 2.0).unitise(),
                                   ray, scene)  
                    
                    
                              
            fp.write(struct.pack('B', int(0.5 + 255.0 * g / ss**2)))
    fp.close()
    return

if __name__ == '__main__':   
    import pickle

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-f', '--file', dest='file', 
                      action='store',
                      help='Load a scene from a data file.')
    parser.add_option('-s', '--size', dest='size', 
                      action='store', default=4,
                      help='Image width in pixels.')
    parser.add_option('-l', '--level', dest='level', 
                      action='store', default=1,
                      help='Recursion level for auto-generated fractal scene.')
    parser.add_option('-o', '--out', dest='out', 
                      action='store', default='scene.pgm',
                      help='Output file to write to in .pgm format.')

    (options, args) = parser.parse_args()

    if options.file:
        fp = file(options.file, 'r')
        scene = pickle.loads(fp.read())
        fp.close()
        t0 = time.time()
        run(int(options.size), scene,  3, filename=options.out)
        t = time.time() - t0
        print 'Time taken:', t, 'seconds.'
    else:
        t0 = time.time()
        create_run(int(options.size), int(options.level), 3,
                   filename=options.out)
        t = time.time() - t0
        print 'Time taken:', t, 'seconds.'
        
