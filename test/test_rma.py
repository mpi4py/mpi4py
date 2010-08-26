from mpi4py import MPI
import mpiunittest as unittest
import arrayimpl

class BaseTestRMA(object):

    COMM = MPI.COMM_NULL
    INFO = MPI.INFO_NULL

    COUNT_MIN = 0

    def setUp(self):
        nbytes = 100*MPI.DOUBLE.size
        try:
            self.mpi_memory = MPI.Alloc_mem(nbytes)
            self.memory = self.mpi_memory
            try:
                zero = bytearray([0])
            except NameError:
                zero = str('\0')
            self.memory[:] = zero * len(self.memory)
        except MPI.Exception:
            from array import array
            self.mpi_memory = None
            self.memory = array('B',[0]*nbytes)
        self.WIN = MPI.Win.Create(self.memory, 1, self.INFO, self.COMM)

    def tearDown(self):
        self.WIN.Free()
        if self.mpi_memory:
            MPI.Free_mem(self.mpi_memory)

    def testPutGet(self):
        group = self.WIN.Get_group()
        size = group.Get_size()
        group.Free()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for count in range(self.COUNT_MIN, 10):
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
                for count in range(self.COUNT_MIN, 10):
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

    def testAccumulateProcNullReplace(self):
        self.WIN.Fence()
        try: zeros = bytearray([0]) * 8
        except NameError: zeros = str('\0')* 8
        self.WIN.Fence()
        self.WIN.Accumulate([zeros, MPI.INT], MPI.PROC_NULL, None, MPI.REPLACE)
        self.WIN.Fence()
        self.WIN.Accumulate([zeros, MPI.INT], MPI.PROC_NULL, None, MPI.REPLACE)
        self.WIN.Fence()

    def testAccumulateProcNullSum(self):
        self.WIN.Fence()
        try: zeros = bytearray([0]) * 8
        except NameError: zeros = str('\0')* 8
        self.WIN.Fence()
        self.WIN.Accumulate([zeros, MPI.INT], MPI.PROC_NULL, None, MPI.SUM)
        self.WIN.Fence()
        self.WIN.Accumulate([None, MPI.INT], MPI.PROC_NULL, None, MPI.SUM)
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

class TestRMASelf(BaseTestRMA, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestRMAWorld(BaseTestRMA, unittest.TestCase):
    COMM = MPI.COMM_WORLD


try:
    w = MPI.Win.Create(None, 1, MPI.INFO_NULL, MPI.COMM_SELF).Free()
except NotImplementedError:
    del TestRMASelf, TestRMAWorld

_name, _version = MPI.get_vendor()
if _name == 'Open MPI':
    if _version < (1, 4, 0):
        if MPI.Query_thread() > MPI.THREAD_SINGLE:
            del TestRMAWorld
elif _name == 'HP MPI':
    BaseTestRMA.COUNT_MIN = 1

if __name__ == '__main__':
    unittest.main()
