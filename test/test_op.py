from mpi4py import MPI
import mpiunittest as unittest
import array

MPI_ERR_OP = MPI.ERR_OP

try:
    bytes
except NameError:
    bytes = str

try:
    tobytes = array.array.tobytes
except AttributeError:
    tobytes = array.array.tostring

def frombytes(typecode, data):
    a = array.array(typecode,[])
    try:
        data = data.tobytes()
    except AttributeError:
        pass
    try:
        _frombytes = array.array.frombytes
    except AttributeError:
        _frombytes = array.array.fromstring
    _frombytes(a, data)
    return a

def mysum_py(a, b):
    for i in range(len(a)):
        b[i] = a[i] + b[i]
    return b

def mysum(ba, bb, dt):
    if dt is None:
        return mysum_py(ba, bb)
    assert dt == MPI.INT
    assert len(ba) == len(bb)
    a = frombytes('i', ba)
    b = frombytes('i', bb)
    b = mysum_py(a, b)
    bb[:] = tobytes(b)

class TestOp(unittest.TestCase):

    def testConstructor(self):
        op = MPI.Op()
        self.assertFalse(op)
        self.assertEqual(op, MPI.OP_NULL)

    def testCreate(self):
        for comm in [MPI.COMM_SELF, MPI.COMM_WORLD]:
            for commute in [True, False]:
                for N in range(4):
                    # buffer(empty_array) returns
                    # the same non-NULL pointer !!!
                    if N == 0: continue
                    size = comm.Get_size()
                    rank = comm.Get_rank()
                    myop = MPI.Op.Create(mysum, commute)
                    a = array.array('i', [i*(rank+1) for i in range(N)])
                    b = array.array('i', [0]*len(a))
                    comm.Allreduce([a, MPI.INT], [b, MPI.INT], myop)
                    scale = sum(range(1,size+1))
                    for i in range(N):
                        self.assertEqual(b[i], scale*i)
                    ret = myop(a, b)
                    self.assertTrue(ret is b)
                    for i in range(N):
                        self.assertEqual(b[i], a[i]+scale*i)
                    myop.Free()

    def testCreateMany(self):
        N = 16 # max user-defined operations
        #
        ops = []
        for i in range(N):
            o = MPI.Op.Create(mysum)
            ops.append(o)
        self.assertRaises(RuntimeError, MPI.Op.Create, mysum)
        for o in ops: o.Free() # cleanup
        # other round
        ops = []
        for i in range(N):
            o = MPI.Op.Create(mysum)
            ops.append(o)
        self.assertRaises(RuntimeError, MPI.Op.Create, mysum)
        for o in ops: o.Free() # cleanup

    def _test_call(self, op, args, res):
        self.assertEqual(op(*args), res)

    def testCall(self):
        self._test_call(MPI.MIN,  (2,3), 2)
        self._test_call(MPI.MAX,  (2,3), 3)
        self._test_call(MPI.SUM,  (2,3), 5)
        self._test_call(MPI.PROD, (2,3), 6)
        def xor(x,y): return bool(x) ^ bool(y)
        for x, y in ((0, 0),
                     (0, 1),
                     (1, 0),
                     (1, 1)):
            self._test_call(MPI.LAND,  (x,y), x and y)
            self._test_call(MPI.LOR,   (x,y), x or  y)
            self._test_call(MPI.LXOR,  (x,y), xor(x, y))
            self._test_call(MPI.BAND,  (x,y), x  &  y)
            self._test_call(MPI.BOR,   (x,y), x  |  y)
            self._test_call(MPI.LXOR,  (x,y), x  ^  y)
        if MPI.REPLACE:
            self._test_call(MPI.REPLACE, (2,3), 2)
            self._test_call(MPI.REPLACE, (3,2), 3)

if __name__ == '__main__':
    unittest.main()
