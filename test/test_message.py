from mpi4py import MPI
import mpiunittest as unittest

def Sendrecv(smsg, rmsg):
    comm = MPI.COMM_SELF
    sts = MPI.Status()
    comm.Sendrecv(sendbuf=smsg, recvbuf=rmsg, status=sts)

class TestMessage(unittest.TestCase):

    def _test1(self, equal, zero, s, r, t):
        r[:] = zero
        Sendrecv(s, r)
        self.assertTrue(equal(s, r))

    def _test2(self, equal, zero, s, r, typecode):
        datatype = MPI.__DTypeMap__[typecode]
        for type in (None, typecode, datatype):
            r[:] = zero
            Sendrecv([s, type],
                     [r, type])
            self.assertTrue(equal(s, r))

    def _test31(self, equal, z, s, r, typecode):
        datatype = MPI.__DTypeMap__[typecode]
        for count in (None, len(s)):
            for type in (None, typecode, datatype):
                r[:] = z
                Sendrecv([s, count, type],
                         [r, count, type])
                self.assertTrue(equal(s, r))

    def _test32(self, equal, z, s, r, typecode):
        datatype = MPI.__DTypeMap__[typecode]
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
        datatype = MPI.__DTypeMap__[typecode]
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

    def testArray(self):
        from array import array
        from operator import eq as equal
        typecodes = "hil"+"HIL"+"fd"
        for t in tuple(typecodes):
            for n in range(1, 10):
                z = array(t, [0]*n)
                s = array(t, list(range(n)))
                r = array(t, [0]*n)
                self._test1  (equal, z, s, r, t)
                self._test2  (equal, z, s, r, t)
                self._test31 (equal, z, s, r, t)
                self._test32 (equal, z, s, r, t)
                self._test4  (equal, z, s, r, t)

    def testNumPy(self):
        from numpy import zeros, arange, empty
        from numpy import allclose as equal
        typecodes = "hil"+"HIL"+"fd"
        for t in tuple(typecodes):
            for n in range(10):
                z = zeros (n, dtype=t)
                s = arange(n, dtype=t)
                r = empty (n, dtype=t)
                self._test1  (equal, z, s, r, t)
                self._test2  (equal, z, s, r, t)
                self._test31 (equal, z, s, r, t)
                self._test32 (equal, z, s, r, t)
                self._test4  (equal, z, s, r, t)

try:
    import numpy
except ImportError:
    del TestMessage.testNumPy

if __name__ == '__main__':
    unittest.main()
