from mpi4py import MPI
import mpiunittest as unittest
import contextlib
import arrayimpl

def mkzeros(n):
    return bytearray(n)

def memzero(m):
    try:
        m[:] = 0
    except IndexError: # cffi buffer
        m[0:len(m)] = b'\0'*len(m)

@contextlib.contextmanager
def win_lock(win, rank, *args, **kwargs):
    win.Lock(rank, *args, **kwargs)
    try:
        yield
    finally:
        win.Unlock(rank)

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
            self.mpi_memory = None
            self.memory = bytearray(nbytes)
        self.WIN = MPI.Win.Create(self.memory, 1, self.INFO, self.COMM)

    def tearDown(self):
        self.WIN.Free()
        if self.mpi_memory:
            MPI.Free_mem(self.mpi_memory)

    def testPutGet(self):
        group = self.WIN.Get_group()
        size = group.Get_size()
        group.Free()
        for array, typecode in arrayimpl.loop():
            with arrayimpl.test(self):
                if unittest.is_mpi_gpu('mvapich2', array): continue
                for count in range(self.COUNT_MIN, 10):
                    for rank in range(size):
                        with self.subTest(rank=rank, count=count):
                            sbuf = array([rank]*count, typecode)
                            rbuf = array(-1, typecode, count+1)
                            self.WIN.Fence()
                            with win_lock(self.WIN, rank):
                                r = self.WIN.Rput(sbuf.as_mpi(), rank)
                                r.Wait()
                                self.WIN.Flush(rank)
                                r = self.WIN.Rget(rbuf.as_mpi_c(count), rank)
                                r.Wait()
                            for i in range(count):
                                self.assertEqual(sbuf[i], rank)
                                self.assertEqual(rbuf[i], rank)
                            self.assertEqual(rbuf[-1], -1)

    @unittest.skipMPI('openmpi(>=1.10.0,<1.11.0)')
    def testAccumulate(self):
        group = self.WIN.Get_group()
        size = group.Get_size()
        group.Free()
        for array, typecode in arrayimpl.loop():
            with arrayimpl.test(self):
                if unittest.is_mpi_gpu('openmpi', array): continue
                if unittest.is_mpi_gpu('mvapich2', array): continue
                if typecode in 'FDG': continue
                for count in range(self.COUNT_MIN, 10):
                    for rank in range(size):
                        with self.subTest(rank=rank, count=count):
                            ones = array([1]*count, typecode)
                            sbuf = array(range(count), typecode)
                            rbuf = array(-1, typecode, count+1)
                            for op in (
                                MPI.SUM, MPI.PROD,
                                MPI.MAX, MPI.MIN,
                                MPI.REPLACE,
                            ):
                                with win_lock(self.WIN, rank):
                                    self.WIN.Put(ones.as_mpi(), rank)
                                    self.WIN.Flush(rank)
                                    r = self.WIN.Raccumulate(sbuf.as_mpi(),
                                                             rank, op=op)
                                    r.Wait()
                                    self.WIN.Flush(rank)
                                    r = self.WIN.Rget(rbuf.as_mpi_c(count), rank)
                                    r.Wait()
                                #
                                for i in range(count):
                                    self.assertEqual(sbuf[i], i)
                                    self.assertEqual(rbuf[i], op(1, i))
                                self.assertEqual(rbuf[-1], -1)

    @unittest.skipMPI('openmpi(>=1.10,<1.11)')
    def testGetAccumulate(self):
        group = self.WIN.Get_group()
        size = group.Get_size()
        group.Free()
        for array, typecode in arrayimpl.loop():
            with arrayimpl.test(self):
                if unittest.is_mpi_gpu('openmpi', array): continue
                if unittest.is_mpi_gpu('mvapich2', array): continue
                if typecode in 'FDG': continue
                for count in range(self.COUNT_MIN, 10):
                    for rank in range(size):
                        with self.subTest(rank=rank, count=count):
                            ones = array([1]*count, typecode)
                            sbuf = array(range(count), typecode)
                            rbuf = array(-1, typecode, count+1)
                            gbuf = array(-1, typecode, count+1)
                            for op in (
                                MPI.SUM, MPI.PROD,
                                MPI.MAX, MPI.MIN,
                                MPI.REPLACE, MPI.NO_OP,
                            ):
                                with win_lock(self.WIN, rank):
                                    self.WIN.Put(ones.as_mpi(), rank)
                                    self.WIN.Flush(rank)
                                    r = self.WIN.Rget_accumulate(sbuf.as_mpi(),
                                                                 rbuf.as_mpi_c(count),
                                                                 rank, op=op)
                                    r.Wait()
                                    self.WIN.Flush(rank)
                                    r = self.WIN.Rget(gbuf.as_mpi_c(count), rank)
                                    r.Wait()
                                #
                                for i in range(count):
                                    self.assertEqual(sbuf[i], i)
                                    self.assertEqual(rbuf[i], 1)
                                    self.assertEqual(gbuf[i], op(1, i))
                                self.assertEqual(rbuf[-1], -1)
                                self.assertEqual(gbuf[-1], -1)

    def testPutProcNull(self):
        rank = self.COMM.Get_rank()
        with win_lock(self.WIN, rank):
            r = self.WIN.Rput(None, MPI.PROC_NULL, None)
            r.Wait()

    def testGetProcNull(self):
        rank = self.COMM.Get_rank()
        with win_lock(self.WIN, rank):
            r = self.WIN.Rget(None, MPI.PROC_NULL, None)
            r.Wait()

    def testAccumulateProcNullReplace(self):
        rank = self.COMM.Get_rank()
        zeros = mkzeros(8)
        with win_lock(self.WIN, rank):
            r = self.WIN.Raccumulate([zeros, MPI.INT], MPI.PROC_NULL, None, MPI.REPLACE)
            r.Wait()
            r = self.WIN.Raccumulate([zeros, MPI.INT], MPI.PROC_NULL, None, MPI.REPLACE)
            r.Wait()

    def testAccumulateProcNullSum(self):
        rank = self.COMM.Get_rank()
        zeros = mkzeros(8)
        with win_lock(self.WIN, rank):
            r = self.WIN.Raccumulate([zeros, MPI.INT], MPI.PROC_NULL, None, MPI.SUM)
            r.Wait()
            r = self.WIN.Raccumulate([None, MPI.INT], MPI.PROC_NULL, None, MPI.SUM)
            r.Wait()


@unittest.skipMPI('MPI(<3.0)')
@unittest.skipMPI('openmpi(<1.8.1)')
@unittest.skipMPI('MPICH2(<1.5.0)')
class TestRMASelf(BaseTestRMA, unittest.TestCase):
    COMM = MPI.COMM_SELF

@unittest.skipMPI('MPI(<3.0)')
@unittest.skipMPI('openmpi(<1.8.1)')
@unittest.skipMPI('MPICH2(<1.5.0)')
class TestRMAWorld(BaseTestRMA, unittest.TestCase):
    COMM = MPI.COMM_WORLD


SpectrumMPI = MPI.get_vendor()[0] == 'Spectrum MPI'
try:
    if SpectrumMPI: raise NotImplementedError
    MPI.Win.Create(None, 1, MPI.INFO_NULL, MPI.COMM_SELF).Free()
except (NotImplementedError, MPI.Exception):
    unittest.disable(BaseTestRMA, 'mpi-rma-nb')


if __name__ == '__main__':
    unittest.main()
