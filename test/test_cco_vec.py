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


class BaseTestCCOVec(object):

    COMM = MPI.COMM_NULL

    def testGatherv(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for root in range(size):
                    for count in range(size):
                        sbuf = array(root, typecode, count)
                        rbuf = array(  -1, typecode, size*size)
                        counts = [count] * size
                        displs = range(0, size*size, size)
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
                                    self.assertEqual(va, root)
                                for vb in b:
                                    self.assertEqual(vb, -1)

    def testGatherv2(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for root in range(size):
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
                                    self.assertEqual(va, root)
                                for vb in b:
                                    self.assertEqual(vb, -1)


    def testScatterv(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for root in range(size):
                    for count in range(size):
                        #
                        sbuf = array(root, typecode, size*size)
                        rbuf = array(  -1, typecode, count)
                        counts = [count] * size
                        displs = range(0, size*size, size)
                        sendbuf = sbuf.as_mpi_v(counts, displs)
                        if rank != root: sendbuf = None
                        self.COMM.Scatterv(sendbuf, rbuf.as_mpi(), root)
                        for vr in rbuf:
                            self.assertEqual(vr, root)

    def testScatterv2(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for root in range(size):
                    for count in range(size):
                        sbuf = array(root, typecode, size*size)
                        rbuf = array(  -1, typecode, size)
                        sendbuf = sbuf.as_mpi_v(count, size)
                        recvbuf = rbuf.as_mpi_c(count)
                        if rank != root: sendbuf = None
                        self.COMM.Scatterv(sendbuf, recvbuf, root)
                        a, b = rbuf[:count], rbuf[count:]
                        for va in a:
                            self.assertEqual(va, root)
                        for vb in b:
                            self.assertEqual(vb, -1)

    def testAllgatherv(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for root in range(size):
                    for count in range(size):
                        sbuf = array(root, typecode, count)
                        rbuf = array(  -1, typecode, size*size)
                        counts = [count] * size
                        displs = range(0, size*size, size)
                        sendbuf = sbuf.as_mpi()
                        recvbuf = rbuf.as_mpi_v(counts, displs)
                        self.COMM.Allgatherv(sendbuf, recvbuf)
                        for i in range(size):
                            row = rbuf[i*size:(i+1)*size]
                            a, b = row[:count], row[count:]
                            for va in a:
                                self.assertEqual(va, root)
                            for vb in b:
                                self.assertEqual(vb, -1)

    def testAllgatherv2(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for array in arrayimpl.ArrayTypes:
            for typecode in arrayimpl.TypeMap:
                for root in range(size):
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
                                self.assertEqual(va, root)
                            for vb in b:
                                self.assertEqual(vb, -1)


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
                        displs = range(0, size*size, size)
                        sendbuf = sbuf.as_mpi_v(counts, displs)
                        recvbuf = rbuf.as_mpi_v(counts, displs)
                        self.COMM.Alltoallv(sendbuf, recvbuf)
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
                        self.COMM.Alltoallv(sendbuf, recvbuf)
                        for i in range(size):
                            row = rbuf[i*size:(i+1)*size]
                            a, b = row[:count], row[count:]
                            for va in a:
                                self.assertEqual(va, root)
                            for vb in b:
                                self.assertEqual(vb, -1)


class TestCCOVecSelf(BaseTestCCOVec, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestCCOVecWorld(BaseTestCCOVec, unittest.TestCase):
    COMM = MPI.COMM_WORLD

class TestCCOVecSelfDup(BaseTestCCOVec, unittest.TestCase):
    def setUp(self):
        self.COMM = MPI.COMM_SELF.Dup()
    def tearDown(self):
        self.COMM.Free()

class TestCCOVecWorldDup(BaseTestCCOVec, unittest.TestCase):
    def setUp(self):
        self.COMM = MPI.COMM_WORLD.Dup()
    def tearDown(self):
        self.COMM.Free()

_name, _version = MPI.get_vendor()
if _name == 'Open MPI':
    if _version < (1, 4, 0):
        if MPI.Query_thread() > MPI.THREAD_SINGLE:
            del TestCCOVecWorldDup

if __name__ == '__main__':
    unittest.main()
