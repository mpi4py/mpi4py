from mpi4py import MPI
import mpiunittest as unittest

try:
    import numpy
    HAVE_NUMPY = True
except ImportError:
    HAVE_NUMPY = False

def Sendrecv(smsg, rmsg):
    comm = MPI.COMM_SELF
    sts = MPI.Status()
    comm.Sendrecv(sendbuf=smsg, recvbuf=rmsg, status=sts)

class TestMessage(unittest.TestCase):

    TYPECODES = "hil"+"HIL"+"fd"

    def _test1(self, equal, zero, s, r, t):
        r[:] = zero
        Sendrecv(s, r)
        self.assertTrue(equal(s, r))

    def _test2(self, equal, zero, s, r, typecode):
        datatype = MPI.__TypeDict__[typecode]
        for type in (None, typecode, datatype):
            r[:] = zero
            Sendrecv([s, type],
                     [r, type])
            self.assertTrue(equal(s, r))

    def _test31(self, equal, z, s, r, typecode):
        datatype = MPI.__TypeDict__[typecode]
        for count in (None, len(s)):
            for type in (None, typecode, datatype):
                r[:] = z
                Sendrecv([s, count, type],
                         [r, count, type])
                self.assertTrue(equal(s, r))

    def _test32(self, equal, z, s, r, typecode):
        datatype = MPI.__TypeDict__[typecode]
        for type in (None, typecode, datatype):
            for p in range(0, len(s)):
                r[:] = z
                Sendrecv([s, (p, None), type],
                         [r, (p, None), type])
                self.assertTrue(equal(s[:p], r[:p]))
                for q in range(p, len(s)):
                    count, displ = q-p, p
                    r[:] = z
                    Sendrecv([s, (count, displ), type],
                             [r, (count, displ), type])
                    self.assertTrue(equal(s[p:q], r[p:q]))
                    self.assertTrue(equal(z[:p], r[:p]))
                    self.assertTrue(equal(z[q:], r[q:]))

    def _test4(self, equal, z, s, r, typecode):
        datatype = MPI.__TypeDict__[typecode]
        for type in (None, typecode, datatype):
            for p in range(0, len(s)):
                r[:] = z
                Sendrecv([s, p, None, type],
                         [r, p, None, type])
                self.assertTrue(equal(s[:p], r[:p]))
                for q in range(p, len(s)):
                    count, displ = q-p, p
                    r[:] = z
                    Sendrecv([s, count, displ, type],
                             [r, count, displ, type])
                    self.assertTrue(equal(s[p:q], r[p:q]))
                    self.assertTrue(equal(z[:p], r[:p]))
                    self.assertTrue(equal(z[q:], r[q:]))

    def _testArray(self, test):
        from array import array
        from operator import eq as equal
        for t in tuple(self.TYPECODES):
            for n in range(1, 10):
                z = array(t, [0]*n)
                s = array(t, list(range(n)))
                r = array(t, [0]*n)
                test(equal, z, s, r, t)
    def testArray1(self):
        self._testArray(self._test1)
    def testArray2(self):
        self._testArray(self._test2)
    def testArray31(self):
        self._testArray(self._test31)
    def testArray32(self):
        self._testArray(self._test32)
    def testArray4(self):
        self._testArray(self._test4)

    if HAVE_NUMPY:
        def _testNumPy(self, test):
            from numpy import zeros, arange, empty
            from numpy import allclose as equal
            for t in tuple(self.TYPECODES):
                for n in range(10):
                    z = zeros (n, dtype=t)
                    s = arange(n, dtype=t)
                    r = empty (n, dtype=t)
                    test(equal, z, s, r, t)
        def testNumPy1(self):
            self._testNumPy(self._test1)
        def testNumPy2(self):
            self._testNumPy(self._test2)
        def testNumPy31(self):
            self._testNumPy(self._test31)
        def testNumPy32(self):
            self._testNumPy(self._test32)
        def testNumPy4(self):
            self._testNumPy(self._test4)


if __name__ == '__main__':
    unittest.main()
