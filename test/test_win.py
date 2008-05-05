from mpi4py import MPI
import mpiunittest as unittest

class TestWinBase(object):

    COMM = MPI.COMM_NULL
    INFO = MPI.INFO_NULL

    def setUp(self):
        try:
            zero = str8('\0')
        except NameError:
            zero = str('\0')
        self.memory = MPI.Alloc_mem(10)
        self.memory[:] = zero * len(self.memory)
        self.WIN = MPI.Win.Create(self.memory, 1, self.INFO, self.COMM)

    def tearDown(self):
        self.WIN.Free()
        MPI.Free_mem(self.memory)

    def testGetMemory(self):
        memory = self.WIN.memory
        pointer = MPI.Get_address(memory)
        length = len(memory)
        base, size, dunit = self.WIN.attrs
        self.assertEqual(pointer, base)
        self.assertEqual(length,  size)


    def testGetAttributes(self):
        base, size, unit = self.WIN.attrs
        self.assertEqual(base, MPI.Get_address(self.memory))
        self.assertEqual(size, len(self.memory))
        self.assertEqual(unit, 1)
        cgroup = self.COMM.Get_group()
        wgroup = self.WIN.Get_group()
        grpcmp = MPI.Group.Compare(cgroup, wgroup)
        cgroup.Free()
        wgroup.Free()
        self.assertEqual(grpcmp, MPI.IDENT)

    def testGetSetErrhandler(self):
        self.assertRaisesMPI(MPI.ERR_ARG, self.WIN.Set_errhandler, MPI.ERRHANDLER_NULL)
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

class TestWinNull(unittest.TestCase):

    def testFree(self):
        self.assertRaisesMPI(MPI.ERR_WIN, MPI.WIN_NULL.Free)

    def testGetErrhandler(self):
        self.assertRaisesMPI(MPI.ERR_WIN, MPI.WIN_NULL.Get_errhandler)

    def testSetErrhandler(self):
        self.assertRaisesMPI(MPI.ERR_WIN, MPI.WIN_NULL.Set_errhandler, MPI.ERRORS_RETURN)

    def testCallErrhandler(self):
        self.assertRaisesMPI(MPI.ERR_WIN, MPI.WIN_NULL.Call_errhandler, 0)

class TestWinSelf(TestWinBase, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestWinWorld(TestWinBase, unittest.TestCase):
    COMM = MPI.COMM_WORLD


try:
    w = MPI.Win.Create(None, 1, MPI.INFO_NULL, MPI.COMM_SELF).Free()
except NotImplementedError:
    del TestWinNull, TestWinSelf, TestWinWorld


if __name__ == '__main__':
    unittest.main()
