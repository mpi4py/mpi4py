import os
import pathlib
import sys
import tempfile

import mpiunittest as unittest

from mpi4py import MPI


class TestErrhandler(unittest.TestCase):
    #
    def testPredefined(self):
        self.assertFalse(MPI.ERRHANDLER_NULL)
        self.assertTrue(MPI.ERRORS_ARE_FATAL)
        self.assertTrue(MPI.ERRORS_RETURN)
        if MPI.Get_version() >= (4, 0):
            self.assertTrue(MPI.ERRORS_ABORT)
        elif MPI.ERRORS_ABORT != MPI.ERRHANDLER_NULL:
            self.assertTrue(MPI.ERRORS_ABORT)
        else:
            self.assertFalse(MPI.ERRORS_ABORT)

    def testPickle(self):
        from pickle import dumps, loads

        for errhandler in [
            MPI.ERRHANDLER_NULL,
            MPI.ERRORS_ARE_FATAL,
            MPI.ERRORS_RETURN,
            MPI.ERRORS_ABORT,
        ]:
            if not errhandler:
                continue
            errh = loads(dumps(errhandler))
            self.assertIs(errh, errhandler)
            errh = loads(dumps(MPI.Errhandler(errhandler)))
            self.assertIsNot(errh, errhandler)
            self.assertEqual(errh, errhandler)


class BaseTestErrhandler:
    #
    def testCreate(self):
        MAX_USER_EH = 32  # max user-defined error handlers
        mpiobj = self.mpiobj
        index = None
        called = check = False

        def get_errhandler_fn(idx):
            def errhandler_fn(arg, err):
                nonlocal mpiobj, index, called, check
                called = check = True
                check &= arg == mpiobj
                check &= err == MPI.ERR_OTHER
                check &= idx == index

            return errhandler_fn

        def check_handle(eh):
            cint = eh.toint()
            if cint != -1:
                clon = type(eh).fromint(cint)
                self.assertEqual(eh, clon)
            fint = eh.py2f()
            if fint != -1:
                clon = type(eh).f2py(fint)
                self.assertEqual(eh, clon)

        errhandlers = []
        for index in range(MAX_USER_EH):
            try:
                fn = get_errhandler_fn(index)
                eh = type(mpiobj).Create_errhandler(fn)
                errhandlers.append(eh)
            except NotImplementedError:
                clsname = type(mpiobj).__name__.lower()
                self.skipTest(f"mpi-{clsname}-create_errhandler")
        with self.assertRaises(RuntimeError):
            type(mpiobj).Create_errhandler(lambda _arg, _err: None)

        for eh in errhandlers:
            self.assertTrue(eh)
            check_handle(eh)
            with self.assertRaises(ValueError):
                eh.__reduce__()

        eh_orig = mpiobj.Get_errhandler()
        try:
            for i, eh in enumerate(errhandlers):
                index = i
                called = check = False
                mpiobj.Set_errhandler(eh)
                try:
                    mpiobj.Call_errhandler(MPI.SUCCESS)
                    mpiobj.Call_errhandler(MPI.ERR_OTHER)
                except NotImplementedError:
                    if MPI.Get_version() >= (2, 0):
                        raise
                else:
                    self.assertTrue(called)
                    self.assertTrue(check)
                finally:
                    mpiobj.Set_errhandler(eh_orig)
        finally:
            for eh in errhandlers:
                eh.Free()

    def testCall(self):
        mpiobj = self.mpiobj
        mpiobj.Set_errhandler(MPI.ERRORS_RETURN)
        try:
            mpiobj.Call_errhandler(MPI.SUCCESS)
            mpiobj.Call_errhandler(MPI.ERR_OTHER)
        except NotImplementedError:
            if MPI.Get_version() >= (2, 0):
                raise
            clsname = type(mpiobj).__name__.lower()
            self.skipTest(f"mpi-{clsname}-call_errhandler")

    def testGetFree(self):
        mpiobj = self.mpiobj
        errhdls = []
        for _i in range(100):
            e = mpiobj.Get_errhandler()
            errhdls.append(e)
        for e in errhdls:
            e.Free()
        for e in errhdls:
            self.assertEqual(e, MPI.ERRHANDLER_NULL)

    def _run_test_get_set(self, errhandler):
        mpiobj = self.mpiobj
        errhdl_1 = mpiobj.Get_errhandler()
        self.assertNotEqual(errhdl_1, MPI.ERRHANDLER_NULL)
        mpiobj.Set_errhandler(errhandler)
        errhdl_2 = mpiobj.Get_errhandler()
        self.assertEqual(errhdl_2, errhandler)
        errhdl_2.Free()
        self.assertEqual(errhdl_2, MPI.ERRHANDLER_NULL)
        mpiobj.Set_errhandler(errhdl_1)
        errhdl_1.Free()
        self.assertEqual(errhdl_1, MPI.ERRHANDLER_NULL)

    def testErrorsReturn(self):
        self._run_test_get_set(MPI.ERRORS_RETURN)

    def testErrorsFatal(self):
        self._run_test_get_set(MPI.ERRORS_ARE_FATAL)

    @unittest.skipUnless(MPI.ERRORS_ABORT, "mpi-errors-abort")
    @unittest.skipMPI("mpich(<4.1.0)")
    @unittest.skipMPI("openmpi(<5.0.0)")
    @unittest.skipMPI("impi(<2021.14.0)")
    def testErrorsAbort(self):
        self._run_test_get_set(MPI.ERRORS_ABORT)


class TestErrhandlerComm(BaseTestErrhandler, unittest.TestCase):
    #
    def setUp(self):
        self.mpiobj = MPI.COMM_SELF.Dup()

    def tearDown(self):
        self.mpiobj.Free()


@unittest.skipMPI("openmpi(<4.1.0)", sys.platform == "darwin")
class TestErrhandlerWin(BaseTestErrhandler, unittest.TestCase):
    #
    def setUp(self):
        try:
            self.mpiobj = MPI.Win.Create(
                MPI.BOTTOM, 1, MPI.INFO_NULL, MPI.COMM_SELF
            )
        except NotImplementedError:
            self.skipTest("mpi-win")
        except MPI.Exception:
            self.skipTest("mpi-win")

    def tearDown(self):
        self.mpiobj.Free()

    def testCall(self):
        super().testCall()


class TestErrhandlerFile(BaseTestErrhandler, unittest.TestCase):
    #
    def setUp(self):
        rank = MPI.COMM_WORLD.Get_rank()
        fd, filename = tempfile.mkstemp(prefix="mpi4py-", suffix=f"-{rank}")
        os.close(fd)
        amode = MPI.MODE_WRONLY | MPI.MODE_CREATE | MPI.MODE_DELETE_ON_CLOSE
        try:
            self.mpiobj = MPI.File.Open(
                MPI.COMM_SELF, filename, amode, MPI.INFO_NULL
            )
        except NotImplementedError:
            try:
                pathlib.Path(filename).unlink()
            except OSError:
                pass
            self.skipTest("mpi-file")

    def tearDown(self):
        self.mpiobj.Close()

    @unittest.skipMPI("msmpi")
    def testCall(self):
        super().testCall()


class TestErrhandlerSession(BaseTestErrhandler, unittest.TestCase):
    #
    def setUp(self):
        try:
            self.mpiobj = MPI.Session.Init()
        except NotImplementedError:
            self.skipTest("mpi-session")

    def tearDown(self):
        self.mpiobj.Finalize()


if __name__ == "__main__":
    unittest.main()
