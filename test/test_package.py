import mpi4py
import unittest
import sys, os

pkgdir = os.path.dirname(mpi4py.__file__)


class TestImport(unittest.TestCase):

    def testImportMPI(self):
        import mpi4py.MPI

    def testImportBench(self):
        import mpi4py.bench

    def testImportFutures(self):
        import mpi4py.futures
        import mpi4py.futures.server
        import mpi4py.futures.__main__

    def testImportRun(self):
        import mpi4py.run
        import mpi4py.__main__

    def testImportTyping(self):
        import mpi4py.typing

    def testImportUtil(self):
        import mpi4py.util
        import mpi4py.util.dtlib
        import mpi4py.util.pkl5
        import mpi4py.util.pool
        import mpi4py.util.sync


class TestDataFiles(unittest.TestCase):

    def testTyping(self):
        import importlib.machinery
        py_typed = os.path.join(pkgdir, "py.typed")
        self.assertTrue(os.path.exists(py_typed))
        suffixes = [
            *importlib.machinery.SOURCE_SUFFIXES,
            *importlib.machinery.EXTENSION_SUFFIXES,
        ]
        for root, dirs, files in os.walk(pkgdir):
            for fname in files:
                name, _, extra = fname.partition(".")
                suffix = f".{extra}"
                for entry in suffixes:
                    if suffix.endswith(entry):
                        pyi = os.path.join(root, f"{name}.pyi")
                        self.assertTrue(os.path.exists(pyi))
                        break

    def testCython(self):
        for fname in [
            "__init__.pxd",
            "libmpi.pxd",
            "MPI.pxd",
        ]:
            pxd = os.path.join(pkgdir, fname)
            self.assertTrue(os.path.exists(pxd))

    def testHeaders(self):
        for fname in [
            os.path.join("MPI.h"),
            os.path.join("MPI_api.h"),
            os.path.join("include", "mpi4py", "pycapi.h"),
            os.path.join("include", "mpi4py", "mpi4py.h"),
            os.path.join("include", "mpi4py", "mpi4py.i"),
        ]:
            hdr = os.path.join(pkgdir, fname)
            self.assertTrue(os.path.exists(hdr))


if __name__ == '__main__':
    unittest.main()
