# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
import argparse
import fnmatch
import importlib
import os
import pathlib
import re
import sys
import unittest

__unittest = True


def parse_pattern(pattern):
    return f"*{pattern}*" if "*" not in pattern else pattern


def parse_xfile(xfile):
    content = pathlib.Path(xfile).read_text(encoding="utf-8")
    return list(map(parse_pattern, content.splitlines()))


def setup_parser(parser):
    parser.add_argument(
        "-x",  # "--exclude-name",
        help="Skip run tests which match the given substring",
        action="append",
        dest="excludePatterns",
        default=[],
        type=parse_pattern,
        metavar="TESTNAMEPATTERNS",
    )
    parser.add_argument(  # Py3.8: use action="extend" on "excludePatterns"
        "--xfile",
        help="Skip run tests which match the substrings in the given files",
        action="append",
        dest="excludeFile",
        default=[],
        type=str,
        metavar="FILENAME",
    )
    parser.add_argument(
        "-i",  # "--include",
        help="Include test module names matching REGEX",
        action="append",
        dest="include",
        default=[],
        type=str,
        metavar="REGEX",
    )
    parser.add_argument(
        "-e",  # "--exclude",
        help="Exclude test module names matching REGEX",
        action="append",
        dest="exclude",
        default=[],
        type=str,
        metavar="REGEX",
    )
    parser.add_argument(
        "--inplace",
        help="Enable testing from in-place build",
        action="store_true",
        dest="inplace",
        default=False,
    )
    parser.add_argument(
        "--no-builddir",
        help="Disable testing from build directory",
        action="store_false",
        dest="builddir",
        default=True,
    )
    parser.add_argument(
        "--path",
        help="Prepend PATH to sys.path",
        action="append",
        dest="path",
        default=[],
        type=str,
        metavar="PATH",
    )
    parser.add_argument(
        "--threads",
        help="Initialize MPI with thread support",
        action="store_true",
        dest="threads",
        default=None,
    )
    parser.add_argument(
        "--no-threads",
        help="Initialize MPI without thread support",
        action="store_false",
        dest="threads",
        default=None,
    )
    parser.add_argument(
        "--thread-level",
        help="Initialize MPI with required thread support",
        choices=["single", "funneled", "serialized", "multiple"],
        action="store",
        dest="thread_level",
        default=None,
        type=str,
        metavar="LEVEL",
    )
    parser.add_argument(
        "--cupy",
        help="Enable testing with CuPy arrays",
        action="store_true",
        dest="cupy",
        default=False,
    )
    parser.add_argument(
        "--no-cupy",
        help="Disable testing with CuPy arrays",
        action="store_false",
        dest="cupy",
        default=False,
    )
    parser.add_argument(
        "--numba",
        help="Enable testing with Numba arrays",
        action="store_true",
        dest="numba",
        default=False,
    )
    parser.add_argument(
        "--no-numba",
        help="Disable testing with Numba arrays",
        action="store_false",
        dest="numba",
        default=False,
    )
    parser.add_argument(
        "--no-numpy",
        help="Disable testing with NumPy arrays",
        action="store_false",
        dest="numpy",
        default=True,
    )
    parser.add_argument(
        "--no-array",
        help="Disable testing with builtin array module",
        action="store_false",
        dest="array",
        default=True,
    )
    parser.add_argument(
        "--no-skip-mpi",
        help="Disable known failures with backend MPI",
        action="store_false",
        dest="skip_mpi",
        default=True,
    )
    parser.add_argument(
        "--xml",
        help="Directory for storing XML reports",
        action="store",
        dest="xmloutdir",
        default=None,
        nargs="?",
        const=os.path.curdir,
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
        builddir = pathlib.Path(cmd_obj.build_platlib)
    except Exception:
        builddir = None
    return builddir


def getprocessorinfo():
    MPI = importlib.import_module("mpi4py.MPI")
    rank = MPI.COMM_WORLD.Get_rank()
    name = MPI.Get_processor_name()
    return (rank, name)


def getlibraryinfo():
    MPI = importlib.import_module("mpi4py.MPI")
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
    script = pathlib.Path(__file__).resolve()
    testdir = script.parent
    rootdir = testdir.parent
    if options.inplace:
        srcdir = str(rootdir / "src")
        sys.path.insert(0, srcdir)
    elif options.builddir:
        builddir = getbuilddir()
        if builddir is not None:
            builddir = rootdir / builddir
            if builddir.is_dir():
                sys.path.insert(0, str(builddir))
    if options.path:
        for path in reversed(options.path):
            for pth in map(pathlib.Path, path.split(os.path.pathsep)):
                if pth.exists():
                    sys.path.insert(0, str(pth))


def setup_modules(options):
    #
    if not options.cupy:
        sys.modules["cupy"] = None
    if not options.numba:
        sys.modules["numba"] = None
    if not options.numpy:
        sys.modules["numpy"] = None
    if not options.array:
        sys.modules["array"] = None
    #
    mpi4py = importlib.import_module("mpi4py")
    if options.threads is not None:
        mpi4py.rc.threads = options.threads
    if options.thread_level is not None:
        mpi4py.rc.thread_level = options.thread_level
    importlib.import_module("mpi4py.MPI")


def setup_unittest(_options):
    from contextlib import suppress
    from unittest.runner import _WritelnDecorator

    super_writeln = _WritelnDecorator.writeln

    def writeln(self, arg=None):
        with suppress(Exception):
            self.flush()
        super_writeln(self, arg)
        with suppress(Exception):
            self.flush()

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
        writeln(getpackageinfo("numpy"))
        writeln(getpackageinfo("numba"))
        writeln(getpackageinfo("cupy"))
        writeln(getlibraryinfo())
        writeln(getpackageinfo("mpi4py"))


class TestLoader(unittest.TestLoader):
    #
    excludePatterns = None

    def __init__(self, include=None, exclude=None):
        super().__init__()
        if include:
            self.include = re.compile("|".join(include)).search
        else:
            self.include = lambda _arg: True
        if exclude:
            self.exclude = re.compile("|".join(exclude)).search
        else:
            self.exclude = lambda _arg: False

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
            fullname = f"{modname}.{clsname}.{name}"
            return not any(
                fnmatch.fnmatchcase(fullname, pattern)
                for pattern in self.excludePatterns
            )

        names = super().getTestCaseNames(testCaseClass)
        if self.excludePatterns:
            names = list(filter(exclude, names))
        return names


class TestProgram(unittest.TestProgram):
    #
    def _getMainArgParser(self, parent):
        parser = super()._getMainArgParser(parent)
        setup_parser(parser)
        return parser

    def _getDiscoveryArgParser(self, parent):
        parser = argparse.ArgumentParser(parents=[parent])
        setup_parser(parser)
        return parser

    def createTests(self, from_discovery=False, Loader=None):
        setup_python(self)
        setup_modules(self)
        setup_unittest(self)
        testdir = pathlib.Path(__file__).parent
        if from_discovery:
            self.start = str(testdir)
            self.pattern = "test_*.py"
        elif testdir not in sys.path:
            sys.path.insert(0, testdir)
        if not self.skip_mpi:
            mpiunittest = __import__("mpiunittest")
            mpiunittest.skipMPI = lambda _p, *_c: lambda f: f
        for xfile in self.excludeFile:
            self.excludePatterns.extend(parse_xfile(xfile))
        self.testLoader = TestLoader(self.include, self.exclude)
        self.testLoader.excludePatterns = self.excludePatterns
        super().createTests(from_discovery, Loader)

    def _setUpXMLRunner(self):
        MPI = importlib.import_module("mpi4py.MPI")
        size = MPI.COMM_WORLD.Get_size()
        rank = MPI.COMM_WORLD.Get_rank()
        try:
            import xmlrunner
        except ModuleNotFoundError:
            if rank == 0:
                print(
                    "Cannot generate XML reports!",
                    "Install 'unittest-xml-reporting'.",
                    file=sys.stderr,
                    flush=True,
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
            run = importlib.import_module("mpi4py.run")
            run.set_abort_status(1)
        sys.exit(not success)


main = TestProgram


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    main(module=None)
