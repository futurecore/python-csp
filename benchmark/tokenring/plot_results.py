#!/usr/bin/env python

"""
Plotting results of variable ring buffer experiment.

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

from scipy import * 
from pylab import *

__author__ = 'Sarah Mount <s.mount@wlv.ac.uk>'
__date__ = 'November 2009'

FILENAME = 'token_ring.png'

subplots_adjust(hspace=0.4, wspace=0.6)

# Num of nodes in token ring
t = array([2, 4, 8, 16, 32, 64, 128, 256, 512, 1024])


yvals = {1:{'procs':array([350.057995, 
	314.430736, 157.215372, 78.607687, 39.303844,
						   19.651922, 9.825962, 4.912981, 2.456491, None, None]),
			'threads':array([314.430851, 157.215429, 78.607716, 39.303859,
							 19.651930, 9.825965, 4.912983, 2.456492, None, None]),
			'jython':array([314.431448, 157.215729, 78.607867, 39.303935,
							19.651969, 9.825985, 4.912993, 2.456502, 1.228249, 0.614125])}
		 }


subplot(111)
title('Variable sized ring buffer \nwith one token')
plot(t, yvals[1]['procs'],  'g^-')
plot(t, yvals[1]['threads'], 'k*--')
plot(t, yvals[1]['jython'], 'rx-.')

legend(['Processes reified as OS processes',
        'Processes reified as OS threads', 
        'Processes reified as Java threads'],
        loc='upper left')

xlabel('Number of nodes in token ring')
ylabel(r'Time $(\mu{}s)$')

###

#subplot(222)
#title('16 node ring buffer \nwith three tokens')
#plot(t, yvals[1]['procs'],  'g^-')
#plot(t, yvals[1]['threads'], 'k*--')
#plot(t, yvals[1]['jython'], 'rx-.')

#legend(['Processes reified as OS processes',
#        'Processes reified as OS threads', 
#        'Processes reified as Java threads'],
#        loc='upper left')

#xlabel('Number of nodes in token ring')
#ylabel(r'Time $(\mu{}s)$')

###

#subplot(223)
#title('32 node ring buffer \nwith three tokens')
#plot(t, yvals[1]['procs'],  'g^-')
#plot(t, yvals[1]['threads'], 'k*--')
#plot(t, yvals[1]['jython'], 'rx-.')

#legend(['Processes reified as OS processes',
#        'Processes reified as OS threads', 
#        'Processes reified as Java threads'],
#        loc='upper left')

#xlabel('Number of nodes in token ring')
#ylabel(r'Time $(\mu{}s)$')

###

#subplot(224)
#title('64 node ring buffer \nwith three tokens')
#plot(t, yvals[1]['procs'],  'g^-')
#plot(t, yvals[1]['threads'], 'k*--')
#plot(t, yvals[1]['jython'], 'rx-.')

#legend(['Processes reified as OS processes',
#        'Processes reified as OS threads', 
#        'Processes reified as Java threads'],
#        loc='upper left')

#xlabel('Number of nodes in token ring')
#ylabel(r'Time $(\mu{}s)$')

###

grid(True)
savefig(FILENAME, format='png')
show()
