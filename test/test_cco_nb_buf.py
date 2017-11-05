from mpi4py import MPI
import mpiunittest as unittest
import arrayimpl

from functools import reduce
prod = lambda sequence,start=1: reduce(lambda x, y: x*y, sequence, start)

def maxvalue(a):
    try:
        typecode = a.typecode
    except AttributeError:
        typecode = a.dtype.char
    if typecode == ('f'):
        return 1e30
    elif typecode == ('d'):
        return 1e300
    else:
        return 2 ** (a.itemsize * 7) - 1


@unittest.skipMPI('msmpi(<8.1.0)')
class BaseTestCCOBuf(object):

    COMM = MPI.COMM_NULL

    def testBarrier(self):
        self.COMM.Ibarrier().Wait()

    def testBcast(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for root in range(size):
                    if rank == root:
                        buf = array(root, typecode, root)
                    else:
                        buf = array(  -1, typecode, root)
                    self.COMM.Ibcast(buf.as_mpi(), root=root).Wait()
                    for value in buf:
                        self.assertEqual(value, root)

    def testGather(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for root in range(size):
                    sbuf = array(root, typecode, root+1)
                    if rank == root:
                        rbuf = array(-1, typecode, (size,root+1))
                    else:
                        rbuf = array([], typecode)
                    self.COMM.Igather(sbuf.as_mpi(), rbuf.as_mpi(),
                                      root=root).Wait()
                    if rank == root:
                        for value in rbuf.flat:
                            self.assertEqual(value, root)

    def testScatter(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for root in range(size):
                    rbuf = array(-1, typecode, size)
                    if rank == root:
                        sbuf = array(root, typecode, (size, size))
                    else:
                        sbuf = array([], typecode)
                    self.COMM.Iscatter(sbuf.as_mpi(), rbuf.as_mpi(),
                                       root=root).Wait()
                    for value in rbuf:
                        self.assertEqual(value, root)

    def testAllgather(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for root in range(size):
                    sbuf = array(root, typecode, root+1)
                    rbuf = array(  -1, typecode, (size, root+1))
                    self.COMM.Iallgather(sbuf.as_mpi(), rbuf.as_mpi()).Wait()
                    for value in rbuf.flat:
                        self.assertEqual(value, root)

    def testAlltoall(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for root in range(size):
                    sbuf = array(root, typecode, (size, root+1))
                    rbuf = array(  -1, typecode, (size, root+1))
                    self.COMM.Ialltoall(sbuf.as_mpi(), rbuf.as_mpi_c(root+1)).Wait()
                    for value in rbuf.flat:
                        self.assertEqual(value, root)

    def assertAlmostEqual(self, first, second):
        num = float(float(second-first))
        den = float(second+first)/2 or 1.0
        if (abs(num/den) > 1e-2):
            raise self.failureException('%r != %r' % (first, second))

    def testReduce(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for root in range(size):
                    for op in (MPI.SUM, MPI.PROD, MPI.MAX, MPI.MIN):
                        sbuf = array(range(size), typecode)
                        rbuf = array(-1, typecode, size)
                        self.COMM.Ireduce(sbuf.as_mpi(),
                                          rbuf.as_mpi(),
                                          op, root).Wait()
                        max_val = maxvalue(rbuf)
                        for i, value in enumerate(rbuf):
                            if rank != root:
                                self.assertEqual(value, -1)
                                continue
                            if op == MPI.SUM:
                                if (i * size) < max_val:
                                    self.assertAlmostEqual(value, i*size)
                            elif op == MPI.PROD:
                                if (i ** size) < max_val:
                                    self.assertAlmostEqual(value, i**size)
                            elif op == MPI.MAX:
                                self.assertEqual(value, i)
                            elif op == MPI.MIN:
                                self.assertEqual(value, i)

    def testAllreduce(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for op in (MPI.SUM, MPI.MAX, MPI.MIN, MPI.PROD):
                    sbuf = array(range(size), typecode)
                    rbuf = array(0, typecode, size)
                    self.COMM.Iallreduce(sbuf.as_mpi(),
                                         rbuf.as_mpi(),
                                         op).Wait()
                    max_val = maxvalue(rbuf)
                    for i, value in enumerate(rbuf):
                        if op == MPI.SUM:
                            if (i * size) < max_val:
                                self.assertAlmostEqual(value, i*size)
                        elif op == MPI.PROD:
                            if (i ** size) < max_val:
                                self.assertAlmostEqual(value, i**size)
                        elif op == MPI.MAX:
                            self.assertEqual(value, i)
                        elif op == MPI.MIN:
                            self.assertEqual(value, i)

    @unittest.skipMPI('openmpi(<=1.8.3)')
    def testReduceScatter(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for op in (MPI.SUM, MPI.MAX, MPI.MIN, MPI.PROD):
                    rcnt = list(range(1,size+1))
                    sbuf = array([rank+1]*sum(rcnt), typecode)
                    rbuf = array(-1, typecode, rank+1)
                    self.COMM.Ireduce_scatter(sbuf.as_mpi(),
                                              rbuf.as_mpi(),
                                              None, op).Wait()
                    max_val = maxvalue(rbuf)
                    for i, value in enumerate(rbuf):
                        if op == MPI.SUM:
                            redval = sum(range(size))+size
                            if redval < max_val:
                                self.assertAlmostEqual(value, redval)
                        elif op == MPI.PROD:
                            redval = prod(range(1,size+1))
                            if redval < max_val:
                                self.assertAlmostEqual(value, redval)
                        elif op == MPI.MAX:
                            self.assertEqual(value, size)
                        elif op == MPI.MIN:
                            self.assertEqual(value, 1)
                    rbuf = array(-1, typecode, rank+1)
                    self.COMM.Ireduce_scatter(sbuf.as_mpi(),
                                              rbuf.as_mpi(),
                                              rcnt, op).Wait()
                    max_val = maxvalue(rbuf)
                    for i, value in enumerate(rbuf):
                        if op == MPI.SUM:
                            redval = sum(range(size))+size
                            if redval < max_val:
                                self.assertAlmostEqual(value, redval)
                        elif op == MPI.PROD:
                            redval = prod(range(1,size+1))
                            if redval < max_val:
                                self.assertAlmostEqual(value, redval)
                        elif op == MPI.MAX:
                            self.assertEqual(value, size)
                        elif op == MPI.MIN:
                            self.assertEqual(value, 1)

    def testReduceScatterBlock(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for op in (MPI.SUM, MPI.MAX, MPI.MIN, MPI.PROD):
                    for rcnt in range(1, size+1):
                        sbuf = array([rank]*rcnt*size, typecode)
                        rbuf = array(-1, typecode, rcnt)
                        if op == MPI.PROD:
                            sbuf = array([rank+1]*rcnt*size, typecode)
                        self.COMM.Ireduce_scatter_block(sbuf.as_mpi(),
                                                        rbuf.as_mpi(),
                                                        op).Wait()
                        max_val = maxvalue(rbuf)
                        v_sum  = (size*(size-1))/2
                        v_prod = 1
                        for i in range(1,size+1): v_prod *= i
                        v_max  = size-1
                        v_min  = 0
                        for i, value in enumerate(rbuf):
                            if op == MPI.SUM:
                                if v_sum <= max_val:
                                    self.assertAlmostEqual(value, v_sum)
                            elif op == MPI.PROD:
                                if v_prod <= max_val:
                                    self.assertAlmostEqual(value, v_prod)
                            elif op == MPI.MAX:
                                self.assertEqual(value, v_max)
                            elif op == MPI.MIN:
                                self.assertEqual(value, v_min)

    def testScan(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        # --
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for op in (MPI.SUM, MPI.PROD, MPI.MAX, MPI.MIN):
                    sbuf = array(range(size), typecode)
                    rbuf = array(0, typecode, size)
                    self.COMM.Iscan(sbuf.as_mpi(),
                                    rbuf.as_mpi(),
                                    op).Wait()
                    max_val = maxvalue(rbuf)
                    for i, value in enumerate(rbuf):
                        if op == MPI.SUM:
                            if (i * (rank + 1)) < max_val:
                                self.assertAlmostEqual(value, i * (rank + 1))
                        elif op == MPI.PROD:
                            if (i ** (rank + 1)) < max_val:
                                self.assertAlmostEqual(value, i ** (rank + 1))
                        elif op == MPI.MAX:
                            self.assertEqual(value, i)
                        elif op == MPI.MIN:
                            self.assertEqual(value, i)

    @unittest.skipMPI('openmpi(<=1.8.1)')
    def testExscan(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for op in (MPI.SUM, MPI.PROD, MPI.MAX, MPI.MIN):
                    sbuf = array(range(size), typecode)
                    rbuf = array(0, typecode, size)
                    self.COMM.Iexscan(sbuf.as_mpi(),
                                      rbuf.as_mpi(),
                                      op).Wait()
                    if rank == 1:
                        for i, value in enumerate(rbuf):
                            self.assertEqual(value, i)
                    elif rank > 1:
                        max_val = maxvalue(rbuf)
                        for i, value in enumerate(rbuf):
                            if op == MPI.SUM:
                                if (i * rank) < max_val:
                                    self.assertAlmostEqual(value, i * rank)
                            elif op == MPI.PROD:
                                if (i ** rank) < max_val:
                                    self.assertAlmostEqual(value, i ** rank)
                            elif op == MPI.MAX:
                                self.assertEqual(value, i)
                            elif op == MPI.MIN:
                                self.assertEqual(value, i)


    def testBcastTypeIndexed(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array in arrayimpl.ArrayTypes:
            for typecode, datatype in arrayimpl.TypeMap.items():
                for root in range(size):
                    #
                    if rank == root:
                        buf = array(range(10), typecode).as_raw()
                    else:
                        buf = array(-1, typecode, 10).as_raw()
                    indices = list(range(0, len(buf), 2))
                    newtype = datatype.Create_indexed_block(1, indices)
                    newtype.Commit()
                    newbuf = (buf, 1, newtype)
                    self.COMM.Ibcast(newbuf, root=root).Wait()
                    newtype.Free()
                    if rank != root:
                        for i, value in enumerate(buf):
                            if (i % 2):
                                self.assertEqual(value, -1)
                            else:
                                self.assertEqual(value, i)

                    #
                    if rank == root:
                        buf = array(range(10), typecode).as_raw()
                    else:
                        buf = array(-1, typecode, 10).as_raw()
                    indices = list(range(1, len(buf), 2))
                    newtype = datatype.Create_indexed_block(1, indices)
                    newtype.Commit()
                    newbuf = (buf, 1, newtype)
                    self.COMM.Ibcast(newbuf, root).Wait()
                    newtype.Free()
                    if rank != root:
                        for i, value in enumerate(buf):
                            if not (i % 2):
                                self.assertEqual(value, -1)
                            else:
                                self.assertEqual(value, i)


@unittest.skipMPI('MVAPICH2')
class BaseTestCCOBufInplace(object):

    def testGather(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for root in range(size):
                    count = root+3
                    if rank == root:
                        sbuf = MPI.IN_PLACE
                        buf = array(-1, typecode, (size, count))
                        #buf.flat[(rank*count):((rank+1)*count)] = \
                        #    array(root, typecode, count)
                        s, e = rank*count, (rank+1)*count
                        for i in range(s, e): buf.flat[i] = root
                        rbuf = buf.as_mpi()
                    else:
                        buf = array(root, typecode, count)
                        sbuf = buf.as_mpi()
                        rbuf = None
                    self.COMM.Igather(sbuf, rbuf, root=root).Wait()
                    for value in buf.flat:
                        self.assertEqual(value, root)

    def testScatter(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for root in range(size):
                    for count in range(1, 10):
                        if rank == root:
                            buf = array(root, typecode, (size, count))
                            sbuf = buf.as_mpi()
                            rbuf = MPI.IN_PLACE
                        else:
                            buf = array(-1, typecode, count)
                            sbuf = None
                            rbuf = buf.as_mpi()
                        self.COMM.Iscatter(sbuf, rbuf, root=root).Wait()
                        for value in buf.flat:
                            self.assertEqual(value, root)

    def testAllgather(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for count in range(1, 10):
                    buf = array(-1, typecode, (size, count))
                    #buf.flat[(rank*count):((rank+1)*count)] = \
                    #    array(count, typecode, count)
                    s, e = rank*count, (rank+1)*count
                    for i in range(s, e): buf.flat[i] = count
                    self.COMM.Iallgather(MPI.IN_PLACE, buf.as_mpi()).Wait()
                    for value in buf.flat:
                        self.assertEqual(value, count)

    def assertAlmostEqual(self, first, second):
        num = float(second-first)
        den = float(second+first)/2 or 1.0
        if (abs(num/den) > 1e-2):
            raise self.failureException('%r != %r' % (first, second))

    def testReduce(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for root in range(size):
                    for op in (MPI.SUM, MPI.PROD, MPI.MAX, MPI.MIN):
                        count = size
                        if rank == root:
                            buf  = array(range(size), typecode)
                            sbuf = MPI.IN_PLACE
                            rbuf = buf.as_mpi()
                        else:
                            buf  = array(range(size), typecode)
                            buf2 = array(range(size), typecode)
                            sbuf = buf.as_mpi()
                            rbuf = buf2.as_mpi()
                        self.COMM.Ireduce(sbuf, rbuf, op, root).Wait()
                        if rank == root:
                            max_val = maxvalue(buf)
                            for i, value in enumerate(buf):
                                if op == MPI.SUM:
                                    if (i * size) < max_val:
                                        self.assertAlmostEqual(value, i*size)
                                elif op == MPI.PROD:
                                    if (i ** size) < max_val:
                                        self.assertAlmostEqual(value, i**size)
                                elif op == MPI.MAX:
                                    self.assertEqual(value, i)
                                elif op == MPI.MIN:
                                    self.assertEqual(value, i)

    def testAllreduce(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for op in (MPI.SUM, MPI.MAX, MPI.MIN, MPI.PROD):
                    buf = array(range(size), typecode)
                    sbuf = MPI.IN_PLACE
                    rbuf = buf.as_mpi()
                    self.COMM.Iallreduce(sbuf, rbuf, op).Wait()
                    max_val = maxvalue(buf)
                    for i, value in enumerate(buf):
                        if op == MPI.SUM:
                            if (i * size) < max_val:
                                self.assertAlmostEqual(value, i*size)
                        elif op == MPI.PROD:
                            if (i ** size) < max_val:
                                self.assertAlmostEqual(value, i**size)
                        elif op == MPI.MAX:
                            self.assertEqual(value, i)
                        elif op == MPI.MIN:
                            self.assertEqual(value, i)

    @unittest.skipMPI('openmpi(<=1.8.6)')
    def testReduceScatterBlock(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for op in (MPI.SUM, MPI.MAX, MPI.MIN, MPI.PROD):
                    for rcnt in range(size):
                        if op == MPI.PROD:
                            rbuf = array([rank+1]*rcnt*size, typecode)
                        else:
                            rbuf = array([rank]*rcnt*size, typecode)
                        self.COMM.Ireduce_scatter_block(MPI.IN_PLACE,
                                                        rbuf.as_mpi(),
                                                        op).Wait()
                        max_val = maxvalue(rbuf)
                        for i, value in enumerate(rbuf):
                            if i >= rcnt:
                                if op == MPI.PROD:
                                    self.assertEqual(value, rank+1)
                                else:
                                    self.assertEqual(value, rank)
                            else:
                                if op == MPI.SUM:
                                    redval = sum(range(size))
                                    if redval < max_val:
                                        self.assertAlmostEqual(value, redval)
                                elif op == MPI.PROD:
                                    redval = prod(range(1,size+1))
                                    if redval < max_val:
                                        self.assertAlmostEqual(value, redval)
                                elif op == MPI.MAX:
                                    self.assertEqual(value, size-1)
                                elif op == MPI.MIN:
                                    self.assertEqual(value, 0)

    @unittest.skipMPI('openmpi(<=1.8.6)')
    def testReduceScatter(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for op in (MPI.SUM, MPI.MAX, MPI.MIN, MPI.PROD):
                    rcnt = list(range(1, size+1))
                    if op == MPI.PROD:
                        rbuf = array([rank+1]*sum(rcnt), typecode)
                    else:
                        rbuf = array([rank]*sum(rcnt), typecode)
                    self.COMM.Ireduce_scatter(MPI.IN_PLACE,
                                              rbuf.as_mpi(),
                                              rcnt, op).Wait()
                    max_val = maxvalue(rbuf)
                    for i, value in enumerate(rbuf):
                        if i >= rcnt[rank]:
                            if op == MPI.PROD:
                                self.assertEqual(value, rank+1)
                            else:
                                self.assertEqual(value, rank)
                        else:
                            if op == MPI.SUM:
                                redval = sum(range(size))
                                if redval < max_val:
                                    self.assertAlmostEqual(value, redval)
                            elif op == MPI.PROD:
                                redval = prod(range(1,size+1))
                                if redval < max_val:
                                    self.assertAlmostEqual(value, redval)
                            elif op == MPI.MAX:
                                self.assertEqual(value, size-1)
                            elif op == MPI.MIN:
                                self.assertEqual(value, 0)


class TestCCOBufSelf(BaseTestCCOBuf, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestCCOBufWorld(BaseTestCCOBuf, unittest.TestCase):
    COMM = MPI.COMM_WORLD

class TestCCOBufInplaceSelf(BaseTestCCOBufInplace, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestCCOBufInplaceWorld(BaseTestCCOBufInplace, unittest.TestCase):
    COMM = MPI.COMM_WORLD
    @unittest.skipMPI('IntelMPI', MPI.COMM_WORLD.Get_size() > 1)
    def testReduceScatter(self):
        super(TestCCOBufInplaceWorld, self).testReduceScatter()

class TestCCOBufSelfDup(TestCCOBufSelf):
    def setUp(self):
        self.COMM = MPI.COMM_SELF.Dup()
    def tearDown(self):
        self.COMM.Free()

class TestCCOBufWorldDup(TestCCOBufWorld):
    def setUp(self):
        self.COMM = MPI.COMM_WORLD.Dup()
    def tearDown(self):
        self.COMM.Free()


try:
    MPI.COMM_SELF.Ibarrier().Wait()
except NotImplementedError:
    unittest.disable(BaseTestCCOBuf, 'mpi-nbc')
    unittest.disable(BaseTestCCOBufInplace, 'mpi-nbc')


if __name__ == '__main__':
    unittest.main()
