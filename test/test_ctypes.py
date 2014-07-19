from mpi4py import MPI
import mpiunittest as unittest
try:
    import ctypes
except ImportError:
    ctypes = None

class TestCTYPES(unittest.TestCase):

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
        typemap = {ctypes.sizeof(ctypes.c_int): ctypes.c_int,
                   ctypes.sizeof(ctypes.c_void_p): ctypes.c_void_p}
        for obj in self.objects:
            handle_t = typemap[MPI._sizeof(obj)]
            oldobj = obj
            newobj = type(obj)()
            handle_old = handle_t.from_address(MPI._addressof(oldobj))
            handle_new = handle_t.from_address(MPI._addressof(newobj))
            handle_new.value = handle_old.value
            self.assertEqual(obj, newobj)

if ctypes is None:
    del TestCTYPES

if __name__ == '__main__':
    unittest.main()
