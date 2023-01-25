from mpi4py import MPI
import mpiunittest as unittest
import contextlib
import arrayimpl
import sys

scalar = arrayimpl.scalar

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

@contextlib.contextmanager
def win_lock_all(win, *args, **kwargs):
    win.Lock_all(*args, **kwargs)
    try:
        yield
    finally:
        win.Unlock_all()

class BaseTestRMA:

    COMM = MPI.COMM_NULL
    INFO = MPI.INFO_NULL

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
        typemap = MPI._typedict
        group = self.WIN.Get_group()
        size = group.Get_size()
        group.Free()
        for array, typecode in arrayimpl.loop():
            with arrayimpl.test(self):
                if unittest.is_mpi_gpu('mvapich2', array): continue
                for count in range(10):
                    for rank in range(size):
                        with self.subTest(rank=rank, count=count):
                            sbuf = array(range(count), typecode)
                            rbuf = array(-1, typecode, count+1)
                            #
                            self.WIN.Fence()
                            self.WIN.Put(sbuf.as_mpi(), rank)
                            self.WIN.Fence()
                            self.WIN.Get(rbuf.as_mpi_c(count), rank)
                            self.WIN.Fence()
                            for i in range(count):
                                self.assertEqual(sbuf[i], scalar(i))
                                self.assertEqual(rbuf[i], scalar(i))
                            self.assertEqual(rbuf[-1], scalar(-1))
                            #
                            sbuf = array(range(count), typecode)
                            rbuf = array(-1, typecode, count+1)
                            target  = sbuf.itemsize
                            self.WIN.Fence()
                            self.WIN.Put(sbuf.as_mpi(), rank, target)
                            self.WIN.Fence()
                            self.WIN.Get(rbuf.as_mpi_c(count), rank, target)
                            self.WIN.Fence()
                            for i in range(count):
                                self.assertEqual(sbuf[i], scalar(i))
                                self.assertEqual(rbuf[i], scalar(i))
                            self.assertEqual(rbuf[-1], scalar(-1))
                            #
                            sbuf = array(range(count), typecode)
                            rbuf = array(-1, typecode, count+1)
                            datatype = typemap[typecode]
                            target  = (sbuf.itemsize, count, datatype)
                            self.WIN.Fence()
                            self.WIN.Put(sbuf.as_mpi(), rank, target)
                            self.WIN.Fence()
                            self.WIN.Get(rbuf.as_mpi_c(count), rank, target)
                            self.WIN.Fence()
                            for i in range(count):
                                self.assertEqual(sbuf[i], scalar(i))
                                self.assertEqual(rbuf[i], scalar(i))
                            self.assertEqual(rbuf[-1], scalar(-1))

    def testAccumulate(self):
        group = self.WIN.Get_group()
        size = group.Get_size()
        group.Free()
        for array, typecode in arrayimpl.loop():
            with arrayimpl.test(self):
                if unittest.is_mpi_gpu('openmpi', array): continue
                if unittest.is_mpi_gpu('mvapich2', array): continue
                if typecode in '?': continue
                if typecode in 'FDG': continue
                for count in range(10):
                    for rank in range(size):
                        with self.subTest(rank=rank, count=count):
                            sbuf = array(range(count), typecode)
                            rbuf = array(-1, typecode, count+1)
                            for op in (MPI.SUM, MPI.PROD, MPI.MAX, MPI.MIN):
                                self.WIN.Fence()
                                self.WIN.Accumulate(sbuf.as_mpi(), rank, op=op)
                                self.WIN.Fence()
                                self.WIN.Get(rbuf.as_mpi_c(count), rank)
                                self.WIN.Fence()
                                for i in range(count):
                                    self.assertEqual(sbuf[i], scalar(i))
                                    self.assertNotEqual(rbuf[i], scalar(-1))
                                self.assertEqual(rbuf[-1], scalar(-1))

    @unittest.skipMPI('openmpi(>=1.10,<1.11)')
    def testGetAccumulate(self):
        group = self.WIN.Get_group()
        size = group.Get_size()
        rank = group.Get_rank()
        group.Free()
        self.WIN.Fence()
        obuf = MPI.Alloc_mem(1); memzero(obuf)
        rbuf = MPI.Alloc_mem(1); memzero(rbuf)
        try:
            try:
                self.WIN.Get_accumulate([obuf, 0, MPI.BYTE], [rbuf, 0, MPI.BYTE], rank)
                self.WIN.Fence()
            finally:
                MPI.Free_mem(obuf)
                MPI.Free_mem(rbuf)
        except NotImplementedError:
            self.skipTest('mpi-win-get_accumulate')
        self.WIN.Fence()
        for array, typecode in arrayimpl.loop():
            with arrayimpl.test(self):
                if unittest.is_mpi_gpu('openmpi', array): continue
                if unittest.is_mpi_gpu('mvapich2', array): continue
                if typecode in '?': continue
                if typecode in 'FDG': continue
                for count in range(10):
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
                                    self.WIN.Get_accumulate(sbuf.as_mpi(),
                                                            rbuf.as_mpi_c(count),
                                                            rank, op=op)
                                    self.WIN.Flush(rank)
                                    self.WIN.Get(gbuf.as_mpi_c(count), rank)
                                    self.WIN.Flush(rank)
                                #
                                for i in range(count):
                                    self.assertEqual(sbuf[i], scalar(i))
                                    self.assertEqual(rbuf[i], scalar(1))
                                    self.assertEqual(gbuf[i], scalar(op(1, i)))
                                self.assertEqual(rbuf[-1], scalar(-1))
                                self.assertEqual(gbuf[-1], scalar(-1))

    def testFetchAndOp(self):
        typemap = MPI._typedict
        group = self.WIN.Get_group()
        size = group.Get_size()
        rank = group.Get_rank()
        group.Free()
        self.WIN.Fence()
        blen = MPI.INT.Get_size()
        obuf = MPI.Alloc_mem(blen); memzero(obuf)
        rbuf = MPI.Alloc_mem(blen); memzero(rbuf)
        try:
            try:
                self.WIN.Fetch_and_op(
                    [obuf, 1, MPI.INT],
                    [rbuf, 1, MPI.INT],
                    rank)
                self.WIN.Fence()
            finally:
                MPI.Free_mem(obuf)
                MPI.Free_mem(rbuf)
        except NotImplementedError:
            self.skipTest('mpi-win-fetch_and_op')
        self.WIN.Fence()
        for array, typecode in arrayimpl.loop():
            with arrayimpl.test(self):
                if unittest.is_mpi_gpu('openmpi', array): continue
                if unittest.is_mpi_gpu('mvapich2', array): continue
                if typecode in '?': continue
                if typecode in 'FDG': continue
                obuf = array(+1, typecode)
                rbuf = array(-1, typecode, 2)
                datatype = typemap[typecode]
                for op in (
                    MPI.SUM, MPI.PROD,
                    MPI.MAX, MPI.MIN,
                    MPI.REPLACE, MPI.NO_OP,
                ):
                    for rank in range(size):
                        for disp in range(3):
                            with self.subTest(disp=disp, rank=rank):
                                with win_lock(self.WIN, rank):
                                    self.WIN.Fetch_and_op(obuf.as_mpi(),
                                                          rbuf.as_mpi_c(1),
                                                          rank,
                                                          disp * datatype.size,
                                                          op=op)
                                self.assertEqual(rbuf[1], scalar(-1))

    @unittest.skipMPI('mpich(>=4.0,<4.1)', sys.platform == 'darwin')
    def testCompareAndSwap(self):
        typemap = MPI._typedict
        group = self.WIN.Get_group()
        size = group.Get_size()
        rank = group.Get_rank()
        group.Free()
        self.WIN.Fence()
        obuf = MPI.Alloc_mem(1); memzero(obuf)
        cbuf = MPI.Alloc_mem(1); memzero(cbuf)
        rbuf = MPI.Alloc_mem(1); memzero(rbuf)
        try:
            try:
                self.WIN.Compare_and_swap([obuf, 1, MPI.BYTE],
                                          [cbuf, 1, MPI.BYTE],
                                          [rbuf, 1, MPI.BYTE],
                                          rank, 0)
                self.WIN.Fence()
            finally:
                MPI.Free_mem(obuf)
                MPI.Free_mem(cbuf)
                MPI.Free_mem(rbuf)
        except NotImplementedError:
            self.skipTest('mpi-win-compare_and_swap')
        self.WIN.Fence()
        for array, typecode in arrayimpl.loop():
            with arrayimpl.test(self):
                if unittest.is_mpi_gpu('openmpi', array): continue
                if unittest.is_mpi_gpu('mvapich2', array): continue
                if typecode in 'fdg': continue
                if typecode in 'FDG': continue
                obuf = array(+1, typecode)
                cbuf = array( 0, typecode)
                rbuf = array(-1, typecode, 2)
                datatype = typemap[typecode]
                for rank in range(size):
                    for disp in range(3):
                        with self.subTest(disp=disp, rank=rank):
                            with win_lock(self.WIN, rank):
                                self.WIN.Compare_and_swap(obuf.as_mpi(),
                                                          cbuf.as_mpi(),
                                                          rbuf.as_mpi_c(1),
                                                          rank,
                                                          disp * datatype.size)
                            self.assertEqual(rbuf[1], scalar(-1))

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
        zeros = mkzeros(8)
        self.WIN.Fence()
        self.WIN.Accumulate([zeros, MPI.INT], MPI.PROC_NULL, None, MPI.REPLACE)
        self.WIN.Fence()
        self.WIN.Accumulate([zeros, MPI.INT], MPI.PROC_NULL, None, MPI.REPLACE)
        self.WIN.Fence()

    def testAccumulateProcNullSum(self):
        self.WIN.Fence()
        zeros = mkzeros(8)
        self.WIN.Fence()
        self.WIN.Accumulate([zeros, MPI.INT], MPI.PROC_NULL, None, MPI.SUM)
        self.WIN.Fence()
        self.WIN.Accumulate([None, MPI.INT], MPI.PROC_NULL, None, MPI.SUM)
        self.WIN.Fence()

    def testGetAccumulateProcNull(self):
        obuf = [mkzeros(8), 0, MPI.INT]
        rbuf = [mkzeros(8), 0, MPI.INT]
        self.WIN.Fence()
        try:
            self.WIN.Get_accumulate(obuf, rbuf, MPI.PROC_NULL)
        except NotImplementedError:
            self.skipTest('mpi-win-get_accumulate')
        self.WIN.Fence()

    ##def testFetchAndOpProcNull(self):
    ##    obuf = cbuf = rbuf = None
    ##    self.WIN.Fence()
    ##    try:
    ##        self.WIN.Fetch_and_op(obuf, rbuf, MPI.PROC_NULL, 0)
    ##    except NotImplementedError:
    ##        self.skipTest('mpi-win-fetch_and_op')
    ##    self.WIN.Fence()

    ##def testCompareAndSwapProcNull(self):
    ##    obuf = cbuf = rbuf = None
    ##    self.WIN.Fence()
    ##    try:
    ##        self.WIN.Compare_and_swap(obuf, cbuf, rbuf, MPI.PROC_NULL, 0)
    ##    except NotImplementedError:
    ##        self.skipTest('mpi-win-compare_and_swap')
    ##    self.WIN.Fence()

    def testFence(self):
        win = self.WIN
        LMODE = [
            0,
            MPI.MODE_NOSTORE,
            MPI.MODE_NOPUT,
            MPI.MODE_NOSTORE|MPI.MODE_NOPUT,
        ]
        GMODE = [
            0,
            MPI.MODE_NOPRECEDE,
            MPI.MODE_NOSUCCEED,
        ]
        win.Fence()
        for lmode in LMODE:
            for gmode in GMODE:
                assertion =  lmode | gmode
                win.Fence(assertion)
        win.Fence()

    @unittest.skipMPI('openmpi(==1.8.1)')
    def testFenceAll(self):
        win = self.WIN
        assertion = 0
        modes = [
            0,
            MPI.MODE_NOSTORE,
            MPI.MODE_NOPUT,
            MPI.MODE_NOPRECEDE,
            MPI.MODE_NOSUCCEED,
        ]
        win.Fence()
        for mode in modes:
            win.Fence(mode)
            assertion |= mode
            win.Fence(assertion)
        win.Fence()

    @unittest.skipMPI('openmpi(==1.8.6)')
    def testStartComplete(self):
        self.WIN.Start(MPI.GROUP_EMPTY)
        self.WIN.Complete()

    @unittest.skipMPI('openmpi(==1.8.6)')
    def testPostWait(self):
        self.WIN.Post(MPI.GROUP_EMPTY)
        self.WIN.Wait()

    @unittest.skipMPI('openmpi(==1.8.7)')
    @unittest.skipMPI('openmpi(==1.8.6)')
    def testStartCompletePostWait(self):
        win = self.WIN
        wingroup = win.Get_group()
        size = wingroup.Get_size()
        rank = wingroup.Get_rank()
        if size < 2: return wingroup.Free()
        if rank == 0:
            group = wingroup.Excl([0])
            win.Start(group)
            win.Complete()
            win.Post(group)
            win.Wait()
            group.Free()
        else:
            group = wingroup.Incl([0])
            win.Post(group)
            win.Wait()
            win.Start(group)
            win.Complete()
            group.Free()
        wingroup.Free()

    @unittest.skipMPI('openmpi(==1.8.7)')
    @unittest.skipMPI('openmpi(==1.8.6)')
    def testStartCompletePostTest(self):
        comm = self.COMM
        win = self.WIN
        wingroup = win.Get_group()
        size = wingroup.Get_size()
        rank = wingroup.Get_rank()
        if size < 2: return wingroup.Free()
        if rank == 0:
            group = wingroup.Excl([0])
            win.Start(group)
            comm.Barrier()
            win.Complete()
            comm.Barrier()
            group.Free()
        else:
            group = wingroup.Incl([0])
            win.Post(group)
            flag = win.Test()
            self.assertFalse(flag)
            comm.Barrier()
            comm.Barrier()
            flag = win.Test()
            self.assertTrue(flag)
            group.Free()
        wingroup.Free()

    @unittest.skipMPI('MPI(<3.0)')
    def testSync(self):
        win = self.WIN
        comm = self.COMM
        rank = comm.Get_rank()
        with win_lock(win, rank):
            win.Sync()
        comm.Barrier()

    @unittest.skipMPI('MPI(<3.0)')
    def testFlush(self):
        win = self.WIN
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        #
        for i in range(size):
            with win_lock(win, i):
                win.Flush(i)
        comm.Barrier()
        for i in range(size):
            if i == rank:
                with win_lock_all(win):
                    win.Flush_all()
            comm.Barrier()
        #
        for i in range(size):
            with win_lock(win, i):
                win.Flush_local(i)
        comm.Barrier()
        for i in range(size):
            if i == rank:
                with win_lock_all(win):
                    win.Flush_local_all()
            comm.Barrier()

class TestRMASelf(BaseTestRMA, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestRMAWorld(BaseTestRMA, unittest.TestCase):
    COMM = MPI.COMM_WORLD


SpectrumMPI = MPI.get_vendor()[0] == 'Spectrum MPI'
try:
    if SpectrumMPI: raise NotImplementedError
    MPI.Win.Create(None, 1, MPI.INFO_NULL, MPI.COMM_SELF).Free()
except (NotImplementedError, MPI.Exception):
    unittest.disable(BaseTestRMA, 'mpi-rma')


if __name__ == '__main__':
    unittest.main()
