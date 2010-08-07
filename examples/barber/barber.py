"""
Solution to the sleeping barber problem in python-csp.

Copyright (C) Sarah Mount, 2010.

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

__date__ = 'July 2010'
__author__ = 'Sarah Mount <s.mount@wlv.ac.uk>'


from csp.csp import *
from csp.builtins import Printer
from csp.guards import Timer

from queue import BoundedQueue as Queue


@process
def generate_customers(out_chan, printer):
    import random
    customers = ['Michael Palin', 'John Cleese', 'Terry Jones',
                 'Terry Gilliam', 'Graham Chapman']
    while True:
        python = random.choice(customers)
        printer.write('{0} needs a good shave!'.format(python))
        out_chan.write(python)


@process
def barber(door, printer):
    import random
    timer = Timer()
    while True:
        printer.write('Barber is sleeping.')
        customer = door.read()
        print_c.write('The barber has woken to give {0} a shave.'.format(customer))
        timer.sleep(random.random() * 5)
    

@process
def main(max_chairs):
    door_in, door_out = Channel(), Channel()
    printer = Channel()
    Par(generate_customers(door_in, printer),
        Queue(door_in, door_out, max_chairs),
        barber(door_out, printer)).start()


if __name__ == '__main__':
    # Start simulation with 5 chairs in waiting room.
    main(5).start()
