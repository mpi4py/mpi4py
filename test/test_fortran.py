from mpi4py import MPI
import mpiunittest as unittest

class BaseTestFortran:

    HANDLES = []

    def check(self, handle1):
        try:
            fint = handle1.py2f()
        except NotImplementedError:
            self.skipTest(type(handle1).__name__)
        handle2 = type(handle1).f2py(fint)
        self.assertEqual(handle1, handle2)

    def create(self):
        handle = None
        klass = type(self.HANDLES[0])
        if issubclass(klass, MPI.Status):
            handle = MPI.Status()
        if issubclass(klass, MPI.Datatype):
            handle = MPI.BYTE.Dup()
        if issubclass(klass, MPI.Op):
            handle = MPI.Op.Create(lambda *_: None)
        if issubclass(klass, MPI.Request):
            handle = MPI.COMM_SELF.Recv_init(bytearray(0), 0, 0)
        if issubclass(klass, MPI.Message):
            handle = MPI.MESSAGE_NULL
        if issubclass(klass, MPI.Errhandler):
            handle = MPI.ERRHANDLER_NULL
        if issubclass(klass, MPI.Info):
            handle = MPI.Info.Create()
        if issubclass(klass, MPI.Group):
            handle = MPI.COMM_SELF.Get_group()
        if issubclass(klass, MPI.Session):
            handle = MPI.Session.Init()
        if issubclass(klass, MPI.Comm):
            handle = MPI.COMM_SELF.Dup()
        if issubclass(klass, MPI.Win):
            handle = MPI.Win.Create(MPI.BOTTOM, comm=MPI.COMM_SELF)
        if issubclass(klass, MPI.File):
            import os
            name = os.devnull
            mode = MPI.MODE_RDONLY
            if os.name != 'posix':
                import tempfile
                rank = MPI.COMM_WORLD.Get_rank()
                fd, name = tempfile.mkstemp(prefix=f'mpi4py-{rank}-')
                os.close(fd)
                mode |= MPI.MODE_CREATE
                mode |= MPI.MODE_DELETE_ON_CLOSE
            handle = MPI.File.Open(MPI.COMM_SELF, name, mode)
        return handle

    def destroy(self, handle):
        if handle:
            for method in ('Free', 'Close', 'Finalize'):
                if hasattr(handle, method):
                    getattr(handle, method)()

    def testFortran(self):
        for handle in self.HANDLES:
            self.check(handle)
            if not handle:
                continue
            if not hasattr(handle, 'Dup'):
                continue
            handle = handle.Dup()
            try:
                self.check(handle)
            finally:
                handle.Free()
        try:
            handle = self.create()
        except (NotImplementedError, MPI.Exception):
            klass = type(self.HANDLES[0])
            self.skipTest(klass.__name__)
        try:
            self.check(handle)
        finally:
            self.destroy(handle)

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
        super().testFortran()

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
    HANDLES = [
        MPI.DATATYPE_NULL,
        MPI.CHAR,  MPI.SHORT,
        MPI.INT,   MPI.LONG,
        MPI.FLOAT, MPI.DOUBLE,
    ]

class TestFortranOp(BaseTestFortran, unittest.TestCase):
    HANDLES = [
        MPI.OP_NULL,
        MPI.MAX, MPI.MIN,
        MPI.SUM, MPI.PROD,
        MPI.LAND, MPI.BAND,
        MPI.LOR, MPI.BOR,
        MPI.LXOR, MPI.BXOR,
        MPI.MAXLOC, MPI.MINLOC,
    ]

class TestFortranRequest(BaseTestFortran, unittest.TestCase):
    HANDLES = [
        MPI.REQUEST_NULL,
    ]

class TestFortranMessage(BaseTestFortran, unittest.TestCase):
    HANDLES = [
        MPI.MESSAGE_NULL,
        MPI.MESSAGE_NO_PROC,
    ]

class TestFortranErrhandler(BaseTestFortran, unittest.TestCase):
    HANDLES = [
        MPI.ERRHANDLER_NULL,
        MPI.ERRORS_RETURN,
        MPI.ERRORS_ARE_FATAL,
    ]

class TestFortranInfo(BaseTestFortran, unittest.TestCase):
    HANDLES = [
        MPI.INFO_NULL,
    ]

class TestFortranGroup(BaseTestFortran, unittest.TestCase):
    HANDLES = [
        MPI.GROUP_NULL,
        MPI.GROUP_EMPTY,
    ]

class TestFortranSession(BaseTestFortran, unittest.TestCase):
    HANDLES = [
        MPI.SESSION_NULL,
    ]

class TestFortranComm(BaseTestFortran, unittest.TestCase):
    HANDLES = [
        MPI.COMM_NULL,
        MPI.COMM_SELF,
        MPI.COMM_WORLD,
    ]

class TestFortranWin(BaseTestFortran, unittest.TestCase):
    HANDLES = [
        MPI.WIN_NULL,
    ]

class TestFortranFile(BaseTestFortran, unittest.TestCase):
    HANDLES = [
        MPI.FILE_NULL,
    ]


if __name__ == '__main__':
    unittest.main()
