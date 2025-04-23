import arrayimpl
import mpiunittest as unittest

from mpi4py import MPI


def maxvalue(a):
    try:
        typecode = a.typecode
    except AttributeError:
        typecode = a.dtype.char
    if typecode == ("f"):
        return 1e30
    elif typecode == ("d"):
        return 1e300
    else:
        return 2 ** (a.itemsize * 7) - 1


@unittest.skipMPI("msmpi(<8.1.0)")
@unittest.skipMPI("openmpi(<2.0.0)")
class BaseTestCCOVec:
    #
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
                    rbuf = array(-1, typecode, size * size)
                    counts = [count] * size
                    displs = list(range(0, size * size, size))
                    recvbuf = rbuf.as_mpi_v(counts, displs)
                    if rank != root:
                        recvbuf = None
                    self.COMM.Igatherv(sbuf.as_mpi(), recvbuf, root).Wait()
                    if recvbuf is not None:
                        for i in range(size):
                            row = rbuf[i * size : (i + 1) * size]
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
                    rbuf = array(-1, typecode, size * size)
                    sendbuf = sbuf.as_mpi_c(count)
                    recvbuf = rbuf.as_mpi_v(count, size)
                    if rank != root:
                        recvbuf = None
                    self.COMM.Igatherv(sendbuf, recvbuf, root).Wait()
                    if recvbuf is not None:
                        for i in range(size):
                            row = rbuf[i * size : (i + 1) * size]
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
                for count in range(size + 1):
                    #
                    sbuf = array(root, typecode, count).as_raw()
                    rbuf = array(-1, typecode, count * size).as_raw()
                    sendbuf = sbuf
                    recvbuf = [rbuf, count]
                    if rank != root:
                        recvbuf = None
                    self.COMM.Igatherv(sendbuf, recvbuf, root).Wait()
                    if recvbuf is not None:
                        for v in rbuf:
                            self.assertEqual(v, check)
                    #
                    sbuf = array(root, typecode, count).as_raw()
                    if rank == root:
                        rbuf = array(-1, typecode, count * size).as_raw()
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
                    sbuf = array(root, typecode, size * size)
                    rbuf = array(-1, typecode, count)
                    counts = [count] * size
                    displs = list(range(0, size * size, size))
                    sendbuf = sbuf.as_mpi_v(counts, displs)
                    if rank != root:
                        sendbuf = None
                    self.COMM.Iscatterv(sendbuf, rbuf.as_mpi(), root).Wait()
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
                    sbuf = array(root, typecode, size * size)
                    rbuf = array(-1, typecode, size)
                    sendbuf = sbuf.as_mpi_v(count, size)
                    recvbuf = rbuf.as_mpi_c(count)
                    if rank != root:
                        sendbuf = None
                    self.COMM.Iscatterv(sendbuf, recvbuf, root).Wait()
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
                for count in range(size + 1):
                    #
                    sbuf = array(root, typecode, count * size).as_raw()
                    rbuf = array(-1, typecode, count).as_raw()
                    sendbuf = [sbuf, count]
                    recvbuf = rbuf
                    if rank != root:
                        sendbuf = None
                    self.COMM.Iscatterv(sendbuf, recvbuf, root).Wait()
                    for v in rbuf:
                        self.assertEqual(v, check)
                    #
                    if rank == root:
                        sbuf = array(root, typecode, count * size).as_raw()
                    else:
                        sbuf = None
                    rbuf = array(-1, typecode, count).as_raw()
                    self.COMM.Scatterv(sbuf, rbuf, root)
                    for v in rbuf:
                        self.assertEqual(v, check)

    def testAllgatherv(self):
        size = self.COMM.Get_size()
        self.COMM.Get_rank()
        for array, typecode in arrayimpl.loop():
            for root in range(size):
                check_a = arrayimpl.scalar(root)
                check_b = arrayimpl.scalar(-1)
                for count in range(size):
                    sbuf = array(root, typecode, count)
                    rbuf = array(-1, typecode, size * size)
                    counts = [count] * size
                    displs = list(range(0, size * size, size))
                    sendbuf = sbuf.as_mpi()
                    recvbuf = rbuf.as_mpi_v(counts, displs)
                    self.COMM.Iallgatherv(sendbuf, recvbuf).Wait()
                    for i in range(size):
                        row = rbuf[i * size : (i + 1) * size]
                        a, b = row[:count], row[count:]
                        for va in a:
                            self.assertEqual(va, check_a)
                        for vb in b:
                            self.assertEqual(vb, check_b)

    def testAllgatherv2(self):
        size = self.COMM.Get_size()
        self.COMM.Get_rank()
        for array, typecode in arrayimpl.loop():
            for root in range(size):
                check_a = arrayimpl.scalar(root)
                check_b = arrayimpl.scalar(-1)
                for count in range(size):
                    sbuf = array(root, typecode, size)
                    rbuf = array(-1, typecode, size * size)
                    sendbuf = sbuf.as_mpi_c(count)
                    recvbuf = rbuf.as_mpi_v(count, size)
                    self.COMM.Iallgatherv(sendbuf, recvbuf).Wait()
                    for i in range(size):
                        row = rbuf[i * size : (i + 1) * size]
                        a, b = row[:count], row[count:]
                        for va in a:
                            self.assertEqual(va, check_a)
                        for vb in b:
                            self.assertEqual(vb, check_b)

    def testAllgatherv3(self):
        size = self.COMM.Get_size()
        self.COMM.Get_rank()
        for array, typecode in arrayimpl.loop():
            for root in range(size):
                check = arrayimpl.scalar(root)
                for count in range(size + 1):
                    #
                    sbuf = array(root, typecode, count).as_raw()
                    rbuf = array(-1, typecode, count * size).as_raw()
                    sendbuf = sbuf
                    recvbuf = [rbuf, count]
                    self.COMM.Iallgatherv(sendbuf, recvbuf).Wait()
                    for v in rbuf:
                        self.assertEqual(v, check)
                    #
                    sbuf = array(root, typecode, count).as_raw()
                    rbuf = array(-1, typecode, count * size).as_raw()
                    self.COMM.Iallgatherv(sbuf, rbuf).Wait()
                    for v in rbuf:
                        self.assertEqual(v, check)

    def testAlltoallv(self):
        size = self.COMM.Get_size()
        self.COMM.Get_rank()
        for array, typecode in arrayimpl.loop():
            for root in range(size):
                check_a = arrayimpl.scalar(root)
                check_b = arrayimpl.scalar(-1)
                for count in range(size):
                    sbuf = array(root, typecode, size * size)
                    rbuf = array(-1, typecode, size * size)
                    counts = [count] * size
                    displs = list(range(0, size * size, size))
                    sendbuf = sbuf.as_mpi_v(counts, displs)
                    recvbuf = rbuf.as_mpi_v(counts, displs)
                    self.COMM.Ialltoallv(sendbuf, recvbuf).Wait()
                    for i in range(size):
                        row = rbuf[i * size : (i + 1) * size]
                        a, b = row[:count], row[count:]
                        for va in a:
                            self.assertEqual(va, check_a)
                        for vb in b:
                            self.assertEqual(vb, check_b)

    def testAlltoallv2(self):
        size = self.COMM.Get_size()
        self.COMM.Get_rank()
        for array, typecode in arrayimpl.loop():
            for root in range(size):
                check_a = arrayimpl.scalar(root)
                check_b = arrayimpl.scalar(-1)
                for count in range(size):
                    sbuf = array(root, typecode, size * size)
                    rbuf = array(-1, typecode, size * size)
                    sendbuf = sbuf.as_mpi_v(count, size)
                    recvbuf = rbuf.as_mpi_v(count, size)
                    self.COMM.Ialltoallv(sendbuf, recvbuf).Wait()
                    for i in range(size):
                        row = rbuf[i * size : (i + 1) * size]
                        a, b = row[:count], row[count:]
                        for va in a:
                            self.assertEqual(va, check_a)
                        for vb in b:
                            self.assertEqual(vb, check_b)

    def testAlltoallv3(self):
        size = self.COMM.Get_size()
        self.COMM.Get_rank()
        for array, typecode in arrayimpl.loop():
            for root in range(size):
                check = arrayimpl.scalar(root)
                for count in range(size + 1):
                    #
                    sbuf = array(root, typecode, count * size).as_raw()
                    rbuf = array(-1, typecode, count * size).as_raw()
                    sendbuf = [sbuf, count]
                    recvbuf = [rbuf, count]
                    self.COMM.Ialltoallv(sendbuf, recvbuf).Wait()
                    for v in rbuf:
                        self.assertEqual(v, check)
                    #
                    sbuf = array(root, typecode, count * size).as_raw()
                    rbuf = array(-1, typecode, count * size).as_raw()
                    self.COMM.Ialltoallv(sbuf, rbuf).Wait()
                    for v in rbuf:
                        self.assertEqual(v, check)

    def testAlltoallw(self):
        size = self.COMM.Get_size()
        self.COMM.Get_rank()
        for array, typecode in arrayimpl.loop():
            for n in range(1, size + 1):
                check = arrayimpl.scalar(n)
                sbuf = array(n, typecode, (size, n))
                rbuf = array(-1, typecode, (size, n))
                sdt, rdt = sbuf.mpidtype, rbuf.mpidtype
                sdsp = list(range(0, size * n * sdt.extent, n * sdt.extent))
                rdsp = list(range(0, size * n * rdt.extent, n * rdt.extent))
                smsg = (sbuf.as_raw(), ([n] * size, sdsp), [sdt] * size)
                rmsg = (rbuf.as_raw(), ([n] * size, rdsp), [rdt] * size)
                try:
                    self.COMM.Ialltoallw(smsg, rmsg).Wait()
                except NotImplementedError:
                    self.skipTest("mpi-alltoallw")
                for value in rbuf.flat:
                    self.assertEqual(value, check)

    @unittest.skipMPI("openmpi(<4.1.7)")
    def testAlltoallwBottom(self):
        size = self.COMM.Get_size()
        self.COMM.Get_rank()
        for array, typecode in arrayimpl.loop():
            for n in range(1, size + 1):
                check = arrayimpl.scalar(n)
                sbuf = array(n, typecode, (size, n))
                rbuf = array(-1, typecode, (size, n))
                saddr = MPI.Get_address(sbuf.as_raw())
                raddr = MPI.Get_address(rbuf.as_raw())
                sdt, rdt = sbuf.mpidtype, rbuf.mpidtype
                stypes = [
                    MPI.Datatype.Create_struct(
                        [n], [saddr + d], [sdt]
                    ).Commit()
                    for d in list(
                        range(0, size * n * sdt.extent, n * sdt.extent)
                    )
                ]
                rtypes = [
                    MPI.Datatype.Create_struct(
                        [n], [raddr + d], [sdt]
                    ).Commit()
                    for d in list(
                        range(0, size * n * rdt.extent, n * rdt.extent)
                    )
                ]
                smsg = (MPI.BOTTOM, ([1] * size, [0] * size), stypes)
                rmsg = (MPI.BOTTOM, ([1] * size, [0] * size), rtypes)
                try:
                    self.COMM.Ialltoallw(smsg, rmsg).Wait()
                except NotImplementedError:
                    self.skipTest("mpi-alltoallw")
                finally:
                    for t in stypes:
                        t.Free()
                    for t in rtypes:
                        t.Free()
                for value in rbuf.flat:
                    self.assertEqual(value, check)


@unittest.skipMPI("msmpi(<8.1.0)")
@unittest.skipMPI("openmpi(<2.0.0)")
class BaseTestCCOVecInplace:
    #
    COMM = MPI.COMM_NULL

    def testAlltoallv(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array, typecode in arrayimpl.loop():
            for count in range(size):
                rbuf = array(-1, typecode, size * size)
                counts = [count] * size
                displs = list(range(0, size * size, size))
                for i in range(size):
                    for j in range(count):
                        rbuf[i * size + j] = rank
                recvbuf = rbuf.as_mpi_v(counts, displs)
                self.COMM.Ialltoallv(MPI.IN_PLACE, recvbuf).Wait()
                for i in range(size):
                    row = rbuf[i * size : (i + 1) * size]
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
                rbuf = array(-1, typecode, size * size)
                for i in range(size):
                    for j in range(count):
                        rbuf[i * size + j] = rank
                rdt = rbuf.mpidtype
                rdsp = list(
                    range(0, size * size * rdt.extent, size * rdt.extent)
                )
                rmsg = (rbuf.as_raw(), ([count] * size, rdsp), [rdt] * size)
                try:
                    self.COMM.Ialltoallw(MPI.IN_PLACE, rmsg).Wait()
                except NotImplementedError:
                    self.skipTest("mpi-ialltoallw")
                for i in range(size):
                    row = rbuf[i * size : (i + 1) * size]
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
                rbuf = array(-1, typecode, size * size)
                for i in range(size):
                    for j in range(count):
                        rbuf[i * size + j] = rank
                rdt = rbuf.mpidtype
                rdsp = list(
                    range(0, size * size * rdt.extent, size * rdt.extent)
                )
                rmsg = (rbuf.as_raw(), [count] * size, rdsp, [rdt] * size)
                try:
                    self.COMM.Ialltoallw(MPI.IN_PLACE, rmsg).Wait()
                except NotImplementedError:
                    self.skipTest("mpi-ialltoallw")
                for i in range(size):
                    row = rbuf[i * size : (i + 1) * size]
                    a, b = row[:count], row[count:]
                    for va in a:
                        check_a = arrayimpl.scalar(i)
                        self.assertEqual(va, check_a)
                    for vb in b:
                        check_b = arrayimpl.scalar(-1)
                        self.assertEqual(vb, check_b)


class TestCCOVecSelf(BaseTestCCOVec, unittest.TestCase):
    #
    COMM = MPI.COMM_SELF


class TestCCOVecWorld(BaseTestCCOVec, unittest.TestCase):
    #
    COMM = MPI.COMM_WORLD


class TestCCOVecSelfDup(TestCCOVecSelf):
    #
    def setUp(self):
        self.COMM = MPI.COMM_SELF.Dup()

    def tearDown(self):
        self.COMM.Free()


class TestCCOVecWorldDup(TestCCOVecWorld):
    #
    def setUp(self):
        self.COMM = MPI.COMM_WORLD.Dup()

    def tearDown(self):
        self.COMM.Free()


class TestCCOVecInplaceSelf(BaseTestCCOVecInplace, unittest.TestCase):
    #
    COMM = MPI.COMM_SELF


class TestCCOVecInplaceWorld(BaseTestCCOVecInplace, unittest.TestCase):
    #
    COMM = MPI.COMM_WORLD


try:
    MPI.COMM_SELF.Ibarrier().Wait()
except NotImplementedError:
    unittest.disable(BaseTestCCOVec, "mpi-nbc")


if __name__ == "__main__":
    unittest.main()
