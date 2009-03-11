from mpi4py import MPI
import mpiunittest as unittest

class TestErrhandler(unittest.TestCase):

    def testPredefined(self):
        self.assertFalse(MPI.ERRHANDLER_NULL)
        self.assertTrue(MPI.ERRORS_ARE_FATAL)
        self.assertTrue(MPI.ERRORS_RETURN)

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

    def testGetErrhandler(self):
        errhdls = []
        for i in range(100):
            e = MPI.COMM_WORLD.Get_errhandler()
            errhdls.append(e)
        for e in errhdls:
            e.Free()
        for e in errhdls:
            self.assertEqual(e, MPI.ERRHANDLER_NULL)

if __name__ == '__main__':
    unittest.main()
