# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
import re
import os
import sys
import argparse
import fnmatch
import unittest

__unittest = True


def parse_pattern(pattern):
    return f"*{pattern}*" if "*" not in pattern else pattern


def parse_xfile(xfile):
    with open(xfile) as f:
        return list(map(parse_pattern, f.read().splitlines()))


def setup_parser(parser):
    parser.add_argument(
        "-x",  # "--exclude-name",
        help="Skip run tests which match the given substring",
        action="append", dest="excludePatterns", default=[],
        type=parse_pattern, metavar="TESTNAMEPATTERNS",
    )
    parser.add_argument(  # Py3.8: use action="extend" on "excludePatterns"
        "--xfile",
        help="Skip run tests which match the substrings in the given files",
        action="append", dest="excludeFile", default=[],
        type=str, metavar="FILENAME",
    )
    parser.add_argument(
        "-i",  # "--include",
        help="Include test module names matching REGEX",
        action="append", dest="include", default=[],
        type=str, metavar="REGEX",
    )
    parser.add_argument(
        "-e",  # "--exclude",
        help="Exclude test module names matching REGEX",
        action="append", dest="exclude", default=[],
        type=str, metavar="REGEX",
    )
    parser.add_argument(
        "--inplace",
        help="Enable testing from in-place build",
        action="store_true", dest="inplace", default=False,
    )
    parser.add_argument(
        "--no-builddir",
        help="Disable testing from build directory",
        action="store_false", dest="builddir", default=True,
    )
    parser.add_argument(
        "--path",
        help="Prepend PATH to sys.path",
        action="append", dest="path", default=[],
        type=str, metavar="PATH",
    )
    parser.add_argument(
        "--threads",
        help="Initialize MPI with thread support",
        action="store_true", dest="threads", default=None,
    )
    parser.add_argument(
        "--no-threads",
        help="Initialize MPI without thread support",
        action="store_false", dest="threads", default=None,
    )
    parser.add_argument(
        "--thread-level",
        help="Initialize MPI with required thread support",
        choices=["single", "funneled", "serialized", "multiple"],
        action="store", dest="thread_level", default=None,
        type=str, metavar="LEVEL",
    )
    parser.add_argument(
        "--cupy",
        help="Enable testing with CuPy arrays",
        action="store_true", dest="cupy", default=False,
    )
    parser.add_argument(
        "--no-cupy",
        help="Disable testing with CuPy arrays",
        action="store_false", dest="cupy", default=False,
    )
    parser.add_argument(
        "--numba",
        help="Enable testing with Numba arrays",
        action="store_true", dest="numba", default=False,
    )
    parser.add_argument(
        "--no-numba",
        help="Disable testing with Numba arrays",
        action="store_false", dest="numba", default=False,
    )
    parser.add_argument(
        "--no-numpy",
        help="Disable testing with NumPy arrays",
        action="store_false", dest="numpy", default=True,
    )
    parser.add_argument(
        "--no-array",
        help="Disable testing with builtin array module",
        action="store_false", dest="array", default=True,
    )
    parser.add_argument(
        "--no-skip-mpi",
        help="Disable known failures with backend MPI",
        action="store_false", dest="skip_mpi", default=True,
    )
    parser.add_argument(
        "--xml",
        help="Directory for storing XML reports",
        action="store", dest="xmloutdir", default=None,
        nargs="?", const=os.path.curdir,
    )
    return parser


def getbuilddir():
    try:
        try:
            from setuptools.dist import Distribution
        except ImportError:
            from distutils.dist import Distribution
        try:
            from setuptools.command.build import build
        except ImportError:
            from distutils.command.build import build
        cmd_obj = build(Distribution())
        cmd_obj.finalize_options()
        return cmd_obj.build_platlib
    except Exception:
        return None


def getprocessorinfo():
    from mpi4py import MPI
    rank = MPI.COMM_WORLD.Get_rank()
    name = MPI.Get_processor_name()
    return (rank, name)


def getlibraryinfo():
    from mpi4py import MPI
    x, y = MPI.Get_version()
    info = f"MPI {x}.{y}"
    name, version = MPI.get_vendor()
    if name != "unknown":
        x, y, z = version
        info += f" ({name} {x}.{y}.{z})"
    return info


def getpythoninfo():
    x, y, z = sys.version_info[:3]
    return f"Python {x}.{y}.{z} ({sys.executable})"


def getpackageinfo(pkg):
    try:
        pkg = __import__(pkg)
    except ImportError:
        return None
    name = pkg.__name__
    version = pkg.__version__
    path = pkg.__path__[0]
    return f"{name} {version} ({path})"


def setup_python(options):
    script = os.path.abspath(__file__)
    testdir = os.path.dirname(script)
    rootdir = os.path.dirname(testdir)
    if options.inplace:
        srcdir = os.path.join(rootdir, "src")
        sys.path.insert(0, srcdir)
    elif options.builddir:
        builddir = getbuilddir()
        if builddir is not None:
            builddir = os.path.join(rootdir, builddir)
            if os.path.isdir(builddir):
                sys.path.insert(0, builddir)
    if options.path:
        for path in reversed(options.path):
            for pth in path.split(os.path.pathsep):
                if os.path.exists(pth):
                    sys.path.insert(0, pth)


def setup_modules(options):
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
    import mpi4py
    if options.threads is not None:
        mpi4py.rc.threads = options.threads
    if options.thread_level is not None:
        mpi4py.rc.thread_level = options.thread_level
    #
    import mpi4py.MPI


def setup_unittest(options):
    from unittest.runner import _WritelnDecorator
    super_writeln = _WritelnDecorator.writeln
    def writeln(self, arg=None):
        try:
            self.flush()
        except:
            pass
        super_writeln(self, arg)
        try:
            self.flush()
        except:
            pass
    _WritelnDecorator.writeln = writeln


def print_banner(options):
    rank, name = getprocessorinfo()
    prefix = f"[{rank}@{name}]"

    def writeln(message="", endl="\n"):
        if message is None:
            return
        sys.stderr.flush()
        sys.stderr.write(f"{prefix} {message}{endl}")
        sys.stderr.flush()

    if options.verbosity:
        writeln(getpythoninfo())
        writeln(getpackageinfo('numpy'))
        writeln(getpackageinfo('numba'))
        writeln(getpackageinfo('cupy'))
        writeln(getlibraryinfo())
        writeln(getpackageinfo('mpi4py'))


class TestLoader(unittest.TestLoader):

    excludePatterns = None

    def __init__(self, include=None, exclude=None):
        super().__init__()
        if include:
            self.include = re.compile('|'.join(include)).search
        else:
            self.include = lambda arg: True
        if exclude:
            self.exclude = re.compile('|'.join(exclude)).search
        else:
            self.exclude = lambda arg: False

    def _match_path(self, path, full_path, pattern):
        match = super()._match_path(path, full_path, pattern)
        if match:
            if not self.include(path):
                return False
            if self.exclude(path):
                return False
        return match

    def getTestCaseNames(self, testCaseClass):
        def exclude(name):
            modname = testCaseClass.__module__
            clsname = testCaseClass.__qualname__
            fullname = f'{modname}.{clsname}.{name}'
            return not any(map(
                lambda pattern: fnmatch.fnmatchcase(fullname, pattern),
                self.excludePatterns
            ))
        names = super().getTestCaseNames(testCaseClass)
        if self.excludePatterns:
            names = list(filter(exclude, names))
        return names


class TestProgram(unittest.TestProgram):

    def _getMainArgParser(self, parent):
        parser = super()._getMainArgParser(parent)
        setup_parser(parser)
        return parser

    def _getDiscoveryArgParser(self, parent):
        parser = argparse.ArgumentParser(parents=[parent])
        setup_parser(parser)
        return parser

    if sys.version_info < (3, 7):
        def _do_discovery(self, argv, Loader=None):
            if argv is not None:
                if self._discovery_parser is None:
                    self._initArgParsers()
                self._discovery_parser.parse_args(argv, self)
            self.createTests(from_discovery=True, Loader=Loader)

    def createTests(self, from_discovery=False, Loader=None):
        setup_python(self)
        setup_modules(self)
        setup_unittest(self)
        testdir = os.path.dirname(__file__)
        if from_discovery:
            self.start = testdir
            self.pattern = "test_*.py"
        elif testdir not in sys.path:
            sys.path.insert(0, testdir)
        if not self.skip_mpi:
            import mpiunittest
            mpiunittest.skipMPI = lambda p, *c: lambda f: f
        for xfile in self.excludeFile:
            self.excludePatterns.extend(parse_xfile(xfile))
        self.testLoader = TestLoader(self.include, self.exclude)
        self.testLoader.excludePatterns = self.excludePatterns
        if sys.version_info < (3, 7):
            if from_discovery:
                loader = self.testLoader if Loader is None else Loader()
                self.test = loader.discover(self.start, self.pattern, None)
            else:
                super().createTests()
            return
        super().createTests(from_discovery, Loader)

    def _setUpXMLRunner(self):
        from mpi4py import MPI
        size = MPI.COMM_WORLD.Get_size()
        rank = MPI.COMM_WORLD.Get_rank()
        try:
            import xmlrunner
        except ModuleNotFoundError:
            if rank == 0:
                print(
                    "Cannot generate XML reports!",
                    "Install 'unittest-xml-reporting'.",
                    file=sys.stderr, flush=True,
                )
            sys.exit(1)
        runner = xmlrunner.XMLTestRunner(output=self.xmloutdir)
        runner.outsuffix += f"-{rank}" if size > 1 else ""
        self.testRunner = runner
        self.buffer = False
        self.catchbreak = False

    def runTests(self):
        print_banner(self)
        if self.xmloutdir:
            self._setUpXMLRunner()
        try:
            super().runTests()
        except SystemExit:
            pass
        success = self.result.wasSuccessful()
        if not success and self.failfast:
            from mpi4py import run
            run.set_abort_status(1)
        sys.exit(not success)


main = TestProgram


if __name__ == '__main__':
    sys.dont_write_bytecode = True
    main(module=None)
