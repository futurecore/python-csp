#!/usr/bin/env python
"""
This is mainly only a test finder, but adds the feature of running
tests that start with "csptest_" twice for the os_thread and os_process
backend.
"""

import sys
import os
import unittest
import re

os.chdir(os.path.dirname(__file__))
sys.path.insert(0, '..')
test_suite_re = re.compile('((csp)?test_(.*))\.py$')

BACKENDS = []
try:
    import csp.os_thread
    BACKENDS.append(sys.modules['csp.os_thread'])
except: pass
try:
    import csp.os_process
    BACKENDS.append(sys.modules['csp.os_process'])
except: pass
import csp.csp

if len(BACKENDS) < 2:
    from warnings import warn
    warn('This platform supports only backend {0}, '
         'the other one is thus UNTESTED!'.format(csp.csp.CSP_IMPLEMENTATION))


runner = unittest.TextTestRunner(verbosity=2)
def load_and_run(test_module):
    sys.stdout.flush()
    suite = unittest.defaultTestLoader.loadTestsFromName(test_module)
    return runner.run(suite).wasSuccessful()

for testcase in [os.path.basename(x) for x in sys.argv[1:]] or os.listdir('.'):
    assert os.path.exists(testcase)
    testname = test_suite_re.match(os.path.basename(testcase))
    if testname is None:
        continue
    test_module, csptest, titlename = testname.groups()
    title = 'Testing ' + titlename
    remove_from_cache_mods = [x for x in sys.modules if x == test_module or \
                                               (x.startswith('csp.') and \
                                                not x.startswith('csp.os_'))]
    for module in remove_from_cache_mods:
        del sys.modules[module]
    if csptest:
        for backend in BACKENDS:
            sys.modules['csp.csp'] = backend
            sys.stdout.write('{0} ({1}): '.format(title,
                                                  backend.CSP_IMPLEMENTATION))
            if not load_and_run(test_module):
                sys.exit(2)
    else:
        sys.stdout.write(title + ': ')
        if not load_and_run(test_module):
            sys.exit(2)
    print
