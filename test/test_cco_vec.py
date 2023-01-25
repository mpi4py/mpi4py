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


class BaseTestCCOVec:

    COMM = MPI.COMM_NULL

    def testGatherv(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array, typecode in arrayimpl.loop():
            for root in range(size):
                check_a = arrayimpl.scalar(root)
                check_b = arrayimpl.scalar(-1)
                for count in range(size):
                    sbuf = array(root, typecode, count)
                    rbuf = array(  -1, typecode, size*size)
                    counts = [count] * size
                    displs = list(range(0, size*size, size))
                    recvbuf = rbuf.as_mpi_v(counts, displs)
                    if rank != root: recvbuf=None
                    self.COMM.Barrier()
                    self.COMM.Gatherv(sbuf.as_mpi(), recvbuf, root)
                    self.COMM.Barrier()
                    if recvbuf is not None:
                        for i in range(size):
                            row = rbuf[i*size:(i+1)*size]
                            a, b = row[:count], row[count:]
                            for va in a:
                                self.assertEqual(va, check_a)
                            for vb in b:
                                self.assertEqual(vb, check_b)

    def testGatherv2(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array, typecode in arrayimpl.loop():
            for root in range(size):
                check_a = arrayimpl.scalar(root)
                check_b = arrayimpl.scalar(-1)
                for count in range(size):
                    sbuf = array(root, typecode, size)
                    rbuf = array(  -1, typecode, size*size)
                    sendbuf = sbuf.as_mpi_c(count)
                    recvbuf = rbuf.as_mpi_v(count, size)
                    if rank != root: recvbuf=None
                    self.COMM.Barrier()
                    self.COMM.Gatherv(sendbuf, recvbuf, root)
                    self.COMM.Barrier()
                    if recvbuf is not None:
                        for i in range(size):
                            row = rbuf[i*size:(i+1)*size]
                            a, b = row[:count], row[count:]
                            for va in a:
                                self.assertEqual(va, check_a)
                            for vb in b:
                                self.assertEqual(vb, check_b)

    def testGatherv3(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array, typecode in arrayimpl.loop():
            for root in range(size):
                check = arrayimpl.scalar(root)
                for count in range(size+1):
                    #
                    sbuf = array(root, typecode, count).as_raw()
                    rbuf = array(  -1, typecode, count*size).as_raw()
                    sendbuf = sbuf
                    recvbuf = [rbuf, count]
                    if rank != root: recvbuf=None
                    self.COMM.Barrier()
                    self.COMM.Gatherv(sendbuf, recvbuf, root)
                    self.COMM.Barrier()
                    if recvbuf is not None:
                        for v in rbuf:
                            self.assertEqual(v, check)
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
                            self.assertEqual(v, check)

    def testScatterv(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array, typecode in arrayimpl.loop():
            for root in range(size):
                check = arrayimpl.scalar(root)
                for count in range(size):
                    sbuf = array(root, typecode, size*size)
                    rbuf = array(  -1, typecode, count)
                    counts = [count] * size
                    displs = list(range(0, size*size, size))
                    sendbuf = sbuf.as_mpi_v(counts, displs)
                    if rank != root: sendbuf = None
                    self.COMM.Scatterv(sendbuf, rbuf.as_mpi(), root)
                    for vr in rbuf:
                        self.assertEqual(vr, check)

    def testScatterv2(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array, typecode in arrayimpl.loop():
            for root in range(size):
                check_a = arrayimpl.scalar(root)
                check_b = arrayimpl.scalar(-1)
                for count in range(size):
                    sbuf = array(root, typecode, size*size)
                    rbuf = array(  -1, typecode, size)
                    sendbuf = sbuf.as_mpi_v(count, size)
                    recvbuf = rbuf.as_mpi_c(count)
                    if rank != root: sendbuf = None
                    self.COMM.Scatterv(sendbuf, recvbuf, root)
                    a, b = rbuf[:count], rbuf[count:]
                    for va in a:
                        self.assertEqual(va, check_a)
                    for vb in b:
                        self.assertEqual(vb, check_b)

    def testScatterv3(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array, typecode in arrayimpl.loop():
            for root in range(size):
                check = arrayimpl.scalar(root)
                for count in range(size+1):
                    #
                    sbuf = array(root, typecode, count*size).as_raw()
                    rbuf = array(  -1, typecode, count).as_raw()
                    sendbuf = [sbuf, count]
                    recvbuf = rbuf
                    if rank != root: sendbuf = None
                    self.COMM.Scatterv(sendbuf, recvbuf, root)
                    for v in rbuf:
                        self.assertEqual(v, check)
                    #
                    if rank == root:
                        sbuf = array(root, typecode, count*size).as_raw()
                    else:
                        sbuf = None
                    rbuf = array(  -1, typecode, count).as_raw()
                    self.COMM.Scatterv(sbuf, rbuf, root)
                    for v in rbuf:
                        self.assertEqual(v, check)

    def testAllgatherv(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array, typecode in arrayimpl.loop():
            for root in range(size):
                check_a = arrayimpl.scalar(root)
                check_b = arrayimpl.scalar(-1)
                for count in range(size):
                    sbuf = array(root, typecode, count)
                    rbuf = array(  -1, typecode, size*size)
                    counts = [count] * size
                    displs = list(range(0, size*size, size))
                    sendbuf = sbuf.as_mpi()
                    recvbuf = rbuf.as_mpi_v(counts, displs)
                    self.COMM.Allgatherv(sendbuf, recvbuf)
                    for i in range(size):
                        row = rbuf[i*size:(i+1)*size]
                        a, b = row[:count], row[count:]
                        for va in a:
                            self.assertEqual(va, check_a)
                        for vb in b:
                            self.assertEqual(vb, check_b)

    def testAllgatherv2(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array, typecode in arrayimpl.loop():
            for root in range(size):
                check_a = arrayimpl.scalar(root)
                check_b = arrayimpl.scalar(-1)
                for count in range(size):
                    sbuf = array(root, typecode, size)
                    rbuf = array(  -1, typecode, size*size)
                    sendbuf = sbuf.as_mpi_c(count)
                    recvbuf = rbuf.as_mpi_v(count, size)
                    self.COMM.Allgatherv(sendbuf, recvbuf)
                    for i in range(size):
                        row = rbuf[i*size:(i+1)*size]
                        a, b = row[:count], row[count:]
                        for va in a:
                            self.assertEqual(va, check_a)
                        for vb in b:
                            self.assertEqual(vb, check_b)

    def testAllgatherv3(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array, typecode in arrayimpl.loop():
            for root in range(size):
                check = arrayimpl.scalar(root)
                for count in range(size+1):
                    #
                    sbuf = array(root, typecode, count).as_raw()
                    rbuf = array(  -1, typecode, count*size).as_raw()
                    sendbuf = sbuf
                    recvbuf = [rbuf, count]
                    self.COMM.Allgatherv(sendbuf, recvbuf)
                    for v in rbuf:
                        self.assertEqual(v, check)
                    #
                    sbuf = array(root, typecode, count).as_raw()
                    rbuf = array(  -1, typecode, count*size).as_raw()
                    self.COMM.Allgatherv(sbuf, rbuf)
                    for v in rbuf:
                        self.assertEqual(v, check)

    def testAlltoallv(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array, typecode in arrayimpl.loop():
            for root in range(size):
                check_a = arrayimpl.scalar(root)
                check_b = arrayimpl.scalar(-1)
                for count in range(size):
                    sbuf = array(root, typecode, size*size)
                    rbuf = array(  -1, typecode, size*size)
                    counts = [count] * size
                    displs = list(range(0, size*size, size))
                    sendbuf = sbuf.as_mpi_v(counts, displs)
                    recvbuf = rbuf.as_mpi_v(counts, displs)
                    self.COMM.Alltoallv(sendbuf, recvbuf)
                    for i in range(size):
                        row = rbuf[i*size:(i+1)*size]
                        a, b = row[:count], row[count:]
                        for va in a:
                            self.assertEqual(va, check_a)
                        for vb in b:
                            self.assertEqual(vb, check_b)

    def testAlltoallv2(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array, typecode in arrayimpl.loop():
            for root in range(size):
                check_a = arrayimpl.scalar(root)
                check_b = arrayimpl.scalar(-1)
                for count in range(size):
                    sbuf = array(root, typecode, size*size)
                    rbuf = array(  -1, typecode, size*size)
                    sendbuf = sbuf.as_mpi_v(count, size)
                    recvbuf = rbuf.as_mpi_v(count, size)
                    self.COMM.Alltoallv(sendbuf, recvbuf)
                    for i in range(size):
                        row = rbuf[i*size:(i+1)*size]
                        a, b = row[:count], row[count:]
                        for va in a:
                            self.assertEqual(va, check_a)
                        for vb in b:
                            self.assertEqual(vb, check_b)

    def testAlltoallv3(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array, typecode in arrayimpl.loop():
            for root in range(size):
                check = arrayimpl.scalar(root)
                for count in range(size+1):
                    #
                    sbuf = array(root, typecode, count*size).as_raw()
                    rbuf = array(  -1, typecode, count*size).as_raw()
                    sendbuf = [sbuf, count]
                    recvbuf = [rbuf, count]
                    self.COMM.Alltoallv(sendbuf, recvbuf)
                    for v in rbuf:
                        self.assertEqual(v, check)
                    #
                    sbuf = array(root, typecode, count*size).as_raw()
                    rbuf = array(  -1, typecode, count*size).as_raw()
                    self.COMM.Alltoallv(sbuf, rbuf)
                    for v in rbuf:
                        self.assertEqual(v, check)

    def testAlltoallw(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array, typecode in arrayimpl.loop():
            for n in range(1, size+1):
                check = arrayimpl.scalar(n)
                sbuf = array( n, typecode, (size, n))
                rbuf = array(-1, typecode, (size, n))
                sdt, rdt = sbuf.mpidtype, rbuf.mpidtype
                sdsp = list(range(0, size*n*sdt.extent, n*sdt.extent))
                rdsp = list(range(0, size*n*rdt.extent, n*rdt.extent))
                smsg = (sbuf.as_raw(), ([n]*size, sdsp), [sdt]*size)
                rmsg = (rbuf.as_raw(), ([n]*size, rdsp), [rdt]*size)
                try:
                    self.COMM.Alltoallw(smsg, rmsg)
                except NotImplementedError:
                    self.skipTest('mpi-alltoallw')
                for value in rbuf.flat:
                    self.assertEqual(value, check)

    def testAlltoallwBottom(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array, typecode in arrayimpl.loop():
            if unittest.is_mpi_gpu('openmpi', array): continue
            for n in range(1, size+1):
                check = arrayimpl.scalar(n)
                sbuf = array( n, typecode, (size, n))
                rbuf = array(-1, typecode, (size, n))
                saddr = MPI.Get_address(sbuf.as_raw())
                raddr = MPI.Get_address(rbuf.as_raw())
                sdt, rdt = sbuf.mpidtype, rbuf.mpidtype
                stypes = [
                    MPI.Datatype.Create_struct([n], [saddr+d], [sdt]).Commit()
                    for d in list(range(0, size*n*sdt.extent, n*sdt.extent))
                ]
                rtypes = [
                    MPI.Datatype.Create_struct([n], [raddr+d], [sdt]).Commit()
                    for d in list(range(0, size*n*rdt.extent, n*rdt.extent))
                ]
                smsg = (MPI.BOTTOM, ([1]*size, [0]*size), stypes)
                rmsg = (MPI.BOTTOM, ([1]*size, [0]*size), rtypes)
                try:
                    self.COMM.Alltoallw(smsg, rmsg)
                except NotImplementedError:
                    self.skipTest('mpi-alltoallw')
                finally:
                    for t in stypes: t.Free()
                    for t in rtypes: t.Free()
                for value in rbuf.flat:
                    self.assertEqual(value, check)

@unittest.skipMPI('msmpi(<8.1.0)')
@unittest.skipMPI('openmpi(<1.8.0)')
@unittest.skipIf(MPI.BOTTOM == MPI.IN_PLACE, 'mpi-in-place')
class BaseTestCCOVecInplace:

    COMM = MPI.COMM_NULL

    def testAlltoallv(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array, typecode in arrayimpl.loop():
            for count in range(size):
                rbuf = array(-1, typecode, size*size)
                counts = [count] * size
                displs = list(range(0, size*size, size))
                for i in range(size):
                    for j in range(count):
                        rbuf[i*size+j] = rank
                recvbuf = rbuf.as_mpi_v(counts, displs)
                self.COMM.Alltoallv(MPI.IN_PLACE, recvbuf)
                for i in range(size):
                    row = rbuf[i*size:(i+1)*size]
                    a, b = row[:count], row[count:]
                    for va in a:
                        check_a = arrayimpl.scalar(i)
                        self.assertEqual(va, check_a)
                    for vb in b:
                        check_b = arrayimpl.scalar(-1)
                        self.assertEqual(vb, check_b)

    def testAlltoallw(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array, typecode in arrayimpl.loop():
            for count in range(size):
                rbuf = array(-1, typecode, size*size)
                for i in range(size):
                    for j in range(count):
                        rbuf[i*size+j] = rank
                rdt = rbuf.mpidtype
                rdsp = list(range(0, size*size*rdt.extent, size*rdt.extent))
                rmsg = (rbuf.as_raw(), ([count]*size, rdsp), [rdt]*size)
                try:
                    self.COMM.Alltoallw(MPI.IN_PLACE, rmsg)
                except NotImplementedError:
                    self.skipTest('mpi-alltoallw')
                for i in range(size):
                    row = rbuf[i*size:(i+1)*size]
                    a, b = row[:count], row[count:]
                    for va in a:
                        check_a = arrayimpl.scalar(i)
                        self.assertEqual(va, check_a)
                    for vb in b:
                        check_b = arrayimpl.scalar(-1)
                        self.assertEqual(vb, check_b)

    def testAlltoallw2(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array, typecode in arrayimpl.loop():
            for count in range(size):
                rbuf = array(-1, typecode, size*size)
                for i in range(size):
                    for j in range(count):
                        rbuf[i*size+j] = rank
                rdt = rbuf.mpidtype
                rdsp = list(range(0, size*size*rdt.extent, size*rdt.extent))
                rmsg = (rbuf.as_raw(), [count]*size, rdsp, [rdt]*size)
                try:
                    self.COMM.Alltoallw(MPI.IN_PLACE, rmsg)
                except NotImplementedError:
                    self.skipTest('mpi-alltoallw')
                for i in range(size):
                    row = rbuf[i*size:(i+1)*size]
                    a, b = row[:count], row[count:]
                    for va in a:
                        check_a = arrayimpl.scalar(i)
                        self.assertEqual(va, check_a)
                    for vb in b:
                        check_b = arrayimpl.scalar(-1)
                        self.assertEqual(vb, check_b)


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

class TestCCOVecInplaceSelf(BaseTestCCOVecInplace, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestCCOVecInplaceWorld(BaseTestCCOVecInplace, unittest.TestCase):
    COMM = MPI.COMM_WORLD


if __name__ == '__main__':
    unittest.main()
