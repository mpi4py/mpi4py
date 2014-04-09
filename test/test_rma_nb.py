from mpi4py import MPI
import mpiunittest as unittest
import arrayimpl

def mkzeros(n):
    import sys
    if not hasattr(sys, 'pypy_version_info'):
        try:
            return bytearray([0]) * n
        except NameError:
            return str('\0') * n
    return str('\0') * n

def memzero(m):
    n = len(m)
    if n == 0: return
    try:
        zero = '\0'.encode('ascii')
        m[0] = zero
    except TypeError:
        zero = 0
        m[0] = zero
    for i in range(n):
        m[i] = zero

class BaseTestRMA(object):

    COMM = MPI.COMM_NULL
    INFO = MPI.INFO_NULL

    COUNT_MIN = 0

    def setUp(self):
        nbytes = 100*MPI.DOUBLE.size
        try:
            self.mpi_memory = MPI.Alloc_mem(nbytes)
            self.memory = self.mpi_memory
            memzero(self.memory)
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
                        sbuf = array([rank]*count, typecode)
                        rbuf = array(-1, typecode, count+1)
                        self.WIN.Lock(MPI.LOCK_EXCLUSIVE, rank)
                        r = self.WIN.Rput(sbuf.as_mpi(), rank)
                        r.Wait()
                        r = self.WIN.Rget(rbuf.as_mpi_c(count), rank)
                        r.Wait()
                        self.WIN.Unlock(rank)
                        for i in range(count):
                            self.assertEqual(sbuf[i], rank)
                            self.assertEqual(rbuf[i], rank)
                        self.assertEqual(rbuf[-1], -1)

    def testAccumulate(self):
        group = self.WIN.Get_group()
        size = group.Get_size()
        group.Free()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for count in range(self.COUNT_MIN, 10):
                    for rank in range(size):
                        ones = array([1]*count, typecode)
                        sbuf = array(range(count), typecode)
                        rbuf = array(-1, typecode, count+1)
                        for op in (MPI.SUM, MPI.PROD,
                                   MPI.MAX, MPI.MIN,
                                   MPI.REPLACE):
                            self.WIN.Lock(MPI.LOCK_EXCLUSIVE, rank)
                            self.WIN.Put(ones.as_mpi(), rank)
                            r = self.WIN.Raccumulate(sbuf.as_mpi(), rank, op=op)
                            r.Wait()
                            self.WIN.Get(rbuf.as_mpi_c(count), rank)
                            self.WIN.Unlock(rank)
                            #
                            for i in range(count):
                                self.assertEqual(sbuf[i], i)
                                self.assertEqual(rbuf[i], op(1,i))
                            self.assertEqual(rbuf[-1], -1)

    def testGetAccumulate(self):
        group = self.WIN.Get_group()
        size = group.Get_size()
        group.Free()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for count in range(1, 10): # XXX MPICH fails with buf=NULL
                    for rank in range(size):
                        ones = array([1]*count, typecode)
                        sbuf = array(range(count), typecode)
                        rbuf = array(-1, typecode, count+1)
                        gbuf = array(-1, typecode, count+1)
                        for op in (MPI.SUM, MPI.PROD,
                                   MPI.MAX, MPI.MIN,
                                   MPI.REPLACE, MPI.NO_OP):
                            self.WIN.Lock(MPI.LOCK_EXCLUSIVE, rank)
                            self.WIN.Put(ones.as_mpi(), rank)
                            r = self.WIN.Rget_accumulate(sbuf.as_mpi(),
                                                         rbuf.as_mpi_c(count),
                                                         rank, op=op)
                            r.Wait()
                            self.WIN.Get(gbuf.as_mpi_c(count), rank)
                            self.WIN.Unlock(rank)
                            #
                            for i in range(count):
                                self.assertEqual(sbuf[i], i)
                                self.assertEqual(rbuf[i], 1)
                                self.assertEqual(gbuf[i], op(1, i))
                            self.assertEqual(rbuf[-1], -1)
                            self.assertEqual(gbuf[-1], -1)

    def testPutProcNull(self):
        self.WIN.Lock_all()
        r = self.WIN.Rput(None, MPI.PROC_NULL, None)
        r.Wait()
        self.WIN.Unlock_all()

    def testGetProcNull(self):
        self.WIN.Lock_all()
        r = self.WIN.Rget(None, MPI.PROC_NULL, None)
        r.Wait()
        self.WIN.Unlock_all()

    def testAccumulateProcNullReplace(self):
        zeros = mkzeros(8)
        self.WIN.Lock_all()
        r = self.WIN.Raccumulate([zeros, MPI.INT], MPI.PROC_NULL, None, MPI.REPLACE)
        r.Wait()
        r = self.WIN.Raccumulate([zeros, MPI.INT], MPI.PROC_NULL, None, MPI.REPLACE)
        r.Wait()
        self.WIN.Unlock_all()

    def testAccumulateProcNullSum(self):
        zeros = mkzeros(8)
        self.WIN.Lock_all()
        r = self.WIN.Raccumulate([zeros, MPI.INT], MPI.PROC_NULL, None, MPI.SUM)
        r.Wait()
        r = self.WIN.Raccumulate([None, MPI.INT], MPI.PROC_NULL, None, MPI.SUM)
        r.Wait()
        self.WIN.Unlock_all()

class TestRMASelf(BaseTestRMA, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestRMAWorld(BaseTestRMA, unittest.TestCase):
    COMM = MPI.COMM_WORLD


try:
    MPI.Win.Create(None, 1, MPI.INFO_NULL, MPI.COMM_SELF).Free()
except NotImplementedError:
    del TestRMASelf, TestRMAWorld
else:
    name, version = MPI.get_vendor()
    if name == 'Open MPI':
        if version < (1, 8, 0):
            del TestRMASelf, TestRMAWorld
    elif name == 'MPICH2':
        if version < (1, 5, 0):
            del TestRMASelf, TestRMAWorld
    elif MPI.Get_version() < (3, 0):
        del TestRMASelf, TestRMAWorld

if __name__ == '__main__':
    unittest.main()
