from mpi4py import MPI
import mpiunittest as unittest


class TestErrhandler(unittest.TestCase):

    def testPredefined(self):
        self.assertFalse(MPI.ERRHANDLER_NULL)
        self.assertTrue(MPI.ERRORS_ARE_FATAL)
        self.assertTrue(MPI.ERRORS_RETURN)
        if MPI.VERSION >= 4:
            self.assertTrue(MPI.ERRORS_ABORT)
        else:
            self.assertFalse(MPI.ERRORS_ABORT)

    def testGetErrhandler(self):
        errhdls = []
        for i in range(100):
            e = MPI.COMM_WORLD.Get_errhandler()
            errhdls.append(e)
        for e in errhdls:
            e.Free()
        for e in errhdls:
            self.assertEqual(e, MPI.ERRHANDLER_NULL)

    def testSessionGetSetErrhandler(self):
        try:
            session = MPI.Session.Init()
        except NotImplementedError:
            self.skipTest('mpi-session')
        for ERRHANDLER in [
            MPI.ERRORS_ARE_FATAL,
            MPI.ERRORS_RETURN,
            MPI.ERRORS_ARE_FATAL,
            MPI.ERRORS_RETURN,
        ]:
            errhdl_1 = session.Get_errhandler()
            self.assertNotEqual(errhdl_1, MPI.ERRHANDLER_NULL)
            session.Set_errhandler(ERRHANDLER)
            errhdl_2 = session.Get_errhandler()
            self.assertEqual(errhdl_2, ERRHANDLER)
            errhdl_2.Free()
            self.assertEqual(errhdl_2, MPI.ERRHANDLER_NULL)
            session.Set_errhandler(errhdl_1)
            errhdl_1.Free()
            self.assertEqual(errhdl_1, MPI.ERRHANDLER_NULL)
        session.Finalize()

    def testCommGetSetErrhandler(self):
        for COMM in [MPI.COMM_SELF, MPI.COMM_WORLD]:
            for ERRHANDLER in [MPI.ERRORS_ARE_FATAL, MPI.ERRORS_RETURN,
                               MPI.ERRORS_ARE_FATAL, MPI.ERRORS_RETURN, ]:
                errhdl_1 = COMM.Get_errhandler()
                self.assertNotEqual(errhdl_1, MPI.ERRHANDLER_NULL)
                COMM.Set_errhandler(ERRHANDLER)
                errhdl_2 = COMM.Get_errhandler()
                self.assertEqual(errhdl_2, ERRHANDLER)
                errhdl_2.Free()
                self.assertEqual(errhdl_2, MPI.ERRHANDLER_NULL)
                COMM.Set_errhandler(errhdl_1)
                errhdl_1.Free()
                self.assertEqual(errhdl_1, MPI.ERRHANDLER_NULL)

    def testSessionCallErrhandler(self):
        try:
            session = MPI.Session.Init()
        except NotImplementedError:
            self.skipTest('mpi-session')
        session.Set_errhandler(MPI.ERRORS_RETURN)
        session.Call_errhandler(MPI.ERR_OTHER)
        session.Finalize()

    @unittest.skipMPI('MPI(<2.0)')
    def testCommCallErrhandler(self):
        errhdl = MPI.COMM_SELF.Get_errhandler()
        comm = MPI.COMM_SELF.Dup()
        comm.Set_errhandler(MPI.ERRORS_RETURN)
        comm.Call_errhandler(MPI.ERR_OTHER)
        comm.Free()

    @unittest.skipMPI('MPI(<2.0)')
    @unittest.skipMPI('SpectrumMPI')
    def testWinCallErrhandler(self):
        try:
            win = MPI.Win.Create(MPI.BOTTOM, 1, MPI.INFO_NULL, MPI.COMM_SELF)
        except NotImplementedError:
            self.skipTest('mpi-win')
        win.Set_errhandler(MPI.ERRORS_RETURN)
        win.Call_errhandler(MPI.ERR_OTHER)
        win.Free()

    @unittest.skipMPI('MPI(<2.0)')
    @unittest.skipMPI('msmpi')
    def testFileCallErrhandler(self):
        import os, tempfile
        rank = MPI.COMM_WORLD.Get_rank()
        fd, filename = tempfile.mkstemp(prefix='mpi4py-', suffix="-%d"%rank)
        os.close(fd)
        amode = MPI.MODE_WRONLY | MPI.MODE_CREATE | MPI.MODE_DELETE_ON_CLOSE
        try:
            file = MPI.File.Open(MPI.COMM_SELF, filename, amode, MPI.INFO_NULL)
        except NotImplementedError:
            self.skipTest('mpi-file')
        file.Set_errhandler(MPI.ERRORS_RETURN)
        #file.Call_errhandler(MPI.ERR_OTHER)
        file.Call_errhandler(MPI.SUCCESS)
        file.Close()


try:
    MPI.Win.Create(MPI.BOTTOM, 1, MPI.INFO_NULL, MPI.COMM_SELF).Free()
except (NotImplementedError, MPI.Exception):
    TestErrhandler.testWinCallErrhandler = \
    unittest.disable(TestErrhandler.testWinCallErrhandler, 'mpi-win')


if __name__ == '__main__':
    unittest.main()
