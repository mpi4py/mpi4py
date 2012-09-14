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
                        r = self.WIN.Rput(sbuf.as_mpi(), rank)
                        r.Wait()
                        self.WIN.Fence()
                        r = self.WIN.Rget(rbuf.as_mpi_c(count), rank)
                        r.Wait()
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
                            r = self.WIN.Raccumulate(sbuf.as_mpi(), rank, op=op)
                            r.Wait()
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
        r = self.WIN.Rput(None, MPI.PROC_NULL, None)
        r.Wait()
        self.WIN.Fence()

    def testGetProcNull(self):
        self.WIN.Fence()
        r = self.WIN.Rget(None, MPI.PROC_NULL, None)
        r.Wait()
        self.WIN.Fence()

    def testAccumulateProcNullReplace(self):
        self.WIN.Fence()
        try: zeros = bytearray([0]) * 8
        except NameError: zeros = str('\0')* 8
        self.WIN.Fence()
        r = self.WIN.Raccumulate([zeros, MPI.INT], MPI.PROC_NULL, None, MPI.REPLACE)
        r.Wait()
        self.WIN.Fence()
        r = self.WIN.Raccumulate([zeros, MPI.INT], MPI.PROC_NULL, None, MPI.REPLACE)
        r.Wait()
        self.WIN.Fence()

    def testAccumulateProcNullSum(self):
        self.WIN.Fence()
        try: zeros = bytearray([0]) * 8
        except NameError: zeros = str('\0')* 8
        self.WIN.Fence()
        r = self.WIN.Raccumulate([zeros, MPI.INT], MPI.PROC_NULL, None, MPI.SUM)
        r.Wait()
        self.WIN.Fence()
        r = self.WIN.Raccumulate([None, MPI.INT], MPI.PROC_NULL, None, MPI.SUM)
        r.Wait()
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
    del TestRMASelf, TestRMAWorld
if _name == 'MPICH2':
    del TestRMASelf, TestRMAWorld
else:
    try:
        del TestRMASelf, TestRMAWorld
    except NameError:
        pass

if __name__ == '__main__':
    unittest.main()
