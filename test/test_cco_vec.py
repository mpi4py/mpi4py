from mpi4py import MPI
import mpiunittest as unittest

typemap = dict(h=MPI.SHORT,
               i=MPI.INT,
               l=MPI.LONG,
               f=MPI.FLOAT,
               d=MPI.DOUBLE)

arrayimpl = []

try:
    import array
    def mk_buf_array_1(a, dt=None, s=1, c=None):
        return (a, (c or len(a))//s, dt or typemap[a.typecode])
    def mk_buf_array_2(a, dt=None, s=1, c=None):
        if c is None: return (a, dt or typemap[a.typecode])
        else:         return (a, c//s, dt or typemap[a.typecode])
    mk_buf_array = (mk_buf_array_1, mk_buf_array_2)
    mk_arr_array = lambda typecode, init: array.array(typecode, init)
    eq_arr_array = lambda a, b : a == b
    arrayimpl.append((mk_buf_array, mk_arr_array, eq_arr_array))
except ImportError:
    pass

try:
    import numpy
    def mk_buf_numpy_1(a, dt=None, s=1, c=None):
        return (a, (c or a.size)//s, dt or typemap[a.dtype.char])
    def mk_buf_numpy_2(a, dt=None, s=1, c=None):
        if c is None: return (a.data, dt or typemap[a.dtype.char])
        else:         return (a.data, (c or a.size)//s, dt or typemap[a.dtype.char])
    mk_buf_numpy = (mk_buf_numpy_1, mk_buf_numpy_2)
    mk_arr_numpy = lambda typecode, init: numpy.array(init, dtype=typecode)
    eq_arr_numpy = lambda a, b : numpy.allclose(a, b)
    arrayimpl.append((mk_buf_numpy, mk_arr_numpy, eq_arr_numpy))
except ImportError:
    pass


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


class TestCCOVecBase(object):

    COMM = MPI.COMM_NULL

    def testGatherv(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for mkbufs, array, equal in arrayimpl:
            #for mkbuf in mkbufs:
                for typecode, datatype in typemap.items():
                    for root in range(size):
                        for count in range(size):
                            sbuf = array(typecode, [root]*(count))
                            rbuf = array(typecode, [  -1]*(size*size))
                            counts = [count] * size
                            displs = range(0, size*size, size)
                            recvbuf = [rbuf, (counts, displs), datatype]
                            if rank != root: recvbuf=None
                            self.COMM.Barrier()
                            self.COMM.Gatherv([sbuf, count, datatype],
                                              recvbuf, root)
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
        for mkbufs, array, equal in arrayimpl:
            #for mkbuf in mkbufs:
                for typecode, datatype in typemap.items():
                    for root in range(size):
                        for count in range(size):
                            sbuf = array(typecode, [root]*(size*size))
                            rbuf = array(typecode, [  -1]*(count))
                            counts = [count] * size
                            displs = range(0, size*size, size)
                            sendbuf = [sbuf, [counts, displs], datatype]
                            if rank != root: sendbuf = None
                            self.COMM.Scatterv(sendbuf,
                                               [rbuf, count, datatype], root)
                            for vr in rbuf:
                                self.assertEqual(vr, root)

    def testAllgatherv(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for mkbufs, array, equal in arrayimpl:
            #for mkbuf in mkbufs:
                for typecode, datatype in typemap.items():
                    for root in range(size):
                        for count in range(size):
                            sbuf = array(typecode, [root]*(count))
                            rbuf = array(typecode, [  -1]*(size*size))
                            counts = [count] * size
                            displs = range(0, size*size, size)
                            sendbuf = [sbuf, count, datatype]
                            recvbuf = (rbuf, counts, displs, datatype)
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
        for mkbufs, array, equal in arrayimpl:
            #for mkbuf in mkbufs:
                for typecode, datatype in typemap.items():
                    for root in range(size):
                        for count in range(size):
                            sarr = array(typecode, [root]*(size*size))
                            rarr = array(typecode, [  -1]*(size*size))
                            counts = [count] * size
                            displs = range(0, size*size, size)
                            sbuf = [sarr, counts, displs, datatype]
                            rbuf = [rarr, counts, displs, datatype]
                            sendbuf = [sarr, counts, displs, datatype]
                            recvbuf = (rarr, counts, displs, datatype)
                            self.COMM.Alltoallv(sendbuf, recvbuf)
                            for i in range(size):
                                row = rarr[i*size:(i+1)*size]
                                a, b = row[:count], row[count:]
                                for va in a:
                                    self.assertEqual(va, root)
                                for vb in b:
                                    self.assertEqual(vb, -1)


class TestCCOVecSelf(TestCCOVecBase, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestCCOVecWorld(TestCCOVecBase, unittest.TestCase):
    COMM = MPI.COMM_WORLD

class TestCCOVecSelfDup(TestCCOVecBase, unittest.TestCase):
    def setUp(self):
        self.COMM = MPI.COMM_SELF.Dup()
    def tearDown(self):
        self.COMM.Free()

class TestCCOVecWorldDup(TestCCOVecBase, unittest.TestCase):
    def setUp(self):
        self.COMM = MPI.COMM_WORLD.Dup()
    def tearDown(self):
        self.COMM.Free()

if __name__ == '__main__':
    unittest.main()
