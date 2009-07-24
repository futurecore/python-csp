#!/usr/bin/env python2.6


from csp.cspthread import *



if __name__ == '__main__':
    c = []
    c.append(Channel())
    c.append(Channel())
    c.append(Channel())
    
    f = Fibonacci(c[0])
    g = Generate(c[1])
    m = Multiply(c[0],c[1],c[2])
    p = Printer(c[2])
    
    par = Par(f,g,m,p)
    par.start()

