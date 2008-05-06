from mpi4py import MPI
import mpiunittest as unittest
import arrayimpl

class TestRMABase(object):

    COMM = MPI.COMM_NULL
    INFO = MPI.INFO_NULL

    def setUp(self):
        try:
            zero = str8('\0')
        except NameError:
            zero = str('\0')
        self.memory = MPI.Alloc_mem(100*MPI.DOUBLE.size)
        self.memory[:] = zero * len(self.memory)
        self.WIN = MPI.Win.Create(self.memory, 1,
                                  self.INFO, self.COMM)

    def tearDown(self):
        self.WIN.Free()
        MPI.Free_mem(self.memory)

    def testPutGet(self):
        group = self.WIN.Get_group()
        size = group.Get_size()
        group.Free()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for count in range(0, 10):
                    for rank in range(size):
                        sbuf = array(range(count), typecode)
                        rbuf = array(-1, typecode, count+1)
                        self.WIN.Fence()
                        self.WIN.Put(sbuf.as_mpi(), rank)
                        self.WIN.Fence()
                        self.WIN.Get(rbuf.as_mpi_c(count), rank)
                        self.WIN.Fence()
                        for i in range(count):
                            self.assertEqual(sbuf[i], i)
                            self.assertNotEqual(rbuf[i], -1)
                        self.assertEqual(rbuf[-1], -1)

    def testAccumulate(self):
        group = self.WIN.Get_group()
        size = group.Get_size()
        group.Free()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for count in range(0, 10):
                    for rank in range(size):
                        sbuf = array(range(count), typecode)
                        rbuf = array(-1, typecode, count+1)
                        for op in (MPI.SUM, MPI.PROD, MPI.MAX, MPI.MIN):
                            self.WIN.Fence()
                            self.WIN.Accumulate(sbuf.as_mpi(), rank, op=op)
                            self.WIN.Fence()
                            self.WIN.Get(rbuf.as_mpi_c(count), rank)
                            self.WIN.Fence()
                            #
                            for i in range(count):
                                self.assertEqual(sbuf[i], i)
                                self.assertNotEqual(rbuf[i], -1)
                            self.assertEqual(rbuf[-1], -1)


    def testPutProcNull(self):
        self.WIN.Fence()
        self.WIN.Put(None, MPI.PROC_NULL, None)
        self.WIN.Fence()

    def testGetProcNull(self):
        self.WIN.Fence()
        self.WIN.Get(None, MPI.PROC_NULL, None)
        self.WIN.Fence()

    def testAccumulateProcNull(self):
        self.WIN.Fence()
        self.WIN.Accumulate(None, MPI.PROC_NULL, None, MPI.SUM)
        self.WIN.Fence()

    def testFence(self):
        self.WIN.Fence()
        assertion = 0
        modes = [0,
                 MPI.MODE_NOSTORE,
                 MPI.MODE_NOPUT,
                 MPI.MODE_NOPRECEDE,
                 MPI.MODE_NOSUCCEED]
        self.WIN.Fence()
        for mode in modes:
            self.WIN.Fence(mode)
            assertion |= mode
            self.WIN.Fence(assertion)
        self.WIN.Fence()

class TestRMASelf(TestRMABase, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestRMAWorld(TestRMABase, unittest.TestCase):
    COMM = MPI.COMM_WORLD


try:
    w = MPI.Win.Create(None, 1, MPI.INFO_NULL, MPI.COMM_SELF).Free()
except NotImplementedError:
    del TestRMASelf, TestRMAWorld


if __name__ == '__main__':
    unittest.main()
