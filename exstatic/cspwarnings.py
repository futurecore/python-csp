#!/usr/bin/env python

"""
Exstatic errors and warnings for CSP.

TODO: Document this module.

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

import exstatic.warnings

__all__ = ['errcodes', 'list_error_codes', 'create_error', 'reset_errors',
           'get_errors', 'print_errors']

errcodes = {
    # Information.
    'I001':'Function is a CSP process or server process',
    # Warnings.
    'W001':'Channel in both readset and writeset.',
    'W002':'No readset given in documentation.',
    'W003':'No writeset given in documentation.',
    'W004':'@process or @forever applied to method (rather than function)',
    # Errors.
    'E001':'Process / forever decorator wraps a method, not a function.',
    'E002':'Channel in readset is not a formal parameter to this process.',
    'E003':'Channel in writeset is not a formal parameter to this process.',
    'E004':'Channel appears in documented readset but not read from in function body.',
    'E005':'Channel is read from in function body but does not appear in documented readset',
    'E006':'Channel appears in documented writeset but not written to in function body.',
    'E007':'Channel is written to in function body but does not appear in documented writeset'
    }


csp_error_list = exstatic.warnings.ExstaticErrorList(errcodes)


def list_error_codes():
    """List all available error codes.
    """
    sep = '--------------------------------------------------------------------'
    print ( sep )
    print ( ' CODE  | MESSAGE' )
    codes = list(errcodes.keys())
    codes.sort()
    current_type = ''
    for key in codes:
        if key[0] != current_type:
            print ( sep )
        print ( str ( key ) + ': |' + str ( errcodes[key] ) )
        current_type = key[0]
    print ( sep )
    return


def create_error(filename, lineno, scope, errcode):
    """Create a new error and add it to the list.
    """
    return csp_error_list.create_error(filename, lineno, scope, errcode)


def reset_errors():
    """Empty the current error list of all errors.
    """
    csp_error_list.reset_errors()
    return


def get_errors(excluded=[]):
    """Return the list of current errors.

    @return list of current errors.
    @type list
    """
    return csp_error_list.get_errors(excluded=excluded)

def print_errors(excluded=[]):
    """Print the list of current errors.
    """
    csp_error_list.print_errors(excluded=excluded)
    return
