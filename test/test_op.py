from mpi4py import MPI
import mpiunittest as unittest

MPI_ERR_OP = MPI.ERR_OP

class TestOp(unittest.TestCase):

    def testCreate(self):
        op = MPI.Op()
        self.assertFalse(op)
        self.assertEqual(op, MPI.OP_NULL)

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

    def testFree(self):
        self.assertRaisesMPI(MPI.ERR_OP, MPI.OP_NULL.Free)
        for op in (MPI.MAX, MPI.MIN,
                   MPI.SUM, MPI.PROD,
                   MPI.LAND, MPI.BAND,
                   MPI.LOR, MPI.BOR,
                   MPI.LXOR, MPI.BXOR,
                   MPI.MAXLOC, MPI.MINLOC):
            self.assertRaisesMPI(MPI_ERR_OP, op.Free)
        if MPI.REPLACE != MPI.OP_NULL:
            self.assertRaisesMPI(MPI_ERR_OP, op.Free)

_name, _version = MPI.get_vendor()
if _name == 'MPICH1':
    MPI_ERR_OP = MPI.ERR_ARG


if __name__ == '__main__':
    unittest.main()
