from mpi4py import MPI
import mpiunittest as unittest

class BaseTestFortran(object):
    HANDLES = []
    def testFortran(self):
        for handle1 in self.HANDLES:
            try:
                fint = handle1.py2f()
            except NotImplementedError:
                continue
            handle2 = type(handle1).f2py(fint)
            self.assertEqual(handle1, handle2)

class TestFortranStatus(BaseTestFortran, unittest.TestCase):
    def setUp(self):
        s1 = MPI.Status()
        s2 = MPI.Status()
        s2.source = 1
        s2.tag = 2
        s2.error = MPI.ERR_OTHER
        s3 = MPI.Status()
        s3.source = 0
        s3.tag = 0
        s3.error = MPI.SUCCESS
        self.HANDLES = [s1, s2, s3]

    @unittest.skipMPI('MPICH1')
    def testFortran(self):
        super(TestFortranStatus, self).testFortran()

    def testFintArray(self):
        s = MPI.F_SOURCE
        t = MPI.F_TAG
        e = MPI.F_ERROR
        for status in self.HANDLES:
            try:
                f_status = status.py2f()
            except NotImplementedError:
                continue
            self.assertEqual(f_status[s], status.Get_source())
            self.assertEqual(f_status[t], status.Get_tag())
            self.assertEqual(f_status[e], status.Get_error())
            self.assertEqual(len(f_status), MPI.F_STATUS_SIZE)

class TestFortranDatatype(BaseTestFortran, unittest.TestCase):
    HANDLES = [MPI.DATATYPE_NULL,
               MPI.CHAR,  MPI.SHORT,
               MPI.INT,   MPI.LONG,
               MPI.FLOAT, MPI.DOUBLE,
               ]

class TestFortranOp(BaseTestFortran, unittest.TestCase):
    HANDLES =  [MPI.OP_NULL,
                MPI.MAX, MPI.MIN,
                MPI.SUM, MPI.PROD,
                MPI.LAND, MPI.BAND,
                MPI.LOR, MPI.BOR,
                MPI.LXOR, MPI.BXOR,
                MPI.MAXLOC, MPI.MINLOC,
                ]

class TestFortranRequest(BaseTestFortran, unittest.TestCase):
    HANDLES = [MPI.REQUEST_NULL,
               ]

class TestFortranMessage(BaseTestFortran, unittest.TestCase):
    HANDLES = [MPI.MESSAGE_NULL,
               MPI.MESSAGE_NO_PROC,
               ]

class TestFortranErrhandler(BaseTestFortran, unittest.TestCase):
    HANDLES = [MPI.ERRHANDLER_NULL,
               MPI.ERRORS_RETURN,
               MPI.ERRORS_ARE_FATAL,
               ]

class TestFortranInfo(BaseTestFortran, unittest.TestCase):
    HANDLES = [MPI.INFO_NULL,
               ]

class TestFortranGroup(BaseTestFortran, unittest.TestCase):
    HANDLES = [MPI.GROUP_NULL,
               MPI.GROUP_EMPTY,
               ]

class TestFortranComm(BaseTestFortran, unittest.TestCase):
    HANDLES = [MPI.COMM_NULL,
               MPI.COMM_SELF,
               MPI.COMM_WORLD,
               ]

class TestFortranWin(BaseTestFortran, unittest.TestCase):
    HANDLES = [MPI.WIN_NULL,
               ]

class TestFortranFile(BaseTestFortran, unittest.TestCase):
    HANDLES = [MPI.FILE_NULL,
               ]


if __name__ == '__main__':
    unittest.main()
