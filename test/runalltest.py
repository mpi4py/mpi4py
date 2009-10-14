EXCLUDE = [
    #'test_exceptions',
    #'test_spawn',
    ]

import sys, os
import unittest

for arg in sys.argv[1:]:
    if arg.startswith('--path='):
        sys.argv.remove(arg)
        path = arg.replace('--path=', '').split(os.path.pathsep)
        path.reverse()
        for p in path:
            sys.path.insert(0, p)

try: # use the 'installed' mpi4py
    import mpi4py
except ImportError: # or the no yet installed mpi4py
    from distutils.util import get_platform
    plat_specifier = ".%s-%s" % (get_platform(), sys.version[0:3])
    os.path.split(__file__)[0]
    path = os.path.join(os.path.split(__file__)[0], os.path.pardir,
                        'build', 'lib' + plat_specifier)
    if not os.path.exists(path) and os.path.exists(path+'-pydebug'):
        path += '-pydebug'
    path = os.path.normpath(path)
    sys.path.insert(0, path)
    import mpi4py

from mpi4py import rc
#rc.threaded = False
from mpi4py import MPI
sys.stderr.flush()
sys.stderr.write("[%d of %d on %s] Py%d%d - mpi4py from '%s'\n" \
                 % (MPI.COMM_WORLD.Get_rank(),
                    MPI.COMM_WORLD.Get_size(),
                    MPI.Get_processor_name(),
                    sys.version_info[0],
                    sys.version_info[1],
                    mpi4py.__path__[0]))
sys.stderr.flush()

# make sure we are using the Cython-based version
assert os.path.splitext(MPI.__file__)[1] not in ('.py', '.pyc', '.pyo')

testpath = os.path.split(__file__)[0]
sys.path.insert(0, testpath)
import mpiunittest

alltests = mpiunittest.find_tests(exclude=EXCLUDE[:])

def runtests(*args, **kargs):
    quiet = '-q' in args or '-q' in sys.argv
    if quiet:
        try:
            from unittest.runner import _WritelnDecorator
        except ImportError:
            from unittest import _WritelnDecorator
        def dummy_write(self, *args): pass
        _WritelnDecorator.write   = dummy_write
        _WritelnDecorator.writeln = dummy_write
    for test in alltests:
        if not quiet:
            sys.stderr.flush()
            sys.stderr.write("\nRunning %s\n" % test.__name__)
            sys.stderr.flush()
        mpiunittest.main(test, *args, **kargs)

def runtestsleak(repeats, *args, **kargs):
    import gc
    test = r1 = r2 = None
    while repeats:
        repeats -= 1
        gc.collect()
        r1 = sys.gettotalrefcount()
        for test in alltests:
            mpiunittest.main(test, *args, **kargs)
        gc.collect()
        r2 = sys.gettotalrefcount()
        sys.stderr.flush()
        sys.stderr.write('REF LEAKS -- before: %d, after: %d, diff: [%d]\n' % (r1, r2, r2-r1))
        sys.stderr.flush()

if __name__ == '__main__':
    runtests()
    if hasattr(sys, 'gettotalrefcount'):
        try:
            from unittest.runner import _WritelnDecorator
        except ImportError:
            from unittest import _WritelnDecorator
        def dummy_write(self, *args): pass
        _WritelnDecorator.write   = dummy_write
        _WritelnDecorator.writeln = dummy_write
        runtestsleak(5)
