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
        self.mpiabi = importlib.import_module("mpi4py._mpiabi")
        self.sentinel = getattr(self.mpiabi._get_mpiabi, "mpiabi", None)

    def tearDown(self):
        self.mpiabi._registry.pop("mpi4py.xyz", None)
        if self.sentinel is not None:
            self.mpiabi._get_mpiabi.mpiabi = self.sentinel
        elif hasattr(self.mpiabi._get_mpiabi, "mpiabi"):
            del self.mpiabi._get_mpiabi.mpiabi
        del self.mpiabi

    def testGetStr(self):
        importlib.import_module("mpi4py.MPI")
        mpiabi = self.mpiabi
        saved = mpiabi.MPIABI
        try:
            mpiabi.MPIABI = "@mpiabi@"
            result = mpiabi._get_mpiabi()
            self.assertEqual(result, mpiabi.MPIABI)
        finally:
            mpiabi.MPIABI = saved
        result = mpiabi._get_mpiabi()

    def testGetLib(self):
        importlib.import_module("mpi4py.MPI")
        mpiabi = self.mpiabi
        abinames = {"mpiabi", "mpich", "openmpi", "impi", "msmpi"}
        result = mpiabi._get_mpiabi()
        self.assertIn(result, abinames)

    def testString(self):
        mpiabi = self.mpiabi
        posix = os.name == "posix"
        for string, expected in (
            ("MPICH", "mpich" if posix else "impi"),
            ("I_MPI", "mpich" if posix else "impi"),
            ("Open MPI", "openmpi"),
            ("OPEN-MPI", "openmpi"),
            ("", ""),
        ):
            result = mpiabi._get_mpiabi_from_string(string)
            self.assertEqual(result, expected)

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
        try:
            for os_name, sys_platform in (
                ("posix", "linux"),
                ("posix", "freebsd"),
                ("posix", "darwin"),
                ("nt", "win32"),
            ):
                os.name = os_name
                sys.platform = sys_platform
                mpiabi._dlopen_rpath()
            os.environ = env = {}
            env["I_MPI_ROOT"] = "/usr"
            mpiabi._dlopen_rpath()
            env["MSMPI_ROOT"] = "/usr"
            mpiabi._dlopen_rpath()
            env["MSMPI_BIN"] = "/usr/bin"
            mpiabi._dlopen_rpath()
        finally:
            os.name = os_name_save
            os.environ = os_environ_save  # noqa: B003
            sys.platform = sys_platform_save


if __name__ == "__main__":
    unittest.main()
