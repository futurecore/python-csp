#!/usr/bin/env python

"""Setup python-csp for packaging or installation.

Much here is borrowed from the Python wiki or wxPython.
See U{http://wiki.python.org/moin/DistUtilsTutorial}

FIXME: Remove hard-coded paths. Make portable.
"""

__author__ = 'Sarah Mount <s.mount@wlv.ac.uk>'
__credits__ = 'Donn Ingle, Robin Dunn'

import distutils, distutils.command, distutils.command.install_data
import distutils.sysconfig
from distutils.core import setup
import os
import glob
import fnmatch

def opj(*args):
    path = os.path.join(*args)
    return os.path.normpath(path)

class wx_smart_install_data(distutils.command.install_data.install_data):
    """Need to change self.install_dir to the actual library dir"""
    def run(self):
        install_cmd = self.get_finalized_command('install')
        self.install_dir = getattr(install_cmd, 'install_lib')
        return distutils.command.install_data.install_data.run(self)

def find_data_files(srcdir, *wildcards, **kw):
    """Get a list of all files under the srcdir matching wildcards,
    returned in a format to be used for install_data
    """
    def walk_helper(arg, dirname, files):
        if '.svn' in dirname:
            return
        names = []
        lst, wildcards = arg
        for wc in wildcards:
            wc_name = opj(dirname, wc)
            for f in files:
                filename = opj(dirname, f)

                if (fnmatch.fnmatch(filename, wc_name) and
		    not os.path.isdir(filename)):
                    names.append(filename)
        if names:
            lst.append( (dirname, names ) )

    file_list = []
    recursive = kw.get('recursive', True)
    if recursive:
        os.path.walk(srcdir, walk_helper, (file_list, wildcards))
    else:
        walk_helper((file_list, wildcards),
                    srcdir,
                    [os.path.basename(f) for f in glob.glob(opj(srcdir, '*'))])
    return file_list

        
files = find_data_files('csp/', '*.*')
def makeabs(path):
    return os.path.join(distutils.sysconfig.PREFIX, path)

dist = setup(name = "csp",
      version = "0.2",
      description = "python-csp adds communicating sequential processes to Python",
      author = 'Sarah Mount',
      author_email = "s.mount@wlv.ac.uk",
      url = "http://code.google.com/p/python-csp/",
      long_description = """python-csp adds communicating sequential processes to Python""",

      packages = ['csp'],
      data_files = (files +
		    [(makeabs('share/applications/'),
			       ['applications/python-csp.desktop'])] +
            [('/usr/local/lib/jython2.5/Lib/',
                    ['jythonsetup/Jycspthread.py'])]),

      ## Borrowed from wxPython:
      ## Causes the data_files to be installed into the modules directory.
      ## Override some of the default distutils command classes with my own.
#      cmdclass = { 'install_data': wx_smart_install_data},

      scripts = ['scripts/python-csp'],
) 

# Update the .desktop file database
try:
    call(["update-desktop-database"])
except:
    pass

# # Fix permissions on image files
# try:
#     impath = os.path.join(distutils.sysconfig.get_python_lib(),
# 			  'Dingo/images/')
#     for imfile in glob.glob(impath+'*'):
# 	    print 'changing mode of %s to 755' % imfile
# 	    os.chmod(imfile, 0755)
# 	    pixmap = '/usr/share/pixmaps/dingo.xpm' # Oh dear.
# 	    print 'changing mode of %s to 755' % pixmap
# 	    os.chmod(pixmap, 0755)
# except:
#     print 'ERROR: could not chown images to 755'
