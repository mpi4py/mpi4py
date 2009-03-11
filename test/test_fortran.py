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
