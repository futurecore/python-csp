from csp.csp import Par, process

import sys
sys.path.append('../')
from CChannel import CChannel as Channel
del sys


@process
def out(cout):
    i =0;
    while True:
        print "PYTHON: About to write " , i , "\n"
        cout.write(i)
        print "PYTHON: Have written " , i, "\n"
        i = i +1
    

@process
def inn(cin):
    while True:
        print "PYTHON: About to read \n"
        a = cin.read()
        print "PYTHON: Read ",a,"\n"


if __name__ == '__main__':

    c = Channel()
    p = Par(out(c),inn(c))
    p.start()
