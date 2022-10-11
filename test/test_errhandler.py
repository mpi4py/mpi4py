from mpi4py import MPI
import mpiunittest as unittest


class TestErrhandler(unittest.TestCase):

    def testPredefined(self):
        self.assertFalse(MPI.ERRHANDLER_NULL)
        self.assertTrue(MPI.ERRORS_ARE_FATAL)
        self.assertTrue(MPI.ERRORS_RETURN)
        if MPI.VERSION >= 4:
            self.assertTrue(MPI.ERRORS_ABORT)
        elif MPI.ERRORS_ABORT != MPI.ERRHANDLER_NULL:
            self.assertTrue(MPI.ERRORS_ABORT)
        else:
            self.assertFalse(MPI.ERRORS_ABORT)


class BaseTestErrhandler:

    def testCall(self):
        mpiobj = self.mpiobj
        mpiobj.Set_errhandler(MPI.ERRORS_RETURN)
        try:
            mpiobj.Call_errhandler(MPI.SUCCESS)
            mpiobj.Call_errhandler(MPI.ERR_OTHER)
        except NotImplementedError:
            if MPI.VERSION >= 2: raise
            clsname = type(mpiobj).__name__.lower()
            self.skipTest(f'mpi-{clsname}-call-errhandler')

    def testGetFree(self):
        mpiobj = self.mpiobj
        errhdls = []
        for i in range(100):
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

    @unittest.skipUnless(MPI.ERRORS_ABORT, 'mpi-errors-abort')
    @unittest.skipMPI("mpich(<4.1.0)")
    def testErrorsAbort(self):
        self._run_test_get_set(MPI.ERRORS_ABORT)


class TestErrhandlerComm(BaseTestErrhandler, unittest.TestCase):

    def setUp(self):
        self.mpiobj = MPI.COMM_SELF.Dup()

    def tearDown(self):
        self.mpiobj.Free()


class TestErrhandlerWin(BaseTestErrhandler, unittest.TestCase):

    def setUp(self):
        try:
            self.mpiobj = MPI.Win.Create(MPI.BOTTOM, 1, MPI.INFO_NULL, MPI.COMM_SELF)
        except NotImplementedError:
            self.skipTest('mpi-win')
        except MPI.Exception:
            self.skipTest('mpi-win')

    def tearDown(self):
        self.mpiobj.Free()

    @unittest.skipMPI('SpectrumMPI')
    def testCall(self):
        super().testCall()


class TestErrhandlerFile(BaseTestErrhandler, unittest.TestCase):

    def setUp(self):
        import os, tempfile
        rank = MPI.COMM_WORLD.Get_rank()
        fd, filename = tempfile.mkstemp(prefix='mpi4py-', suffix=f"-{rank}")
        os.close(fd)
        amode = MPI.MODE_WRONLY | MPI.MODE_CREATE | MPI.MODE_DELETE_ON_CLOSE
        try:
            self.mpiobj = MPI.File.Open(MPI.COMM_SELF, filename, amode, MPI.INFO_NULL)
        except NotImplementedError:
            try:
                os.remove(filename)
            except OSError:
                pass
            self.skipTest('mpi-file')

    def tearDown(self):
        self.mpiobj.Close()

    @unittest.skipMPI('msmpi')
    def testCall(self):
        super().testCall()


class TestErrhandlerSession(BaseTestErrhandler, unittest.TestCase):

    def setUp(self):
        try:
            self.mpiobj = MPI.Session.Init()
        except NotImplementedError:
            self.skipTest('mpi-session')

    def tearDown(self):
        self.mpiobj.Finalize()


if __name__ == '__main__':
    unittest.main()
