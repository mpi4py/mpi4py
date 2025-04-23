import importlib
import os
import pathlib
import unittest

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


if __name__ == "__main__":
    unittest.main()
