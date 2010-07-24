#!/usr/bin/env python

"""
Count the words in every file in a given directory.

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


from csp.csp import *


__author__ = 'Sarah Mount <s.mount@wlv.ac.uk>'
__date__ = 'July 2010'


@process
def word_count(filename):
    fd = file(filename)
    words = [line.split() for line in fd]
    fd.close()
    print '%s contains %i words.' % (filename, len(words))


@process
def directory_count(path):
    import glob
    import os.path
    import sys
    # Test if directory exists
    if not os.path.exists(path):
        print '%s does not exist. Exiting.' % path
        sys.exit(1)
    # Get all filenames in directory
    paths = glob.glob(path + '/*')
    files = [path for path in paths if not os.path.isdir(path) and os.path.isfile(path)]
    procs = [word_count(fd) for fd in files]
    Par(*procs).start()


if __name__ == '__main__':
    import sys
    if sys.argv <= 1:
        print 'You need to provide this script with a directory path. Exiting.'
        sys.exit(1)
    else:
        directory_count(sys.argv[1]).start()
    
