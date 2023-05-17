from mpi4py import MPI
import mpiunittest as unittest

try:
    import array
except ImportError:
    array = None

def asarray(typecode, data):
    tobytes = lambda s: memoryview(s).tobytes()
    frombytes = array.array.frombytes
    a = array.array(typecode, [])
    frombytes(a, tobytes(data))
    return a

def mysum_obj(a, b):
    for i in range(len(a)):
        b[i] = a[i] + b[i]
    return b

def mysum_buf(a, b, dt):
    assert dt == MPI.INT
    assert len(a) == len(b)
    b[:] = mysum_obj(asarray('i', a), asarray('i', b))

def mysum(ba, bb, dt):
    if dt is None:
        return mysum_obj(ba, bb)
    else:
        return mysum_buf(ba, bb, dt)

def mybor(a, b, dt):
    assert dt == MPI.BYTE
    assert len(a) == len(b)
    for i in range(len(a)):
        b[i] = a[i] | b[i]


class TestOp(unittest.TestCase):

    def testConstructor(self):
        op = MPI.Op()
        self.assertFalse(op)
        self.assertEqual(op, MPI.OP_NULL)

    @unittest.skipIf(array is None, 'array')
    def testCreate(self):
        for comm in [MPI.COMM_SELF, MPI.COMM_WORLD]:
            for commute in [True, False]:
                for N in range(4):
                    myop = MPI.Op.Create(mysum, commute)
                    self.assertFalse(myop.is_predefined)
                    try:
                        size = comm.Get_size()
                        rank = comm.Get_rank()
                        a = array.array('i', [i*(rank+1) for i in range(N)])
                        b = array.array('i', [0]*len(a))
                        comm.Allreduce([a, MPI.INT], [b, MPI.INT], myop)
                        scale = sum(range(1,size+1))
                        for i in range(N):
                            self.assertEqual(b[i], scale*i)
                        res = myop(a, b)
                        self.assertIs(res, b)
                        for i in range(N):
                            self.assertEqual(b[i], a[i]+scale*i)
                        myop2 = MPI.Op(myop)
                        a = array.array('i', [1]*N)
                        b = array.array('i', [2]*N)
                        res = myop2(a, b)
                        self.assertIs(res, b)
                        for i in range(N):
                            self.assertEqual(b[i], 3)
                        myop2 = None
                    finally:
                        myop.Free()

    def testCreateMany(self):
        MAX_USER_OP = 32 # max user-defined operations
        # create
        ops = []
        for i in range(MAX_USER_OP):
            o = MPI.Op.Create(mysum)
            ops.append(o)
        with self.assertRaises(RuntimeError):
            MPI.Op.Create(mysum)
        # cleanup
        for o in ops:
            o.Free()
        # another round
        ops = []
        for i in range(MAX_USER_OP):
            op = MPI.Op.Create(mybor)
            ops.append(op)
        with self.assertRaises(RuntimeError):
            MPI.Op.Create(mybor)
        # local reductions
        try:
            b1 = bytearray([2] * 3)
            b2 = bytearray([4] * 3)
            for op in ops:
                ibuf = [b1, MPI.BYTE]
                obuf = [b2, MPI.BYTE]
                op.Reduce_local(ibuf, obuf)
                for c1, c2 in zip(b1, b2):
                    self.assertEqual(c1, 2)
                    self.assertEqual(c2, 6)
        except NotImplementedError:
            pass
        # pickling support
        try:
            for op in ops:
                op.__reduce__()
                clon = MPI.Op.f2py(op.py2f())
                with self.assertRaises(ValueError):
                    clon.__reduce__()
        except NotImplementedError:
            pass
        # cleanup
        for op in ops:
            op.Free()

    def _test_call(self, op, args, res):
        self.assertEqual(op(*args), res)
        self.assertEqual(MPI.Op(op)(*args), res)

    def testCall(self):
        self.assertRaises(TypeError, MPI.OP_NULL)
        self.assertRaises(TypeError, MPI.OP_NULL, None)
        self.assertRaises(ValueError, MPI.OP_NULL, None, None)
        self._test_call(MPI.MIN,  (2,3), 2)
        self._test_call(MPI.MAX,  (2,3), 3)
        self._test_call(MPI.SUM,  (2,3), 5)
        self._test_call(MPI.PROD, (2,3), 6)
        for x in (False, True):
            for y in (False, True):
                self._test_call(MPI.LAND,  (x,y), x and y)
                self._test_call(MPI.LOR,   (x,y), x or  y)
                self._test_call(MPI.LXOR,  (x,y), x ^ y)
        for x in range(5):
            for y in range(5):
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
        self.assertEqual(res, x)
        res = MPI.MAX(x, y)
        self.assertEqual(res, x)

    def testMinMaxLoc(self):
        x = [1]; i = [2]; u = [x, i]
        y = [2]; j = [1]; v = [y, j]
        res = MPI.MINLOC(u, v)
        self.assertIs(res[0], x)
        self.assertIs(res[1], i)
        res = MPI.MINLOC(v, u)
        self.assertIs(res[0], x)
        self.assertIs(res[1], i)
        res = MPI.MAXLOC(u, v)
        self.assertIs(res[0], y)
        self.assertIs(res[1], j)
        res = MPI.MAXLOC(v, u)
        self.assertIs(res[0], y)
        self.assertIs(res[1], j)
        #
        x = [1]; i = 0; u = [x, i]
        y = [1]; j = 1; v = [y, j]
        res = MPI.MINLOC(u, v)
        self.assertIs(res[0], x)
        self.assertIs(res[1], i)
        res = MPI.MAXLOC(u, v)
        self.assertIs(res[0], x)
        self.assertIs(res[1], i)
        #
        x = [1]; i = 1; u = [x, i]
        y = [1]; j = 0; v = [y, j]
        res = MPI.MINLOC(u, v)
        self.assertIs(res[0], y)
        self.assertIs(res[1], j)
        res = MPI.MAXLOC(u, v)
        self.assertIs(res[0], y)
        self.assertIs(res[1], j)
        #
        x = [1]; i = [0]; u = [x, i]
        y = [1]; j = [1]; v = [y, j]
        res = MPI.MINLOC(u, v)
        self.assertIs(res[0], x)
        self.assertIs(res[1], i)
        res = MPI.MAXLOC(u, v)
        self.assertIs(res[0], x)
        self.assertIs(res[1], i)
        #
        x = [1]; i = [1]; u = [x, i]
        y = [1]; j = [0]; v = [y, j]
        res = MPI.MINLOC(u, v)
        self.assertIs(res[0], y)
        self.assertIs(res[1], j)
        res = MPI.MAXLOC(u, v)
        self.assertIs(res[0], y)
        self.assertIs(res[1], j)

    @unittest.skipMPI('openmpi(<=1.8.1)')
    def testIsCommutative(self):
        try:
            MPI.SUM.Is_commutative()
        except NotImplementedError:
            self.skipTest('mpi-op-is_commutative')
        ops = [
            MPI.MAX,    MPI.MIN,
            MPI.SUM,    MPI.PROD,
            MPI.LAND,   MPI.BAND,
            MPI.LOR,    MPI.BOR,
            MPI.LXOR,   MPI.BXOR,
            MPI.MAXLOC, MPI.MINLOC,
        ]
        for op in ops:
            flag = op.Is_commutative()
            self.assertEqual(flag, op.is_commutative)
            self.assertTrue(flag)

    @unittest.skipMPI('openmpi(<=1.8.1)')
    @unittest.skipMPI('mpich(==3.4.1)')
    def testIsCommutativeExtra(self):
        try:
            MPI.SUM.Is_commutative()
        except NotImplementedError:
            self.skipTest('mpi-op-is_commutative')
        ops =  [MPI.REPLACE, MPI.NO_OP]
        for op in ops:
            if not op: continue
            flag = op.Is_commutative()
            self.assertEqual(flag, op.is_commutative)
            #self.assertFalse(flag)

    def testIsPredefined(self):
        self.assertTrue(MPI.OP_NULL.is_predefined)
        ops = [MPI.MAX,    MPI.MIN,
               MPI.SUM,    MPI.PROD,
               MPI.LAND,   MPI.BAND,
               MPI.LOR,    MPI.BOR,
               MPI.LXOR,   MPI.BXOR,
               MPI.MAXLOC, MPI.MINLOC,]
        for op in ops:
            self.assertTrue(op.is_predefined)

    def testPicklePredefined(self):
        from pickle import dumps, loads
        ops = [
            MPI.MAX,     MPI.MIN,
            MPI.SUM,     MPI.PROD,
            MPI.LAND,    MPI.BAND,
            MPI.LOR,     MPI.BOR,
            MPI.LXOR,    MPI.BXOR,
            MPI.MAXLOC,  MPI.MINLOC,
            MPI.OP_NULL, MPI.NO_OP,
        ]
        for op in ops:
            newop = loads(dumps(op))
            self.assertIs(newop, op)
            newop = loads(dumps(MPI.Op(op)))
            self.assertIsNot(newop, op)
            self.assertEqual(newop, op)

    def testPickleUserDefined(self):
        from pickle import dumps, loads
        for commute in [True, False]:
            myop1 = MPI.Op.Create(mysum, commute)
            myop2 = loads(dumps(myop1))
            self.assertNotEqual(myop1, myop2)
            myop1.Free()
            self.assertEqual(myop2([2], [3]), [5])
            self.assertEqual(myop2.Is_commutative(), commute)
            myop2.Free()

if __name__ == '__main__':
    unittest.main()
