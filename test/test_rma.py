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
    def mk_buf_array_1(a, dt=None, c=None):
        return (a, c or len(a), dt or typemap[a.typecode])
    def mk_buf_array_2(a, dt=None, c=None):
        if c is None: return (a, dt or typemap[a.typecode])
        else:         return (a, c, dt or typemap[a.typecode])
    mk_buf_array = (mk_buf_array_1, mk_buf_array_2)
    mk_arr_array = lambda typecode, init: array.array(typecode, init)
    eq_arr_array = lambda a, b : a == b
    arrayimpl.append((mk_buf_array, mk_arr_array, eq_arr_array))
except ImportError:
    pass

try:
    import numpy
    def mk_buf_numpy_1(a, dt=None, c=None):
        return (a, c or a.size, dt or typemap[a.dtype.char])
    def mk_buf_numpy_2(a, dt=None, c=None):
        if c is None: return (a.data, dt or typemap[a.dtype.char])
        else:         return (a.data, c or a.size, dt or typemap[a.dtype.char])
    mk_buf_numpy = (mk_buf_numpy_1, mk_buf_numpy_2)
    mk_arr_numpy = lambda typecode, init: numpy.array(init, dtype=typecode)
    eq_arr_numpy = lambda a, b : numpy.allclose(a, b)
    arrayimpl.append((mk_buf_numpy, mk_arr_numpy, eq_arr_numpy))
except ImportError:
    pass

class TestRMABase(object):

    COMM = MPI.COMM_NULL
    INFO = MPI.INFO_NULL

    def setUp(self):
        try:
            zero = str8('\0')
        except NameError:
            zero = str('\0')
        self.memory = MPI.Alloc_mem(100*MPI.DOUBLE.size)
        self.memory[:] = zero * len(self.memory)
        self.WIN = MPI.Win.Create(self.memory, 1,
                                  self.INFO, self.COMM)

    def tearDown(self):
        self.WIN.Free()
        MPI.Free_mem(self.memory)

    def testPutGet(self):
        group = self.WIN.Get_group()
        size = group.Get_size()
        group.Free()
        for mkbufs, array, equal in arrayimpl:
            for mkbuf in mkbufs:
                for typecode, datatype in typemap.items():
                    for count in range(1, 10):
                        for rank in range(size):
                            sbuf = array(typecode, range(count))
                            rbuf = array(typecode, [-1] * (count+1))
                            self.WIN.Fence()
                            self.WIN.Put(mkbuf(sbuf, datatype, count), rank)
                            self.WIN.Fence()
                            self.WIN.Get(mkbuf(rbuf, datatype, count), rank)
                            self.WIN.Fence()
                            for i, value in enumerate(rbuf[:-1]):
                                self.assertEqual(value, i)
                            self.assertEqual(rbuf[-1], -1)

    def testAccumulate(self):
        group = self.WIN.Get_group()
        size = group.Get_size()
        group.Free()
        for mkbufs, array, equal in arrayimpl:
            for mkbuf in mkbufs:
                for typecode, datatype in typemap.items():
                    for count in range(1, 10):
                        for rank in range(size):
                            sbuf = array(typecode, range(count))
                            rbuf = array(typecode, [-1] * (count+1))
                            for op in (MPI.SUM, MPI.PROD, MPI.MAX, MPI.MIN):
                                self.WIN.Fence()
                                self.WIN.Accumulate(mkbuf(sbuf, datatype, count), rank, op=op)
                                self.WIN.Fence()
                                self.WIN.Get(mkbuf(rbuf, datatype, count), rank)
                                self.WIN.Fence()
                                #
                                self.assertEqual(rbuf[-1], -1)
                                for i, value in enumerate(rbuf[:-1]):
                                    self.assertNotEqual(value, -1)


    def testPutProcNull(self):
        self.WIN.Fence()
        self.WIN.Put(None, MPI.PROC_NULL, None)
        self.WIN.Fence()

    def testGetProcNull(self):
        self.WIN.Fence()
        self.WIN.Get(None, MPI.PROC_NULL, None)
        self.WIN.Fence()

    def testAccumulateProcNull(self):
        self.WIN.Fence()
        self.WIN.Accumulate(None, MPI.PROC_NULL, None, MPI.SUM)
        self.WIN.Fence()

    def testFence(self):
        self.WIN.Fence()
        assertion = 0
        modes = [0,
                 MPI.MODE_NOSTORE,
                 MPI.MODE_NOPUT,
                 MPI.MODE_NOPRECEDE,
                 MPI.MODE_NOSUCCEED]
        self.WIN.Fence()
        for mode in modes:
            self.WIN.Fence(mode)
            assertion |= mode
            self.WIN.Fence(assertion)
        self.WIN.Fence()

class TestRMASelf(TestRMABase, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestRMAWorld(TestRMABase, unittest.TestCase):
    COMM = MPI.COMM_WORLD


try:
    w = MPI.Win.Create(None, 1, MPI.INFO_NULL, MPI.COMM_SELF).Free()
except NotImplementedError:
    del TestRMASelf, TestRMAWorld


if __name__ == '__main__':
    unittest.main()
