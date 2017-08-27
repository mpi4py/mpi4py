from mpi4py import MPI
import mpiunittest as unittest
import arrayimpl


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
class BaseTestCCOVec(object):

    COMM = MPI.COMM_NULL

    skip = []

    @unittest.skipMPI('openmpi(==1.10.1)')
    def testGatherv(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for root in range(size):
                    for count in range(size):
                        if (count, '*') in self.skip: continue
                        if (count, typecode) in self.skip: continue
                        sbuf = array(root, typecode, count)
                        rbuf = array(  -1, typecode, size*size)
                        counts = [count] * size
                        displs = list(range(0, size*size, size))
                        recvbuf = rbuf.as_mpi_v(counts, displs)
                        if rank != root: recvbuf=None
                        self.COMM.Igatherv(sbuf.as_mpi(), recvbuf, root).Wait()
                        if recvbuf is not None:
                            for i in range(size):
                                row = rbuf[i*size:(i+1)*size]
                                a, b = row[:count], row[count:]
                                for va in a:
                                    self.assertEqual(va, root)
                                for vb in b:
                                    self.assertEqual(vb, -1)

    @unittest.skipMPI('openmpi(==1.10.1)')
    def testGatherv2(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for root in range(size):
                    for count in range(size):
                        if (count, '*') in self.skip: continue
                        if (count, typecode) in self.skip: continue
                        sbuf = array(root, typecode, size)
                        rbuf = array(  -1, typecode, size*size)
                        sendbuf = sbuf.as_mpi_c(count)
                        recvbuf = rbuf.as_mpi_v(count, size)
                        if rank != root: recvbuf=None
                        self.COMM.Igatherv(sendbuf, recvbuf, root).Wait()
                        if recvbuf is not None:
                            for i in range(size):
                                row = rbuf[i*size:(i+1)*size]
                                a, b = row[:count], row[count:]
                                for va in a:
                                    self.assertEqual(va, root)
                                for vb in b:
                                    self.assertEqual(vb, -1)

    @unittest.skipMPI('openmpi(==1.10.1)')
    def testGatherv3(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for root in range(size):
                    for count in range(size+1):
                        if (count, '*') in self.skip: continue
                        if (count, typecode) in self.skip: continue
                        #
                        sbuf = array(root, typecode, count).as_raw()
                        rbuf = array(  -1, typecode, count*size).as_raw()
                        sendbuf = sbuf
                        recvbuf = [rbuf, count]
                        if rank != root: recvbuf=None
                        self.COMM.Igatherv(sendbuf, recvbuf, root).Wait()
                        if recvbuf is not None:
                            for v in rbuf:
                                self.assertEqual(v, root)
                        #
                        sbuf = array(root, typecode, count).as_raw()
                        if rank == root:
                            rbuf = array(  -1, typecode, count*size).as_raw()
                        else:
                            rbuf = None
                        self.COMM.Gatherv(sbuf, rbuf, root)
                        self.COMM.Barrier()
                        if rank == root:
                            for v in rbuf:
                                self.assertEqual(v, root)

    @unittest.skipMPI('openmpi(==1.10.1)')
    def testScatterv(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for root in range(size):
                    for count in range(size):
                        if (count, '*') in self.skip: continue
                        if (count, typecode) in self.skip: continue
                        sbuf = array(root, typecode, size*size)
                        rbuf = array(  -1, typecode, count)
                        counts = [count] * size
                        displs = list(range(0, size*size, size))
                        sendbuf = sbuf.as_mpi_v(counts, displs)
                        if rank != root: sendbuf = None
                        self.COMM.Iscatterv(sendbuf, rbuf.as_mpi(), root).Wait()
                        for vr in rbuf:
                            self.assertEqual(vr, root)

    @unittest.skipMPI('openmpi(==1.10.1)')
    def testScatterv2(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for root in range(size):
                    for count in range(size):
                        if (count, '*') in self.skip: continue
                        if (count, typecode) in self.skip: continue
                        sbuf = array(root, typecode, size*size)
                        rbuf = array(  -1, typecode, size)
                        sendbuf = sbuf.as_mpi_v(count, size)
                        recvbuf = rbuf.as_mpi_c(count)
                        if rank != root: sendbuf = None
                        self.COMM.Iscatterv(sendbuf, recvbuf, root).Wait()
                        a, b = rbuf[:count], rbuf[count:]
                        for va in a:
                            self.assertEqual(va, root)
                        for vb in b:
                            self.assertEqual(vb, -1)

    @unittest.skipMPI('openmpi(==1.10.1)')
    def testScatterv3(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for root in range(size):
                    for count in range(size+1):
                        if (count, '*') in self.skip: continue
                        if (count, typecode) in self.skip: continue
                        #
                        sbuf = array(root, typecode, count*size).as_raw()
                        rbuf = array(  -1, typecode, count).as_raw()
                        sendbuf = [sbuf, count]
                        recvbuf = rbuf
                        if rank != root: sendbuf = None
                        self.COMM.Iscatterv(sendbuf, recvbuf, root).Wait()
                        for v in rbuf:
                            self.assertEqual(v, root)
                        #
                        if rank == root:
                            sbuf = array(root, typecode, count*size).as_raw()
                        else:
                            sbuf = None
                        rbuf = array(  -1, typecode, count).as_raw()
                        self.COMM.Scatterv(sbuf, rbuf, root)
                        for v in rbuf:
                            self.assertEqual(v, root)

    @unittest.skipMPI('openmpi(==1.10.1)')
    def testAllgatherv(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for root in range(size):
                    for count in range(size):
                        if (count, '*') in self.skip: continue
                        if (count, typecode) in self.skip: continue
                        sbuf = array(root, typecode, count)
                        rbuf = array(  -1, typecode, size*size)
                        counts = [count] * size
                        displs = list(range(0, size*size, size))
                        sendbuf = sbuf.as_mpi()
                        recvbuf = rbuf.as_mpi_v(counts, displs)
                        self.COMM.Iallgatherv(sendbuf, recvbuf).Wait()
                        for i in range(size):
                            row = rbuf[i*size:(i+1)*size]
                            a, b = row[:count], row[count:]
                            for va in a:
                                self.assertEqual(va, root)
                            for vb in b:
                                self.assertEqual(vb, -1)

    @unittest.skipMPI('openmpi(==1.10.1)')
    def testAllgatherv2(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for root in range(size):
                    for count in range(size):
                        if (count, '*') in self.skip: continue
                        if (count, typecode) in self.skip: continue
                        sbuf = array(root, typecode, size)
                        rbuf = array(  -1, typecode, size*size)
                        sendbuf = sbuf.as_mpi_c(count)
                        recvbuf = rbuf.as_mpi_v(count, size)
                        self.COMM.Iallgatherv(sendbuf, recvbuf).Wait()
                        for i in range(size):
                            row = rbuf[i*size:(i+1)*size]
                            a, b = row[:count], row[count:]
                            for va in a:
                                self.assertEqual(va, root)
                            for vb in b:
                                self.assertEqual(vb, -1)

    @unittest.skipMPI('openmpi(==1.10.1)')
    def testAllgatherv3(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for root in range(size):
                    for count in range(size+1):
                        if (count, '*') in self.skip: continue
                        if (count, typecode) in self.skip: continue
                        #
                        sbuf = array(root, typecode, count).as_raw()
                        rbuf = array(  -1, typecode, count*size).as_raw()
                        sendbuf = sbuf
                        recvbuf = [rbuf, count]
                        self.COMM.Iallgatherv(sendbuf, recvbuf).Wait()
                        for v in rbuf:
                            self.assertEqual(v, root)
                        #
                        sbuf = array(root, typecode, count).as_raw()
                        rbuf = array(  -1, typecode, count*size).as_raw()
                        self.COMM.Iallgatherv(sbuf, rbuf).Wait()
                        for v in rbuf:
                            self.assertEqual(v, root)

    def testAlltoallv(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for root in range(size):
                    for count in range(size):
                        sbuf = array(root, typecode, size*size)
                        rbuf = array(  -1, typecode, size*size)
                        counts = [count] * size
                        displs = list(range(0, size*size, size))
                        sendbuf = sbuf.as_mpi_v(counts, displs)
                        recvbuf = rbuf.as_mpi_v(counts, displs)
                        self.COMM.Ialltoallv(sendbuf, recvbuf).Wait()
                        for i in range(size):
                            row = rbuf[i*size:(i+1)*size]
                            a, b = row[:count], row[count:]
                            for va in a:
                                self.assertEqual(va, root)
                            for vb in b:
                                self.assertEqual(vb, -1)

    def testAlltoallv2(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for root in range(size):
                    for count in range(size):
                        sbuf = array(root, typecode, size*size)
                        rbuf = array(  -1, typecode, size*size)
                        sendbuf = sbuf.as_mpi_v(count, size)
                        recvbuf = rbuf.as_mpi_v(count, size)
                        self.COMM.Ialltoallv(sendbuf, recvbuf).Wait()
                        for i in range(size):
                            row = rbuf[i*size:(i+1)*size]
                            a, b = row[:count], row[count:]
                            for va in a:
                                self.assertEqual(va, root)
                            for vb in b:
                                self.assertEqual(vb, -1)

    def testAlltoallv3(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for root in range(size):
                    for count in range(size+1):
                        #
                        sbuf = array(root, typecode, count*size).as_raw()
                        rbuf = array(  -1, typecode, count*size).as_raw()
                        sendbuf = [sbuf, count]
                        recvbuf = [rbuf, count]
                        self.COMM.Ialltoallv(sendbuf, recvbuf).Wait()
                        for v in rbuf:
                            self.assertEqual(v, root)
                        #
                        sbuf = array(root, typecode, count*size).as_raw()
                        rbuf = array(  -1, typecode, count*size).as_raw()
                        self.COMM.Ialltoallv(sbuf, rbuf).Wait()
                        for v in rbuf:
                            self.assertEqual(v, root)

    @unittest.skipMPI('openmpi(<=1.8.0)')
    def testAlltoallw(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for n in range(1, size+1):
                    sbuf = array( n, typecode, (size, n))
                    rbuf = array(-1, typecode, (size, n))
                    sdt, rdt = sbuf.mpidtype, rbuf.mpidtype
                    sdsp = list(range(0, size*n*sdt.extent, n*sdt.extent))
                    rdsp = list(range(0, size*n*rdt.extent, n*rdt.extent))
                    smsg = (sbuf.as_raw(), ([n]*size, sdsp), [sdt]*size)
                    rmsg = (rbuf.as_raw(), ([n]*size, rdsp), [rdt]*size)
                    try:
                        self.COMM.Ialltoallw(smsg, rmsg).Wait()
                    except NotImplementedError:
                        self.skipTest('mpi-ialltoallw')
                    for v in rbuf.flat:
                        self.assertEqual(v, n)


class TestCCOVecSelf(BaseTestCCOVec, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestCCOVecWorld(BaseTestCCOVec, unittest.TestCase):
    COMM = MPI.COMM_WORLD

class TestCCOVecSelfDup(TestCCOVecSelf):
    def setUp(self):
        self.COMM = MPI.COMM_SELF.Dup()
    def tearDown(self):
        self.COMM.Free()

class TestCCOVecWorldDup(TestCCOVecWorld):
    def setUp(self):
        self.COMM = MPI.COMM_WORLD.Dup()
    def tearDown(self):
        self.COMM.Free()


name, version = MPI.get_vendor()
if name == 'Open MPI':
    if version == (1,10,0):
        BaseTestCCOVec.skip += [(0, '*')]
    if version == (1,8,6):
        BaseTestCCOVec.skip += [(0, 'b')]
try:
    MPI.COMM_SELF.Ibarrier().Wait()
except NotImplementedError:
    unittest.disable(BaseTestCCOVec, 'mpi-nbc')


if __name__ == '__main__':
    unittest.main()
