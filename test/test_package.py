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
        import mpi4py.util.pkl5
        import mpi4py.util.dtlib


class TestDataFiles(unittest.TestCase):

    @unittest.skipIf(sys.version_info < (3, 7), 'py36')
    def testTyping(self):
        py_typed = os.path.join(pkgdir, 'py.typed')
        self.assertTrue(os.path.exists(py_typed))
        for root, dirs, files in os.walk(pkgdir):
            for fname in files:
                if fname.endswith(".py"):
                    pyi = os.path.join(root, f"{fname}i")
                    self.assertTrue(os.path.exists(pyi))

    def testCython(self):
        for fname in [
            "__init__.pxd",
            "libmpi.pxd",
            "MPI.pxd",
        ]:
            pxd = os.path.join(pkgdir, fname)
            self.assertTrue(os.path.exists(pxd))

    def testHeaders(self):
        incdir = mpi4py.get_include()
        for fname in [
            os.path.join(pkgdir, "MPI.h"),
            os.path.join(pkgdir, "MPI_api.h"),
            os.path.join(incdir, "mpi4py", "mpi4py.h"),
            os.path.join(incdir, "mpi4py", "mpi4py.i"),
        ]:
            hdr = os.path.join(pkgdir, fname)
            self.assertTrue(os.path.exists(hdr))


if __name__ == '__main__':
    unittest.main()
