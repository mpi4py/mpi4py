import importlib
import io
import os
import pathlib
import sys
import unittest
import warnings

import mpi4py

pkgdir = pathlib.Path(mpi4py.__file__).resolve().parent


class TestImport(unittest.TestCase):
    #
    #
    def testImportMPI(self):
        importlib.import_module("mpi4py.MPI")

    def testImportBench(self):
        importlib.import_module("mpi4py.bench")

    def testImportFutures(self):
        importlib.import_module("mpi4py.futures")
        importlib.import_module("mpi4py.futures.server")
        importlib.import_module("mpi4py.futures.__main__")

    def testImportRun(self):
        importlib.import_module("mpi4py.run")
        importlib.import_module("mpi4py.__main__")

    def testImportTyping(self):
        importlib.import_module("mpi4py.typing")

    def testImportUtil(self):
        importlib.import_module("mpi4py.util")
        importlib.import_module("mpi4py.util.dtlib")
        importlib.import_module("mpi4py.util.pkl5")
        importlib.import_module("mpi4py.util.pool")
        importlib.import_module("mpi4py.util.sync")

    def testImportMPIABI(self):
        importlib.import_module("mpi4py._mpiabi")


class TestDataFiles(unittest.TestCase):
    #
    #
    def testTyping(self):
        import importlib.machinery

        py_typed = pkgdir / "py.typed"
        self.assertTrue(py_typed.exists())
        suffixes = [
            *importlib.machinery.SOURCE_SUFFIXES,
            *importlib.machinery.EXTENSION_SUFFIXES,
        ]
        for root, _, files in os.walk(pkgdir):
            root = pathlib.Path(root)
            for fname in files:
                name, _, extra = fname.partition(".")
                suffix = f".{extra}"
                for entry in suffixes:
                    if suffix.endswith(entry):
                        pyi = root / f"{name}.pyi"
                        self.assertTrue(pyi.exists())
                        break

    def testCython(self):
        for pxd in [
            pkgdir / "__init__.pxd",
            pkgdir / "libmpi.pxd",
            pkgdir / "MPI.pxd",
        ]:
            self.assertTrue(pxd.exists())

    def testHeaders(self):
        for hdr in [
            pkgdir / "MPI.h",
            pkgdir / "MPI_api.h",
            pkgdir / "include" / "mpi4py" / "pycapi.h",
            pkgdir / "include" / "mpi4py" / "mpi4py.h",
            pkgdir / "include" / "mpi4py" / "mpi4py.i",
        ]:
            self.assertTrue(hdr.exists())


class TestMPIABI(unittest.TestCase):
    #
    #
    def setUp(self):
        module = importlib.import_module("mpi4py.MPI")
        self.mpiabi = importlib.import_module("mpi4py._mpiabi")
        self.sentinel = getattr(self.mpiabi._get_mpiabi, "mpiabi", None)
        self.savedstate = (self.mpiabi.MPIABI, self.mpiabi.LIBMPI)
        if os.name == "posix":
            self.libmpi = module.__file__
        else:
            vendor = module.get_vendor()[0]
            if vendor == "Intel MPI":
                self.libmpi = "impi.dll"
            elif vendor == "Microsoft MPI":
                self.libmpi = "msmpi.dll"

    def tearDown(self):
        self.mpiabi._registry.pop("mpi4py.xyz", None)
        if self.sentinel is not None:
            self.mpiabi._get_mpiabi.mpiabi = self.sentinel
        elif hasattr(self.mpiabi._get_mpiabi, "mpiabi"):
            del self.mpiabi._get_mpiabi.mpiabi
        self.mpiabi.MPIABI, self.mpiabi.LIBMPI = self.savedstate
        del self.mpiabi

    def testGetFromString(self):
        mpiabi = self.mpiabi
        libmpi = self.libmpi
        string = mpiabi._get_mpiabi_from_libmpi(libmpi)
        try:
            libmpi = mpiabi._get_libmpi_from_mpiabi(string)
            string = mpiabi._get_mpiabi_from_libmpi(libmpi)
        except RuntimeError:
            return
        mpiabi._get_mpiabi.mpiabi = None
        mpiabi.MPIABI = string
        result = mpiabi._get_mpiabi()
        self.assertEqual(result, string)

    def testGetFromLibMPI(self):
        mpiabi = self.mpiabi
        libmpi = self.libmpi
        mpiabi._get_mpiabi.mpiabi = None
        mpiabi.LIBMPI = libmpi
        result = mpiabi._get_mpiabi()
        expected = {"mpiabi", "mpich", "openmpi", "impi", "msmpi"}
        self.assertIn(result, expected)

    def testString(self):
        mpiabi = self.mpiabi
        posix = os.name == "posix"
        for string, expected in (
            ("mpiabi", "mpiabi"),
            ("MPICH", "mpich" if posix else "impi"),
            ("I_MPI", "mpich" if posix else "impi"),
            ("Open MPI", "openmpi"),
            ("OPEN-MPI", "openmpi"),
            ("", ""),
        ):
            result = mpiabi._get_mpiabi_from_string(string)
            self.assertEqual(result, expected)

    def testLibMPI(self):
        mpiabi = self.mpiabi
        libmpi = self.libmpi
        result = mpiabi._get_mpiabi_from_libmpi(libmpi)
        expected = {"mpiabi", "mpich", "openmpi", "impi", "msmpi"}
        self.assertIn(result, expected)

    def testSuffix(self):
        mpiabi = self.mpiabi
        for abiname in ("mpiabi1", "mpiabi2", ""):
            mpiabi._get_mpiabi.mpiabi = abiname
            result = mpiabi._get_mpiabi_suffix("mpi4py.xyz")
            self.assertIsNone(result)
            mpiabi._register("mpi4py.xyz", abiname)
            mpiabi._register("mpi4py.xyz", abiname)
            result = mpiabi._get_mpiabi_suffix("mpi4py.xyz")
            self.assertEqual(result, f".{abiname}" if abiname else "")

    def testFinder(self):
        mpiabi = self.mpiabi
        finder = mpiabi._Finder
        registry = mpiabi._registry
        if finder not in sys.meta_path:
            mpiabi._install_finder()
            mpiabi._install_finder()
            self.assertIs(finder, sys.meta_path.pop())
        if "mpi4py.MPI" not in registry:
            mpiabi._get_mpiabi.mpiabi = ""
            mpiabi._register("mpi4py.MPI", "")
        spec = finder.find_spec("mpi4py.MPI", mpi4py.__path__)
        if mpiabi._get_mpiabi.mpiabi == "":
            del mpiabi._get_mpiabi.mpiabi
            del registry["mpi4py.MPI"]
        self.assertIsNotNone(spec)
        #
        spec = finder.find_spec("mpi4py.xyz", mpi4py.__path__)
        self.assertIsNone(spec)
        mpiabi._get_mpiabi.mpiabi = ""
        mpiabi._register("mpi4py.xyz", "")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            spec = finder.find_spec("mpi4py.xyz", mpi4py.__path__)
            self.assertIsNone(spec)
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            with self.assertRaises(RuntimeWarning):
                finder.find_spec("mpi4py.xyz", mpi4py.__path__)

    def testVerboseInfo(self):
        mpiabi = self.mpiabi
        message = "@message@"
        output = f"# [{mpiabi.__name__}] {message}\n"
        sys.stderr = stderr = io.StringIO()
        try:
            mpiabi._verbose_info(message, verbosity=-1)
        finally:
            sys.stderr = sys.__stderr__
        self.assertEqual(stderr.getvalue(), output)

    def testDLOpen(self):
        mpiabi = self.mpiabi
        os_name_save = os.name
        os_environ_save = os.environ
        sys_platform_save = sys.platform
        rtldmodes = ("RTLD_LAZY", "RTLD_LOCAL", "RTLD_GLOBAL")
        try:
            if os.name == "nt":
                for attr in rtldmodes:
                    setattr(os, attr, 0)
            for os_name, sys_platform in (
                ("posix", "linux"),
                ("posix", "freebsd"),
                ("posix", "darwin"),
                ("nt", "win32"),
            ):
                os.name = os_name
                sys.platform = sys_platform
                rpath = "@rpath" if sys.platform == "darwin" else ""
                path = mpiabi._dlopen_path()
                self.assertIsInstance(path, list)
                path = mpiabi._dlopen_path([])
                self.assertEqual(path, [rpath])
                path = mpiabi._dlopen_path("")
                self.assertEqual(path, [rpath])
                self.assertIn(rpath, path)
                pathseq = ("a", "b", "a", "b")
                pathstr = os.pathsep.join(pathseq)
                path = mpiabi._dlopen_path(pathseq)
                self.assertEqual(path, ["a", "b"])
                path = mpiabi._dlopen_path(pathstr)
                self.assertEqual(path, ["a", "b"])
                mode = mpiabi._dlopen_mode()
                modetype = int if os.name == "posix" else type(None)
                self.assertIsInstance(mode, modetype)
                mode = mpiabi._dlopen_mode(42)
                self.assertEqual(mode, 42)
                mpiabi._dlopen_filename("foo")
                mpiabi._dlopen_filename("foo", 0)
            os.name = "nt"
            sys.platform = "win32"
            os.environ = env = {}
            prefix = "/c/opt/impi"
            bindir = os.path.join(prefix, "bin")  # noqa: PTH118
            env["I_MPI_ROOT"] = prefix
            path = mpiabi._dlopen_path()
            self.assertIn(bindir, path)
            env.clear()
            prefix = "/c/opt/msmpi"
            bindir = os.path.join(prefix, "bin")  # noqa: PTH118
            env["MSMPI_ROOT"] = prefix
            path = mpiabi._dlopen_path()
            self.assertIn(bindir, path)
            env.clear()
            env["MSMPI_BIN"] = bindir
            path = mpiabi._dlopen_path()
            self.assertIn(bindir, path)
            env.clear()
        finally:
            os.name = os_name_save
            os.environ = os_environ_save  # noqa: B003
            sys.platform = sys_platform_save
            if os.name == "nt":
                for attr in rtldmodes:
                    delattr(os, attr)


if __name__ == "__main__":
    unittest.main()
