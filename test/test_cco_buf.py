from mpi4py import MPI
import mpiunittest as unittest
import arrayimpl

from functools import reduce
prod = lambda sequence,start=1: reduce(lambda x, y: x*y, sequence, start)

def skip_op(typecode, op):
    if typecode in 'FDG':
        if op in (MPI.MAX, MPI.MIN):
            return True
    return False

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


class BaseTestCCOBuf(object):

    COMM = MPI.COMM_NULL

    def testBarrier(self):
        self.COMM.Barrier()

    def testBcast(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array, typecode in arrayimpl.subTest(self):
            for root in range(size):
                if rank == root:
                    buf = array(root, typecode, root)
                else:
                    buf = array(  -1, typecode, root)
                self.COMM.Bcast(buf.as_mpi(), root=root)
                for value in buf:
                    self.assertEqual(value, root)

    def testGather(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array, typecode in arrayimpl.subTest(self):
            for root in range(size):
                sbuf = array(root, typecode, root+1)
                if rank == root:
                    rbuf = array(-1, typecode, (size,root+1))
                else:
                    rbuf = array([], typecode)
                self.COMM.Gather(sbuf.as_mpi(), rbuf.as_mpi(),
                                 root=root)
                if rank == root:
                    for value in rbuf.flat:
                        self.assertEqual(value, root)

    def testScatter(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array, typecode in arrayimpl.subTest(self):
            for root in range(size):
                rbuf = array(-1, typecode, size)
                if rank == root:
                    sbuf = array(root, typecode, (size, size))
                else:
                    sbuf = array([], typecode)
                self.COMM.Scatter(sbuf.as_mpi(), rbuf.as_mpi(),
                                  root=root)
                for value in rbuf:
                    self.assertEqual(value, root)

    def testAllgather(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array, typecode in arrayimpl.subTest(self):
            for root in range(size):
                sbuf = array(root, typecode, root+1)
                rbuf = array(  -1, typecode, (size, root+1))
                self.COMM.Allgather(sbuf.as_mpi(), rbuf.as_mpi())
                for value in rbuf.flat:
                    self.assertEqual(value, root)

    def testAlltoall(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array, typecode in arrayimpl.subTest(self):
            for root in range(size):
                sbuf = array(root, typecode, (size, root+1))
                rbuf = array(  -1, typecode, (size, root+1))
                self.COMM.Alltoall(sbuf.as_mpi(), rbuf.as_mpi_c(root+1))
                for value in rbuf.flat:
                    self.assertEqual(value, root)

    def assertAlmostEqual(self, first, second):
        num = complex(second-first)
        den = complex(second+first)/2 or 1.0
        if (abs(num/den) > 1e-2):
            raise self.failureException('%r != %r' % (first, second))

    def testReduce(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array, typecode in arrayimpl.subTest(self):
            for op in (MPI.SUM, MPI.PROD, MPI.MAX, MPI.MIN):
                if skip_op(typecode, op): continue
                for root in range(size):
                    sbuf = array(range(size), typecode)
                    rbuf = array(-1, typecode, size)
                    self.COMM.Reduce(sbuf.as_mpi(),
                                     rbuf.as_mpi(),
                                     op, root)
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
        for array, typecode in arrayimpl.subTest(self):
            for op in (MPI.SUM, MPI.MAX, MPI.MIN, MPI.PROD):
                if skip_op(typecode, op): continue
                sbuf = array(range(size), typecode)
                rbuf = array(0, typecode, size)
                self.COMM.Allreduce(sbuf.as_mpi(),
                                    rbuf.as_mpi(),
                                    op)
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

    def testReduceScatter(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array, typecode in arrayimpl.subTest(self):
            for op in (MPI.SUM, MPI.MAX, MPI.MIN, MPI.PROD):
                if skip_op(typecode, op): continue
                rcnt = list(range(1,size+1))
                sbuf = array([rank+1]*sum(rcnt), typecode)
                rbuf = array(-1, typecode, rank+1)
                self.COMM.Reduce_scatter(sbuf.as_mpi(),
                                         rbuf.as_mpi(),
                                         None, op)
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
                self.COMM.Reduce_scatter(sbuf.as_mpi(),
                                         rbuf.as_mpi(),
                                         rcnt, op)
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
        for array, typecode in arrayimpl.subTest(self):
            for op in (MPI.SUM, MPI.MAX, MPI.MIN, MPI.PROD):
                if skip_op(typecode, op): continue
                for rcnt in range(1,size):
                    sbuf = array([rank]*rcnt*size, typecode)
                    rbuf = array(-1, typecode, rcnt)
                    if op == MPI.PROD:
                        sbuf = array([rank+1]*rcnt*size, typecode)
                    self.COMM.Reduce_scatter_block(sbuf.as_mpi(),
                                                   rbuf.as_mpi(),
                                                   op)
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
        for array, typecode in arrayimpl.subTest(self):
            for op in (MPI.SUM, MPI.PROD, MPI.MAX, MPI.MIN):
                if skip_op(typecode, op): continue
                sbuf = array(range(size), typecode)
                rbuf = array(0, typecode, size)
                self.COMM.Scan(sbuf.as_mpi(),
                               rbuf.as_mpi(),
                               op)
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

    def testExscan(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array, typecode in arrayimpl.subTest(self):
            for op in (MPI.SUM, MPI.PROD, MPI.MAX, MPI.MIN):
                if skip_op(typecode, op): continue
                sbuf = array(range(size), typecode)
                rbuf = array(0, typecode, size)
                try:
                    self.COMM.Exscan(sbuf.as_mpi(),
                                     rbuf.as_mpi(),
                                     op)
                except NotImplementedError:
                    self.skipTest('mpi-exscan')
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
        for array, typecode in arrayimpl.subTest(self):
            datatype = array.TypeMap[typecode]
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
                self.COMM.Bcast(newbuf, root=root)
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
                self.COMM.Bcast(newbuf, root)
                newtype.Free()
                if rank != root:
                    for i, value in enumerate(buf):
                        if not (i % 2):
                            self.assertEqual(value, -1)
                        else:
                            self.assertEqual(value, i)


class BaseTestCCOBufInplace(object):

    def testGather(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array, typecode in arrayimpl.subTest(self):
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
                self.COMM.Gather(sbuf, rbuf, root=root)
                for value in buf.flat:
                    self.assertEqual(value, root)

    @unittest.skipMPI('msmpi(==10.0.0)')
    def testScatter(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array, typecode in arrayimpl.subTest(self):
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
                    self.COMM.Scatter(sbuf, rbuf, root=root)
                    for value in buf.flat:
                        self.assertEqual(value, root)

    def testAllgather(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array, typecode in arrayimpl.subTest(self):
            for count in range(1, 10):
                buf = array(-1, typecode, (size, count))
                #buf.flat[(rank*count):((rank+1)*count)] = \
                #    array(count, typecode, count)
                s, e = rank*count, (rank+1)*count
                for i in range(s, e): buf.flat[i] = count
                self.COMM.Allgather(MPI.IN_PLACE, buf.as_mpi())
                for value in buf.flat:
                    self.assertEqual(value, count)

    def assertAlmostEqual(self, first, second):
        num = complex(second-first)
        den = complex(second+first)/2 or 1.0
        if (abs(num/den) > 1e-2):
            raise self.failureException('%r != %r' % (first, second))

    def testReduce(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array, typecode in arrayimpl.subTest(self):
            for op in (MPI.SUM, MPI.PROD, MPI.MAX, MPI.MIN):
                if skip_op(typecode, op): continue
                for root in range(size):
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
                    self.COMM.Reduce(sbuf, rbuf, op, root)
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
        for array, typecode in arrayimpl.subTest(self):
            for op in (MPI.SUM, MPI.MAX, MPI.MIN, MPI.PROD):
                if skip_op(typecode, op): continue
                buf = array(range(size), typecode)
                sbuf = MPI.IN_PLACE
                rbuf = buf.as_mpi()
                self.COMM.Allreduce(sbuf, rbuf, op)
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

    def testReduceScatterBlock(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array, typecode in arrayimpl.subTest(self):
            # one of the ranks would fail as of OpenMPI 4.1.1
            if unittest.is_mpi_gpu('openmpi', array): continue
            for op in (MPI.SUM, MPI.MAX, MPI.MIN, MPI.PROD):
                if skip_op(typecode, op): continue
                for rcnt in range(size):
                    if op == MPI.PROD:
                        rbuf = array([rank+1]*rcnt*size, typecode)
                    else:
                        rbuf = array([rank]*rcnt*size, typecode)
                    self.COMM.Reduce_scatter_block(MPI.IN_PLACE,
                                                   rbuf.as_mpi(),
                                                   op)
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

    @unittest.skipMPI('MVAPICH2')
    def testReduceScatter(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array, typecode in arrayimpl.subTest(self):
            for op in (MPI.SUM, MPI.MAX, MPI.MIN, MPI.PROD):
                if skip_op(typecode, op): continue
                rcnt = list(range(1, size+1))
                if op == MPI.PROD:
                    rbuf = array([rank+1]*sum(rcnt), typecode)
                else:
                    rbuf = array([rank]*sum(rcnt), typecode)
                self.COMM.Reduce_scatter(MPI.IN_PLACE,
                                         rbuf.as_mpi(),
                                         rcnt, op)
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

    @unittest.skipMPI('openmpi(<=1.8.4)')
    def testScan(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        # --
        for array, typecode in arrayimpl.subTest(self):
            for op in (MPI.SUM, MPI.PROD, MPI.MAX, MPI.MIN):
                if skip_op(typecode, op): continue
                buf = array(range(size), typecode)
                self.COMM.Scan(MPI.IN_PLACE,
                               buf.as_mpi(),
                               op)
                max_val = maxvalue(buf)
                for i, value in enumerate(buf):
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

    @unittest.skipMPI('msmpi(<=4.2.0)')
    @unittest.skipMPI('openmpi(<=1.8.4)')
    def testExscan(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array, typecode in arrayimpl.subTest(self):
            for op in (MPI.SUM, MPI.PROD, MPI.MAX, MPI.MIN):
                if skip_op(typecode, op): continue
                buf = array(range(size), typecode)
                try:
                    self.COMM.Exscan(MPI.IN_PLACE,
                                     buf.as_mpi(),
                                     op)
                except NotImplementedError:
                    self.skipTest('mpi-exscan')
                if rank == 1:
                    for i, value in enumerate(buf):
                        self.assertEqual(value, i)
                elif rank > 1:
                    max_val = maxvalue(buf)
                    for i, value in enumerate(buf):
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

class TestReduceLocal(unittest.TestCase):

    def testReduceLocal(self):
        for array, typecode in arrayimpl.subTest(self):
            # segfault as of OpenMPI 4.1.1
            if unittest.is_mpi_gpu('openmpi', array): continue
            for op in (MPI.SUM, MPI.PROD, MPI.MAX, MPI.MIN):
                if skip_op(typecode, op): continue
                size = 5
                sbuf = array(range(1,size+1), typecode)
                rbuf = array(range(0,size+0), typecode)
                try:
                    op.Reduce_local(sbuf.as_mpi(), rbuf.as_mpi())
                except NotImplementedError:
                    self.skipTest('mpi-op-reduce_local')
                for i, value in enumerate(rbuf):
                    self.assertEqual(sbuf[i], i+1)
                    if op == MPI.SUM:
                        self.assertAlmostEqual(value, i+(i+1))
                    elif op == MPI.PROD:
                        self.assertAlmostEqual(value, i*(i+1))
                    elif op == MPI.MAX:
                        self.assertEqual(value, i+1)
                    elif op == MPI.MIN:
                        self.assertEqual(value, i)

    def testReduceLocalBadCount(self):
        for array, typecode in arrayimpl.subTest(self):
            for op in (MPI.SUM, MPI.PROD, MPI.MAX, MPI.MIN):
                sbuf = array(range(3), typecode)
                rbuf = array(range(3), typecode)
                def f(): op.Reduce_local(sbuf.as_mpi_c(2),
                                         rbuf.as_mpi_c(3))
                self.assertRaises(ValueError, f)
                def f(): op.Reduce_local([sbuf.as_raw(), 1, MPI.INT],
                                         [rbuf.as_raw(), 1, MPI.SHORT])
                self.assertRaises(ValueError, f)


class TestCCOBufSelf(BaseTestCCOBuf, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestCCOBufWorld(BaseTestCCOBuf, unittest.TestCase):
    COMM = MPI.COMM_WORLD

@unittest.skipMPI('MPICH1')
@unittest.skipMPI('LAM/MPI')
@unittest.skipIf(MPI.IN_PLACE == MPI.BOTTOM, 'mpi-in-place')
class TestCCOBufInplaceSelf(BaseTestCCOBufInplace, unittest.TestCase):
    COMM = MPI.COMM_SELF

@unittest.skipMPI('MPICH1')
@unittest.skipMPI('LAM/MPI')
@unittest.skipIf(MPI.IN_PLACE == MPI.BOTTOM, 'mpi-in-place')
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

@unittest.skipMPI('openmpi(<1.4.0)', MPI.Query_thread() > MPI.THREAD_SINGLE)
class TestCCOBufWorldDup(TestCCOBufWorld):
    def setUp(self):
        self.COMM = MPI.COMM_WORLD.Dup()
    def tearDown(self):
        self.COMM.Free()


if __name__ == '__main__':
    unittest.main()
