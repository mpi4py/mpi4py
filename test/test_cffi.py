from mpi4py import MPI
import mpiunittest as unittest
try:
    import cffi
except ImportError:
    cffi = None

class TestCFFI(unittest.TestCase):

    mpitypes = [
        MPI.Datatype,
        MPI.Request,
        MPI.Info,
        MPI.Errhandler,
        MPI.Group,
        MPI.Win,
        MPI.Op,
        MPI.File,
        MPI.Message,
        MPI.Comm,
    ]

    objects = [
        MPI.DATATYPE_NULL,
        MPI.INT,
        MPI.DOUBLE,
        MPI.REQUEST_NULL,
        MPI.INFO_NULL,
        MPI.INFO_ENV,
        MPI.ERRHANDLER_NULL,
        MPI.ERRORS_RETURN,
        MPI.ERRORS_ARE_FATAL,
        MPI.GROUP_NULL,
        MPI.GROUP_EMPTY,
        MPI.WIN_NULL,
        MPI.OP_NULL,
        MPI.SUM,
        MPI.MIN,
        MPI.MAX,
        MPI.FILE_NULL,
        MPI.MESSAGE_NULL,
        MPI.MESSAGE_NO_PROC,
        MPI.COMM_NULL,
        MPI.COMM_SELF,
        MPI.COMM_WORLD,
    ]

    def testHandle(self):
        ffi = cffi.FFI()
        typemap = {ffi.sizeof('int'): 'int',
                   ffi.sizeof('void*'): 'void*'}
        for tp in self.mpitypes:
            handle_t = typemap[MPI._sizeof(tp)]
            mpi_t = 'MPI_' + tp.__name__
            ffi.cdef("typedef %s %s;" % (handle_t, mpi_t))
        for obj in self.objects:
            if isinstance(obj, MPI.Comm):
                mpi_t = 'MPI_Comm'
            else:
                mpi_t = 'MPI_' + type(obj).__name__
            oldobj = obj
            newobj = type(obj)()
            handle_old = ffi.cast(mpi_t+'*', MPI._addressof(oldobj))
            handle_new = ffi.cast(mpi_t+'*', MPI._addressof(newobj))
            handle_new[0] = handle_old[0]
            self.assertEqual(oldobj, newobj)

if cffi is None:
    del TestCFFI

if __name__ == '__main__':
    unittest.main()
