import sys

sys.path.insert(0, "..")

from csp.csp import *
from csp.guards import Timer

@process
def hello():
    t = Timer()
    for i in range(5):
        print i
        t.sleep(1)

if __name__ == '__main__':
    hello() * 3
    2 * hello()
