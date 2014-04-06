from mpi4py import MPI
import mpiunittest as unittest

MPI_ERR_OP = MPI.ERR_OP

try:
    import array
except ImportError:
    array = None

try:
    bytes
except NameError:
    bytes = str

if array:
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
            self._test_call(MPI.BXOR,  (x,y), x  ^  y)
        if MPI.REPLACE:
            self._test_call(MPI.REPLACE, (2,3), 3)
            self._test_call(MPI.REPLACE, (3,2), 2)
        if MPI.NO_OP:
            self._test_call(MPI.NO_OP, (2,3), 2)
            self._test_call(MPI.NO_OP, (3,2), 3)

    def testMinMax(self):
        x = [1]; y = [1]
        res = MPI.MIN(x, y)
        self.assertTrue(res is x)
        res = MPI.MAX(x, y)
        self.assertTrue(res is x)

    def testMinMaxLoc(self):
        x = [1]; i = [2]; u = [x, i]
        y = [2]; j = [1]; v = [y, j]
        res = MPI.MINLOC(u, v)
        self.assertTrue(res[0] is x)
        self.assertTrue(res[1] is i)
        res = MPI.MAXLOC(u, v)
        self.assertTrue(res[0] is y)
        self.assertTrue(res[1] is j)
        #
        x = [1]; i = 1; u = [x, i]
        y = [1]; j = 0; v = [y, j]
        res = MPI.MINLOC(u, v)
        self.assertTrue(res[0] is y)
        self.assertTrue(res[1] is j)
        res = MPI.MAXLOC(u, v)
        self.assertTrue(res[0] is y)
        self.assertTrue(res[1] is j)
        #
        x = [1]; i = [1]; u = [x, i]
        y = [1]; j = [0]; v = [y, j]
        res = MPI.MINLOC(u, v)
        self.assertTrue(res[0] is y)
        self.assertTrue(res[1] is j)
        res = MPI.MAXLOC(u, v)
        self.assertTrue(res[0] is y)
        self.assertTrue(res[1] is j)

    def testIsCommutative(self):
        try: MPI.SUM.Is_commutative()
        except NotImplementedError: return
        ops = [MPI.MAX,    MPI.MIN,
               MPI.SUM,    MPI.PROD,
               MPI.LAND,   MPI.BAND,
               MPI.LOR,    MPI.BOR,
               MPI.LXOR,   MPI.BXOR,
               MPI.MAXLOC, MPI.MINLOC,]
        for op in ops:
            flag = op.Is_commutative()
            self.assertEqual(flag, op.is_commutative)
            self.assertTrue(flag)
        ops =  [MPI.REPLACE, MPI.NO_OP]
        for op in ops:
            if not op: continue
            flag = op.Is_commutative()
            self.assertEqual(flag, op.is_commutative)
            #self.assertFalse(flag)

if not array:
    del TestOp.testCreate

if __name__ == '__main__':
    unittest.main()
