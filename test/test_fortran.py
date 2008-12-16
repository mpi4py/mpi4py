from mpi4py import MPI
import mpiunittest as unittest

class TestFortranBase(object):
    HANDLES = []
    def testFortran(self):
        for handle1 in self.HANDLES:
            try:
                fint = handle1.py2f()
            except NotImplementedError:
                continue
            handle2 = type(handle1).f2py(fint)
            self.assertEqual(handle1, handle2)

class TestFortranDatatype(TestFortranBase, unittest.TestCase):
    HANDLES = [MPI.CHAR,  MPI.SHORT,
               MPI.INT,   MPI.LONG,
               MPI.FLOAT, MPI.DOUBLE,
               ]

class TestFortranOp(TestFortranBase, unittest.TestCase):
    HANDLES =  [MPI.MAX, MPI.MIN,
                MPI.SUM, MPI.PROD,
                MPI.LAND, MPI.BAND,
                MPI.LOR, MPI.BOR,
                MPI.LXOR, MPI.BXOR,
                MPI.MAXLOC, MPI.MINLOC,
                ]

class TestFortranRequest(TestFortranBase, unittest.TestCase):
    HANDLES = [MPI.REQUEST_NULL,
               ]

class TestFortranErrhandler(TestFortranBase, unittest.TestCase):
    HANDLES = [MPI.ERRHANDLER_NULL,
               MPI.ERRORS_RETURN,
               MPI.ERRORS_ARE_FATAL,
               ]

class TestFortranInfo(TestFortranBase, unittest.TestCase):
    HANDLES = [MPI.INFO_NULL,
               ]

class TestFortranGroup(TestFortranBase, unittest.TestCase):
    HANDLES = [MPI.GROUP_NULL,
               MPI.GROUP_EMPTY,
               ]

class TestFortranComm(TestFortranBase, unittest.TestCase):
    HANDLES = [MPI.COMM_NULL,
               MPI.COMM_SELF,
               MPI.COMM_WORLD,
               ]

class TestFortranWin(TestFortranBase, unittest.TestCase):
    HANDLES = [MPI.WIN_NULL,
               ]

class TestFortranFile(TestFortranBase, unittest.TestCase):
    HANDLES = [MPI.FILE_NULL,
               ]

if __name__ == '__main__':
    unittest.main()
