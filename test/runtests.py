import sys, os
import optparse
import unittest

def getoptionparser():
    parser = optparse.OptionParser()

    parser.add_option("-q", "--quiet",
                      action="store_const", const=0, dest="verbose", default=1,
                      help="minimal output")
    parser.add_option("-v", "--verbose",
                      action="store_const", const=2, dest="verbose", default=1,
                      help="verbose output")
    parser.add_option("-i", "--include", type="string",
                      action="append",  dest="include", default=[],
                      help="include tests matching PATTERN", metavar="PATTERN")
    parser.add_option("-e", "--exclude", type="string",
                      action="append", dest="exclude", default=[],
                      help="exclude tests matching PATTERN", metavar="PATTERN")
    parser.add_option("-f", "--failfast",
                      action="store_true", dest="failfast", default=False,
                      help="stop on first failure")
    parser.add_option("-c", "--catch",
                      action="store_true", dest="catchbreak", default=False,
                      help="catch Control-C and display results")
    parser.add_option("--no-builddir",
                      action="store_false", dest="builddir", default=True,
                      help="disable testing from build directory")
    parser.add_option("--path", type="string",
                      action="append", dest="path", default=[],
                      help="prepend PATH to sys.path", metavar="PATH")
    parser.add_option("--refleaks", type="int",
                      action="store", dest="repeats", default=3,
                      help="run tests REPEAT times in a loop to catch leaks",
                      metavar="REPEAT")
    parser.add_option("--threads",
                      action="store_true", dest="threads", default=None,
                      help="initialize MPI with thread support")
    parser.add_option("--no-threads",
                      action="store_false", dest="threads", default=None,
                      help="initialize MPI without thread support")
    parser.add_option("--thread-level", type="choice",
                      choices=["single", "funneled", "serialized", "multiple"],
                      action="store", dest="thread_level", default=None,
                      help="initialize MPI with required thread support")
    parser.add_option("--mpe",
                      action="store_true", dest="mpe", default=False,
                      help="use MPE for MPI profiling")
    parser.add_option("--vt",
                      action="store_true", dest="vt", default=False,
                      help="use VampirTrace for MPI profiling")
    parser.add_option("--cupy",
                      action="store_true", dest="cupy", default=False,
                      help="enable testing with CuPy arrays")
    parser.add_option("--no-cupy",
                      action="store_false", dest="cupy", default=False,
                      help="disable testing with CuPy arrays")
    parser.add_option("--numba",
                      action="store_true", dest="numba", default=False,
                      help="enable testing with Numba arrays")
    parser.add_option("--no-numba",
                      action="store_false", dest="numba", default=False,
                      help="disable testing with Numba arrays")
    parser.add_option("--no-numpy",
                      action="store_false", dest="numpy", default=True,
                      help="disable testing with NumPy arrays")
    parser.add_option("--no-array",
                      action="store_false", dest="array", default=True,
                      help="disable testing with builtin array module")
    parser.add_option("--no-skip-mpi",
                      action="store_false", dest="skip_mpi", default=True,
                      help="disable known failures with backend MPI")
    return parser

def getbuilddir():
    from distutils.util import get_platform
    s = os.path.join("build", "lib.%s-%.3s" % (get_platform(), sys.version))
    if hasattr(sys, 'gettotalrefcount'): s += '-pydebug'
    return s

def setup_python(options):
    rootdir = os.path.dirname(os.path.dirname(__file__))
    builddir = os.path.join(rootdir, getbuilddir())
    if options.builddir and os.path.exists(builddir):
        sys.path.insert(0, builddir)
    if options.path:
        path = options.path[:]
        path.reverse()
        for p in path:
            sys.path.insert(0, p)

def setup_unittest(options):
    from unittest import TestSuite
    try:
        from unittest.runner import _WritelnDecorator
    except ImportError:
        from unittest import _WritelnDecorator
    #
    writeln_orig = _WritelnDecorator.writeln
    def writeln(self, message=''):
        try: self.stream.flush()
        except: pass
        writeln_orig(self, message)
        try: self.stream.flush()
        except: pass
    _WritelnDecorator.writeln = writeln

def import_package(options, pkgname):
    #
    if not options.cupy:
        sys.modules['cupy'] = None
    if not options.numba:
        sys.modules['numba'] = None
    if not options.numpy:
        sys.modules['numpy'] = None
    if not options.array:
        sys.modules['array'] = None
    #
    package = __import__(pkgname)
    #
    import mpi4py.rc
    if options.threads is not None:
        mpi4py.rc.threads = options.threads
    if options.thread_level is not None:
        mpi4py.rc.thread_level = options.thread_level
    if options.mpe:
        mpi4py.profile('mpe', logfile='runtests-mpi4py')
    if options.vt:
        mpi4py.profile('vt', logfile='runtests-mpi4py')
    import mpi4py.MPI
    #
    return package

def getprocessorinfo():
    from mpi4py import MPI
    rank = MPI.COMM_WORLD.Get_rank()
    name = MPI.Get_processor_name()
    return (rank, name)

def getlibraryinfo():
    from mpi4py import MPI
    info = "MPI %d.%d" % MPI.Get_version()
    name, version = MPI.get_vendor()
    if name != "unknown":
        info += (" (%s %s)" % (name, '%d.%d.%d' % version))
    return info

def getpythoninfo():
    x, y = sys.version_info[:2]
    return ("Python %d.%d (%s)" % (x, y, sys.executable))

def getpackageinfo(pkg):
    return ("%s %s (%s)" % (pkg.__name__,
                            pkg.__version__,
                            pkg.__path__[0]))

def writeln(message='', endl='\n'):
    sys.stderr.flush()
    sys.stderr.write(message+endl)
    sys.stderr.flush()

def print_banner(options, package):
    r, n = getprocessorinfo()
    fmt = "[%d@%s] %s"
    if options.verbose:
        writeln(fmt % (r, n, getpythoninfo()))
        writeln(fmt % (r, n, getlibraryinfo()))
        writeln(fmt % (r, n, getpackageinfo(package)))

def load_tests(options, args):
    # Find tests
    import re, glob
    testsuitedir = os.path.dirname(__file__)
    sys.path.insert(0, testsuitedir)
    pattern = 'test_*.py'
    wildcard = os.path.join(testsuitedir, pattern)
    testfiles = glob.glob(wildcard)
    include = exclude = None
    if options.include:
        include = re.compile('|'.join(options.include)).search
    if options.exclude:
        exclude = re.compile('|'.join(options.exclude)).search
    testnames = []
    for testfile in testfiles:
        filename = os.path.basename(testfile)
        testname = os.path.splitext(filename)[0]
        if ((exclude and exclude(testname)) or
            (include and not include(testname))):
            continue
        testnames.append(testname)
    testnames.sort()
    # Handle options
    if not options.cupy:
        sys.modules['cupy'] = None
    if not options.numba:
        sys.modules['numba'] = None
    if not options.numpy:
        sys.modules['numpy'] = None
    if not options.array:
        sys.modules['array'] = None
    if not options.skip_mpi:
        import mpiunittest
        mpiunittest.skipMPI = lambda p, *c: lambda f: f
    # Load tests and populate suite
    testloader = unittest.TestLoader()
    testsuite = unittest.TestSuite()
    for testname in testnames:
        module = __import__(testname)
        for arg in args:
            try:
                cases = testloader.loadTestsFromNames((arg,), module)
            except AttributeError:
                continue
            testsuite.addTests(cases)
        if not args:
            cases = testloader.loadTestsFromModule(module)
            testsuite.addTests(cases)
    return testsuite

def run_tests(options, testsuite, runner=None):
    if runner is None:
        runner = unittest.TextTestRunner()
        runner.verbosity = options.verbose
        runner.failfast = options.failfast
    if options.catchbreak:
        unittest.installHandler()
    result = runner.run(testsuite)
    return result.wasSuccessful()

def test_refleaks(options, args):
    from sys import gettotalrefcount
    from gc import collect
    testsuite = load_tests(options, args)
    testsuite._cleanup =  False
    for case in testsuite:
        case._cleanup = False
    class EmptyIO(object):
        def write(self, *args):
            pass
    runner = unittest.TextTestRunner(stream=EmptyIO(), verbosity=0)
    rank, name = getprocessorinfo()
    r1 = r2 = 0
    repeats = options.repeats
    while repeats:
        collect()
        r1 = gettotalrefcount()
        run_tests(options, testsuite, runner)
        collect()
        r2 = gettotalrefcount()
        leaks = r2-r1
        if leaks and repeats < options.repeats:
            writeln('[%d@%s] refleaks:  (%d - %d) --> %d'
                    % (rank, name, r2, r1, leaks))
        repeats -= 1

def abort(code=1):
    from mpi4py import MPI
    MPI.COMM_WORLD.Abort(code)

def shutdown(success):
    from mpi4py import MPI

def main(args=None):
    pkgname = 'mpi4py'
    parser = getoptionparser()
    (options, args) = parser.parse_args(args)
    setup_python(options)
    setup_unittest(options)
    package = import_package(options, pkgname)
    print_banner(options, package)
    testsuite = load_tests(options, args)
    success = run_tests(options, testsuite)
    if not success and options.failfast: abort()
    if success and hasattr(sys, 'gettotalrefcount'):
        test_refleaks(options, args)
    shutdown(success)
    return not success

if __name__ == '__main__':
    import sys
    sys.dont_write_bytecode = True
    sys.exit(main())
