import sys, os
import unittest

try: # use the 'installed' mpi4py
    from mpi4py import MPI
except ImportError: # or the one no yet installed mpi4py
    from distutils.util import get_platform
    plat_specifier = ".%s-%s" % (get_platform(), sys.version[0:3])
    os.path.split(__file__)[0]
    path = os.path.join(os.path.split(__file__)[0], os.path.pardir,
                        'build', 'lib' + plat_specifier)
    path = os.path.normpath(path)
    sys.path.insert(0, path)
    from mpi4py import MPI
    sys.stderr.write("mpi4py imported from '%s'\n" % path)
    sys.stderr.flush()

# make sure we are using the Cython-based version
assert os.path.splitext(MPI.__file__)[1] not in ('.py', '.pyc', '.pyo')

testpath = os.path.split(__file__)[0]
sys.path.insert(0, testpath)
import mpiunittest

for tests in mpiunittest.find_tests(exclude=['test_doc',
                                             ]):
    mpiunittest.main(tests)
