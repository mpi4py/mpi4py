from mpi4py import MPI
import mpiunittest as unittest
from arrayimpl import allclose
import sys

typemap = MPI._typedict

try:
    import array
except ImportError:
    array = None
try:
    import numpy
except ImportError:
    numpy = None

pypy_lt_53 = (hasattr(sys, 'pypy_version_info') and
              sys.pypy_version_info < (5, 3))

def Sendrecv(smsg, rmsg):
    MPI.COMM_SELF.Sendrecv(sendbuf=smsg, dest=0,   sendtag=0,
                           recvbuf=rmsg, source=0, recvtag=0,
                           status=MPI.Status())

class TestMessageSimple(unittest.TestCase):

    TYPECODES = "hil"+"HIL"+"fd"

    def check1(self, equal, zero, s, r, t):
        r[:] = zero
        Sendrecv(s, r)
        self.assertTrue(equal(s, r))

    def check21(self, equal, zero, s, r, typecode):
        datatype = typemap[typecode]
        for type in (None, typecode, datatype):
            r[:] = zero
            Sendrecv([s, type],
                     [r, type])
            self.assertTrue(equal(s, r))

    def check22(self, equal, zero, s, r, typecode):
        size = len(r)
        for count in range(size):
            r[:] = zero
            Sendrecv([s, count],
                     [r, count])
            for i in range(count):
                self.assertTrue(equal(r[i], s[i]))
            for i in range(count, size):
                self.assertTrue(equal(r[i], zero[0]))
        for count in range(size):
            r[:] = zero
            Sendrecv([s, (count, None)],
                     [r, (count, None)])
            for i in range(count):
                self.assertTrue(equal(r[i], s[i]))
            for i in range(count, size):
                self.assertTrue(equal(r[i], zero[0]))
        for disp in range(size):
            r[:] = zero
            Sendrecv([s, (None, disp)],
                     [r, (None, disp)])
            for i in range(disp):
                self.assertTrue(equal(r[i], zero[0]))
            for i in range(disp, size):
                self.assertTrue(equal(r[i], s[i]))
        for disp in range(size):
            for count in range(size-disp):
                r[:] = zero
                Sendrecv([s, (count, disp)],
                         [r, (count, disp)])
                for i in range(0, disp):
                    self.assertTrue(equal(r[i], zero[0]))
                for i in range(disp, disp+count):
                    self.assertTrue(equal(r[i], s[i]))
                for i in range(disp+count, size):
                    self.assertTrue(equal(r[i], zero[0]))

    def check31(self, equal, z, s, r, typecode):
        datatype = typemap[typecode]
        for type in (None, typecode, datatype):
            for count in (None, len(s)):
                r[:] = z
                Sendrecv([s, count, type],
                         [r, count, type])
                self.assertTrue(equal(s, r))

    def check32(self, equal, z, s, r, typecode):
        datatype = typemap[typecode]
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

    def check4(self, equal, z, s, r, typecode):
        datatype = typemap[typecode]
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

    def testMessageBad(self):
        buf = MPI.Alloc_mem(4)
        empty = [None, 0, "B"]
        def f(): Sendrecv([buf, 0, 0, "i", None], empty)
        self.assertRaises(ValueError, f)
        def f(): Sendrecv([buf,  0, "\0"], empty)
        self.assertRaises(KeyError, f)
        def f(): Sendrecv([buf, -1, "i"], empty)
        self.assertRaises(ValueError, f)
        def f(): Sendrecv([buf, 0, -1, "i"], empty)
        self.assertRaises(ValueError, f)
        def f(): Sendrecv([buf, 0, +2, "i"], empty)
        self.assertRaises(ValueError, f)
        def f(): Sendrecv([None, 1,  0, "i"], empty)
        self.assertRaises(ValueError, f)
        MPI.Free_mem(buf)
        buf = [1,2,3,4]
        def f(): Sendrecv([buf, 4,  0, "i"], empty)
        self.assertRaises(TypeError, f)
        buf = {1:2,3:4}
        def f(): Sendrecv([buf, 4,  0, "i"], empty)
        self.assertRaises(TypeError, f)

    def testMessageNone(self):
        empty = [None, 0, "B"]
        Sendrecv(empty, empty)
        empty = [None, "B"]
        Sendrecv(empty, empty)

    def testMessageBottom(self):
        empty = [MPI.BOTTOM, 0, "B"]
        Sendrecv(empty, empty)
        empty = [MPI.BOTTOM, "B"]
        Sendrecv(empty, empty)

    @unittest.skipIf(pypy_lt_53, 'pypy(<5.3)')
    def testMessageBytes(self):
        sbuf = b"abc"
        rbuf = bytearray(3)
        Sendrecv([sbuf, "c"], [rbuf, MPI.CHAR])
        self.assertEqual(sbuf, rbuf)

    @unittest.skipIf(pypy_lt_53, 'pypy(<5.3)')
    def testMessageBytearray(self):
        sbuf = bytearray(b"abc")
        rbuf = bytearray(3)
        Sendrecv([sbuf, "c"], [rbuf, MPI.CHAR])
        self.assertEqual(sbuf, rbuf)

    @unittest.skipIf(array is None, 'array')
    def checkArray(self, test):
        from operator import eq as equal
        for t in tuple(self.TYPECODES):
            for n in range(1, 10):
                z = array.array(t, [0]*n)
                s = array.array(t, list(range(n)))
                r = array.array(t, [0]*n)
                test(equal, z, s, r, t)
    def testArray1(self):
        self.checkArray(self.check1)
    def testArray21(self):
        self.checkArray(self.check21)
    def testArray22(self):
        self.checkArray(self.check22)
    def testArray31(self):
        self.checkArray(self.check31)
    def testArray32(self):
        self.checkArray(self.check32)
    def testArray4(self):
        self.checkArray(self.check4)

    @unittest.skipIf(numpy is None, 'numpy')
    def checkNumPy(self, test):
        from numpy import zeros, arange, empty
        for t in tuple(self.TYPECODES):
            for n in range(10):
                z = zeros (n, dtype=t)
                s = arange(n, dtype=t)
                r = empty (n, dtype=t)
                test(allclose, z, s, r, t)
    def testNumPy1(self):
        self.checkNumPy(self.check1)
    def testNumPy21(self):
        self.checkNumPy(self.check21)
    def testNumPy22(self):
        self.checkNumPy(self.check22)
    def testNumPy31(self):
        self.checkNumPy(self.check31)
    def testNumPy32(self):
        self.checkNumPy(self.check32)
    def testNumPy4(self):
        self.checkNumPy(self.check4)

def Alltoallv(smsg, rmsg):
    comm = MPI.COMM_SELF
    comm.Alltoallv(smsg, rmsg)

@unittest.skipMPI('msmpi(<8.0.0)')
class TestMessageVector(unittest.TestCase):

    TYPECODES = "hil"+"HIL"+"fd"

    def check1(self, equal, zero, s, r, t):
        r[:] = zero
        Alltoallv(s, r)
        self.assertTrue(equal(s, r))

    def check21(self, equal, zero, s, r, typecode):
        datatype = typemap[typecode]
        for type in (None, typecode, datatype):
            r[:] = zero
            Alltoallv([s, type],
                      [r, type])
            self.assertTrue(equal(s, r))

    def check22(self, equal, zero, s, r, typecode):
        size = len(r)
        for count in range(size):
            r[:] = zero
            Alltoallv([s, count],
                      [r, count])
            for i in range(count):
                self.assertTrue(equal(r[i], s[i]))
            for i in range(count, size):
                self.assertTrue(equal(r[i], zero[0]))
        for count in range(size):
            r[:] = zero
            Alltoallv([s, (count, None)],
                      [r, (count, None)])
            for i in range(count):
                self.assertTrue(equal(r[i], s[i]))
            for i in range(count, size):
                self.assertTrue(equal(r[i], zero[0]))
        for disp in range(size):
            for count in range(size-disp):
                r[:] = zero
                Alltoallv([s, ([count], [disp])],
                          [r, ([count], [disp])])
                for i in range(0, disp):
                    self.assertTrue(equal(r[i], zero[0]))
                for i in range(disp, disp+count):
                    self.assertTrue(equal(r[i], s[i]))
                for i in range(disp+count, size):
                    self.assertTrue(equal(r[i], zero[0]))

    def check31(self, equal, z, s, r, typecode):
        datatype = typemap[typecode]
        for type in (None, typecode, datatype):
            for count in (None, len(s)):
                r[:] = z
                Alltoallv([s, count, type],
                          [r, count, type])
                self.assertTrue(equal(s, r))

    def check32(self, equal, z, s, r, typecode):
        datatype = typemap[typecode]
        for type in (None, typecode, datatype):
            for p in range(len(s)):
                r[:] = z
                Alltoallv([s, (p, None), type],
                          [r, (p, None), type])
                self.assertTrue(equal(s[:p], r[:p]))
                for q in range(p, len(s)):
                    count, displ = q-p, p
                    r[:] = z
                    Alltoallv([s, (count, [displ]), type],
                              [r, (count, [displ]), type])
                    self.assertTrue(equal(s[p:q], r[p:q]))
                    self.assertTrue(equal(z[:p], r[:p]))
                    self.assertTrue(equal(z[q:], r[q:]))

    def check4(self, equal, z, s, r, typecode):
        datatype = typemap[typecode]
        for type in (None, typecode, datatype):
            for p in range(0, len(s)):
                r[:] = z
                Alltoallv([s, p, None, type],
                          [r, p, None, type])
                self.assertTrue(equal(s[:p], r[:p]))
                for q in range(p, len(s)):
                    count, displ = q-p, p
                    r[:] = z
                    Alltoallv([s, count, [displ], type],
                              [r, count, [displ], type])
                    self.assertTrue(equal(s[p:q], r[p:q]))
                    self.assertTrue(equal(z[:p], r[:p]))
                    self.assertTrue(equal(z[q:], r[q:]))

    def testMessageBad(self):
        buf = MPI.Alloc_mem(4)
        empty = [None, 0, [0], "B"]
        def f(): Alltoallv([buf, 0, [0], "i", None], empty)
        self.assertRaises(ValueError, f)
        def f(): Alltoallv([buf, 0, [0], "\0"], empty)
        self.assertRaises(KeyError, f)
        MPI.Free_mem(buf)
        buf = [1,2,3,4]
        def f(): Alltoallv([buf, 0,  0, "i"], empty)
        self.assertRaises(TypeError, f)
        buf = {1:2,3:4}
        def f(): Alltoallv([buf, 0,  0, "i"], empty)
        self.assertRaises(TypeError, f)

    def testMessageNone(self):
        empty = [None, 0, "B"]
        Alltoallv(empty, empty)
        empty = [None, "B"]
        Alltoallv(empty, empty)

    def testMessageBottom(self):
        empty = [MPI.BOTTOM, 0, [0], "B"]
        Alltoallv(empty, empty)
        empty = [MPI.BOTTOM, 0, "B"]
        Alltoallv(empty, empty)
        empty = [MPI.BOTTOM, "B"]
        Alltoallv(empty, empty)

    @unittest.skipIf(pypy_lt_53, 'pypy(<5.3)')
    def testMessageBytes(self):
        sbuf = b"abc"
        rbuf = bytearray(3)
        Alltoallv([sbuf, "c"], [rbuf, MPI.CHAR])
        self.assertEqual(sbuf, rbuf)

    @unittest.skipIf(pypy_lt_53, 'pypy(<5.3)')
    def testMessageBytearray(self):
        sbuf = bytearray(b"abc")
        rbuf = bytearray(3)
        Alltoallv([sbuf, "c"], [rbuf, MPI.CHAR])
        self.assertEqual(sbuf, rbuf)

    @unittest.skipIf(array is None, 'array')
    def checkArray(self, test):
        from operator import eq as equal
        for t in tuple(self.TYPECODES):
            for n in range(1, 10):
                z = array.array(t, [0]*n)
                s = array.array(t, list(range(n)))
                r = array.array(t, [0]*n)
                test(equal, z, s, r, t)
    def testArray1(self):
        self.checkArray(self.check1)
    def testArray21(self):
        self.checkArray(self.check21)
    def testArray22(self):
        self.checkArray(self.check22)
    def testArray31(self):
        self.checkArray(self.check31)
    def testArray32(self):
        self.checkArray(self.check32)
    def testArray4(self):
        self.checkArray(self.check4)

    @unittest.skipIf(numpy is None, 'numpy')
    def checkNumPy(self, test):
        from numpy import zeros, arange, empty
        for t in tuple(self.TYPECODES):
            for n in range(10):
                z = zeros (n, dtype=t)
                s = arange(n, dtype=t)
                r = empty (n, dtype=t)
                test(allclose, z, s, r, t)
    def testNumPy1(self):
        self.checkNumPy(self.check1)
    def testNumPy21(self):
        self.checkNumPy(self.check21)
    def testNumPy22(self):
        self.checkNumPy(self.check22)
    def testNumPy31(self):
        self.checkNumPy(self.check31)
    def testNumPy32(self):
        self.checkNumPy(self.check32)
    def testNumPy4(self):
        self.checkNumPy(self.check4)

def Alltoallw(smsg, rmsg):
    try:
        MPI.COMM_SELF.Alltoallw(smsg, rmsg)
    except NotImplementedError:
        if isinstance(smsg, (list, tuple)): smsg = smsg[0]
        if isinstance(rmsg, (list, tuple)): rmsg = rmsg[0]
        try: rmsg[:] = smsg
        except: pass

class TestMessageVectorW(unittest.TestCase):

    def testMessageBad(self):
        sbuf = MPI.Alloc_mem(4)
        rbuf = MPI.Alloc_mem(4)
        def f(): Alltoallw([sbuf, [0], [0], [MPI.BYTE], None],
                           [sbuf, [0], [0], [MPI.BYTE]])
        self.assertRaises(ValueError, f)
        def f(): Alltoallw([sbuf, [0], [0], [MPI.BYTE]],
                           [sbuf, [0], [0], [MPI.BYTE], None])
        self.assertRaises(ValueError, f)
        MPI.Free_mem(sbuf)
        MPI.Free_mem(rbuf)

    @unittest.skipIf(pypy_lt_53, 'pypy(<5.3)')
    def testMessageBytes(self):
        sbuf = b"abc"
        rbuf = bytearray(3)
        smsg = [sbuf, [3], [0], [MPI.CHAR]]
        rmsg = [rbuf, ([3], [0]), [MPI.CHAR]]
        Alltoallw(smsg, rmsg)
        self.assertEqual(sbuf, rbuf)

    @unittest.skipIf(pypy_lt_53, 'pypy(<5.3)')
    def testMessageBytearray(self):
        sbuf = bytearray(b"abc")
        rbuf = bytearray(3)
        smsg = [sbuf, [3], [0], [MPI.CHAR]]
        rmsg = [rbuf, ([3], [0]), [MPI.CHAR]]
        Alltoallw(smsg, rmsg)
        self.assertEqual(sbuf, rbuf)

def PutGet(smsg, rmsg, target):
    try: win =  MPI.Win.Allocate(8, 1, MPI.INFO_NULL, MPI.COMM_SELF)
    except NotImplementedError: win = MPI.WIN_NULL
    try:
        try: win.Fence()
        except NotImplementedError: pass
        try: win.Put(smsg, 0, target)
        except NotImplementedError: pass
        try: win.Fence()
        except NotImplementedError: pass
        try: win.Get(rmsg, 0, target)
        except NotImplementedError:
            if isinstance(smsg, (list, tuple)): smsg = smsg[0]
            if isinstance(rmsg, (list, tuple)): rmsg = rmsg[0]
            try: rmsg[:] = smsg
            except: pass
        try: win.Fence()
        except NotImplementedError: pass
    finally:
        if win != MPI.WIN_NULL: win.Free()

class TestMessageRMA(unittest.TestCase):

    def testMessageBad(self):
        sbuf = [None, 0, 0, "B", None]
        rbuf = [None, 0, 0, "B"]
        target = (0, 0, MPI.BYTE)
        def f(): PutGet(sbuf, rbuf, target)
        self.assertRaises(ValueError, f)
        sbuf = [None, 0, 0, "B"]
        rbuf = [None, 0, 0, "B", None]
        target = (0, 0, MPI.BYTE)
        def f(): PutGet(sbuf, rbuf, target)
        self.assertRaises(ValueError, f)
        sbuf = [None, 0, "B"]
        rbuf = [None, 0, "B"]
        target = (0, 0, MPI.BYTE, None)
        def f(): PutGet(sbuf, rbuf, target)
        self.assertRaises(ValueError, f)
        sbuf = [None, 0, "B"]
        rbuf = [None, 0, "B"]
        target = {1:2,3:4}
        def f(): PutGet(sbuf, rbuf, target)
        self.assertRaises(ValueError, f)

    def testMessageNone(self):
        for empty in ([None, 0, 0, MPI.BYTE],
                      [None, 0, MPI.BYTE],
                      [None, MPI.BYTE]):
            for target in (None, 0, [0, 0, MPI.BYTE]):
                PutGet(empty, empty, target)

    def testMessageBottom(self):
        for empty in ([MPI.BOTTOM, 0, 0, MPI.BYTE],
                      [MPI.BOTTOM, 0, MPI.BYTE],
                      [MPI.BOTTOM, MPI.BYTE]):
            for target in (None, 0, [0, 0, MPI.BYTE]):
                PutGet(empty, empty, target)

    @unittest.skipIf(pypy_lt_53, 'pypy(<5.3)')
    def testMessageBytes(self):
        for target in (None, 0, [0, 3, MPI.BYTE]):
            sbuf = b"abc"
            rbuf = bytearray(3)
            PutGet(sbuf, rbuf, target)
            self.assertEqual(sbuf, rbuf)

    @unittest.skipIf(pypy_lt_53, 'pypy(<5.3)')
    def testMessageBytearray(self):
        for target in (None, 0, [0, 3, MPI.BYTE]):
            sbuf = bytearray(b"abc")
            rbuf = bytearray(3)
            PutGet(sbuf, rbuf, target)
            self.assertEqual(sbuf, rbuf)


if __name__ == '__main__':
    unittest.main()
