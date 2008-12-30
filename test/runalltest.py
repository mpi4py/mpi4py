import sys, os
import unittest

try: # use the 'installed' mpi4py
    import mpi4py
except ImportError: # or the no yet installed mpi4py
    from distutils.util import get_platform
    plat_specifier = ".%s-%s" % (get_platform(), sys.version[0:3])
    os.path.split(__file__)[0]
    path = os.path.join(os.path.split(__file__)[0], os.path.pardir,
                        'build', 'lib' + plat_specifier)
    path = os.path.normpath(path)
    sys.path.insert(0, path)
    import mpi4py

from mpi4py import MPI
sys.stderr.flush()
sys.stderr.write("mpi4py imported from '%s'\n" % mpi4py.__path__[0])
sys.stderr.flush()

# make sure we are using the Cython-based version
assert os.path.splitext(MPI.__file__)[1] not in ('.py', '.pyc', '.pyo')

testpath = os.path.split(__file__)[0]
sys.path.insert(0, testpath)
import mpiunittest

alltests = mpiunittest.find_tests(
    exclude=[#'test_win',
             #'test_rma',
             ]
    )

def runtests(*args, **kargs):
    for test in alltests:
        sys.stderr.flush()
        sys.stderr.write("\nrunning %s\n" % test.__name__)
        sys.stderr.flush()
        mpiunittest.main(test, *args, **kargs)

def runtestsleak(repeats,*args, **kargs):
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
        sys.stderr.write('\nREF LEAKS -- before: %d, after: %d, diff: [%d]\n' % (r1, r2, r2-r1))
        sys.stderr.flush()

if __name__ == '__main__':
    runtests()
    if hasattr(sys, 'gettotalrefcount'):
        def dummy_write(self,*args): pass
        unittest._WritelnDecorator.write   = dummy_write
        unittest._WritelnDecorator.writeln = dummy_write
        runtestsleak(5)
