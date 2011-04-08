import sys
from mpi4py import MPI
import mpiunittest as unittest

class BaseTestWin(object):

    COMM = MPI.COMM_NULL
    INFO = MPI.INFO_NULL

    def setUp(self):
        try:
            self.mpi_memory = MPI.Alloc_mem(10)
            self.memory = self.mpi_memory
            try:
                zero = bytearray([0])
            except NameError:
                zero = str('\0')
            self.memory[:] = zero * len(self.memory)
        except MPI.Exception:
            from array import array
            self.mpi_memory = None
            self.memory = array('B',[0]*10)
        refcnt = sys.getrefcount(self.memory)
        self.WIN = MPI.Win.Create(self.memory, 1, self.INFO, self.COMM)
        if type(self.memory).__name__ == 'buffer':
            self.assertEqual(sys.getrefcount(self.memory), refcnt+1)
        else:
            self.assertEqual(sys.getrefcount(self.memory), refcnt)

    def tearDown(self):
        refcnt = sys.getrefcount(self.memory)
        self.WIN.Free()
        if type(self.memory).__name__ == 'buffer':
            self.assertEqual(sys.getrefcount(self.memory), refcnt-1)
        else:
            self.assertEqual(sys.getrefcount(self.memory), refcnt)
        if self.mpi_memory:
            MPI.Free_mem(self.mpi_memory)

    def testGetMemory(self):
        memory = self.WIN.memory
        pointer = MPI.Get_address(memory)
        length = len(memory)
        base, size, dunit = self.WIN.attrs
        self.assertEqual(size,  length)
        self.assertEqual(dunit, 1)
        self.assertEqual(base,  pointer)


    def testAttributes(self):
        cgroup = self.COMM.Get_group()
        wgroup = self.WIN.Get_group()
        grpcmp = MPI.Group.Compare(cgroup, wgroup)
        cgroup.Free()
        wgroup.Free()
        self.assertEqual(grpcmp, MPI.IDENT)
        base, size, unit = self.WIN.attrs
        self.assertEqual(size, len(self.memory))
        self.assertEqual(unit, 1)
        self.assertEqual(base, MPI.Get_address(self.memory))

    def testGetAttr(self):
        base = MPI.Get_address(self.memory)
        size = len(self.memory)
        unit = 1
        self.assertEqual(size, self.WIN.Get_attr(MPI.WIN_SIZE))
        self.assertEqual(unit, self.WIN.Get_attr(MPI.WIN_DISP_UNIT))
        self.assertEqual(base, self.WIN.Get_attr(MPI.WIN_BASE))

    def testGetSetErrhandler(self):
        for ERRHANDLER in [MPI.ERRORS_ARE_FATAL, MPI.ERRORS_RETURN,
                           MPI.ERRORS_ARE_FATAL, MPI.ERRORS_RETURN,]:
            errhdl_1 = self.WIN.Get_errhandler()
            self.assertNotEqual(errhdl_1, MPI.ERRHANDLER_NULL)
            self.WIN.Set_errhandler(ERRHANDLER)
            errhdl_2 = self.WIN.Get_errhandler()
            self.assertEqual(errhdl_2, ERRHANDLER)
            errhdl_2.Free()
            self.assertEqual(errhdl_2, MPI.ERRHANDLER_NULL)
            self.WIN.Set_errhandler(errhdl_1)
            errhdl_1.Free()
            self.assertEqual(errhdl_1, MPI.ERRHANDLER_NULL)

    def testGetSetName(self):
        try:
            name = self.WIN.Get_name()
            self.WIN.Set_name('mywin')
            self.assertEqual(self.WIN.Get_name(), 'mywin')
            self.WIN.Set_name(name)
            self.assertEqual(self.WIN.Get_name(), name)
        except NotImplementedError:
            pass

class TestWinSelf(BaseTestWin, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestWinWorld(BaseTestWin, unittest.TestCase):
    COMM = MPI.COMM_WORLD

try:
    w = MPI.Win.Create(MPI.BOTTOM, 1, MPI.INFO_NULL, MPI.COMM_SELF).Free()
except NotImplementedError:
    del BaseTestWin, TestWinSelf, TestWinWorld

_name, _version = MPI.get_vendor()
if _name == 'Open MPI':
    if _version < (1, 4, 0):
        if MPI.Query_thread() > MPI.THREAD_SINGLE:
            del TestWinWorld
elif _name == 'MPICH2':
    if 'win' in sys.platform:
        del BaseTestWin.testAttributes

if __name__ == '__main__':
    unittest.main()
