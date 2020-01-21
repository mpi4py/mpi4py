from mpi4py import MPI
import mpiunittest as unittest
from arrayimpl import allclose
from arrayimpl import typestr
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
try:
    import cupy
except ImportError:
    cupy = None
try:
    import numba
    import numba.cuda
    from distutils.version import StrictVersion
    numba_version = StrictVersion(numba.__version__).version
    if numba_version < (0, 48):
        import warnings
        warnings.warn('To test Numba GPU arrays, use Numba v0.48.0+.',
                      RuntimeWarning)
        numba = None
except ImportError:
    numba = None


py2 = sys.version_info[0] == 2
py3 = sys.version_info[0] >= 3
pypy = hasattr(sys, 'pypy_version_info')
pypy2 = pypy and py2
pypy_lt_53 = pypy and sys.pypy_version_info < (5, 3)


# ---

class GPUBuf(object):

    def __init__(self, typecode, initializer, readonly=False):
        self._buf = array.array(typecode, initializer)
        address = self._buf.buffer_info()[0]
        typecode = self._buf.typecode
        itemsize = self._buf.itemsize
        self.__cuda_array_interface__ = dict(
            version = 0,
            data    = (address, readonly),
            typestr = typestr(typecode, itemsize),
            shape   = (len(self._buf), 1, 1),
            strides = (itemsize,) * 3,
            descr   = [('', typestr(typecode, itemsize))],
        )

    def __eq__(self, other):
        return self._buf == other._buf

    def __ne__(self, other):
        return self._buf != other._buf

    def __len__(self):
        return len(self._buf)

    def __getitem__(self, item):
        return self._buf[item]

    def __setitem__(self, item, value):
        self._buf[item] = value._buf


cupy_issue_2259 = False
if cupy is not None:
    cupy_issue_2259 = not isinstance(
        cupy.zeros((2,2)).T.__cuda_array_interface__['strides'],
        tuple
    )

# ---

def Sendrecv(smsg, rmsg):
    MPI.COMM_SELF.Sendrecv(sendbuf=smsg, dest=0,   sendtag=0,
                           recvbuf=rmsg, source=0, recvtag=0,
                           status=MPI.Status())


class TestMessageSimple(unittest.TestCase):

    def testMessageBad(self):
        buf = MPI.Alloc_mem(5)
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
        def f(): Sendrecv([buf, None,  0, "i"], empty)
        self.assertRaises(ValueError, f)
        def f(): Sendrecv([buf, 0, 1, MPI.DATATYPE_NULL], empty)
        self.assertRaises(ValueError, f)
        def f(): Sendrecv([buf, None, 0, MPI.DATATYPE_NULL], empty)
        self.assertRaises(ValueError, f)
        try:
            t = MPI.INT.Create_resized(0, -4).Commit()
            def f(): Sendrecv([buf, None, t], empty)
            self.assertRaises(ValueError, f)
            def f(): Sendrecv([buf, 0, 1, t], empty)
            self.assertRaises(ValueError, f)
            t.Free()
        except NotImplementedError:
            pass
        MPI.Free_mem(buf)
        buf = [1,2,3,4]
        def f(): Sendrecv([buf, 4,  0, "i"], empty)
        self.assertRaises(TypeError, f)
        buf = {1:2,3:4}
        def f(): Sendrecv([buf, 4,  0, "i"], empty)
        self.assertRaises(TypeError, f)
        def f(): Sendrecv(b"abc", b"abc")
        self.assertRaises((BufferError, TypeError, ValueError), f)

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

    @unittest.skipIf(py3, 'python3')
    @unittest.skipIf(pypy2, 'pypy2')
    @unittest.skipIf(hasattr(MPI, 'ffi'), 'mpi4py-cffi')
    def testMessageUnicode(self):  # Test for Issue #120
        sbuf = unicode("abc")
        rbuf = bytearray(len(buffer(sbuf)))
        Sendrecv([sbuf, MPI.BYTE], [rbuf, MPI.BYTE])

    @unittest.skipIf(py3, 'python3')
    @unittest.skipIf(pypy_lt_53, 'pypy(<5.3)')
    def testMessageBuffer(self):
        sbuf = buffer(b"abc")
        rbuf = bytearray(3)
        Sendrecv([sbuf, "c"], [rbuf, MPI.CHAR])
        self.assertEqual(sbuf, rbuf)
        self.assertRaises((BufferError, TypeError, ValueError),
                          Sendrecv, [rbuf, "c"], [sbuf, "c"])

    @unittest.skipIf(pypy2, 'pypy2')
    @unittest.skipIf(pypy_lt_53, 'pypy(<5.3)')
    def testMessageMemoryView(self):
        sbuf = memoryview(b"abc")
        rbuf = bytearray(3)
        Sendrecv([sbuf, "c"], [rbuf, MPI.CHAR])
        self.assertEqual(sbuf, rbuf)
        self.assertRaises((BufferError, TypeError, ValueError),
                          Sendrecv, [rbuf, "c"], [sbuf, "c"])


@unittest.skipMPI('msmpi(<8.0.0)')
class TestMessageBlock(unittest.TestCase):

    @unittest.skipIf(MPI.COMM_WORLD.Get_size() < 2, 'mpi-world-size<2')
    def testMessageBad(self):
        comm = MPI.COMM_WORLD
        buf = MPI.Alloc_mem(4)
        empty = [None, 0, "B"]
        def f(): comm.Alltoall([buf, None, "i"], empty)
        self.assertRaises(ValueError, f)
        MPI.Free_mem(buf)


class BaseTestMessageSimpleArray(object):

    TYPECODES = "bhil"+"BHIL"+"fd"

    def array(self, typecode, initializer):
        raise NotImplementedError

    def check1(self, z, s, r, typecode):
        r[:] = z
        Sendrecv(s, r)
        for a, b in zip(s, r):
            self.assertEqual(a, b)

    def check2(self, z, s, r, typecode):
        datatype = typemap[typecode]
        for type in (None, typecode, datatype):
            r[:] = z
            Sendrecv([s, type],
                     [r, type])
            for a, b in zip(s, r):
                self.assertEqual(a, b)

    def check3(self, z, s, r, typecode):
        size = len(r)
        for count in range(size):
            r[:] = z
            Sendrecv([s, count],
                     [r, count])
            for i in range(count):
                self.assertEqual(r[i], s[i])
            for i in range(count, size):
                self.assertEqual(r[i], z[0])
        for count in range(size):
            r[:] = z
            Sendrecv([s, (count, None)],
                     [r, (count, None)])
            for i in range(count):
                self.assertEqual(r[i], s[i])
            for i in range(count, size):
                self.assertEqual(r[i], z[0])
        for disp in range(size):
            r[:] = z
            Sendrecv([s, (None, disp)],
                     [r, (None, disp)])
            for i in range(disp):
                self.assertEqual(r[i], z[0])
            for i in range(disp, size):
                self.assertEqual(r[i], s[i])
        for disp in range(size):
            for count in range(size-disp):
                r[:] = z
                Sendrecv([s, (count, disp)],
                         [r, (count, disp)])
                for i in range(0, disp):
                    self.assertEqual(r[i], z[0])
                for i in range(disp, disp+count):
                    self.assertEqual(r[i], s[i])
                for i in range(disp+count, size):
                    self.assertEqual(r[i], z[0])

    def check4(self, z, s, r, typecode):
        datatype = typemap[typecode]
        for type in (None, typecode, datatype):
            for count in (None, len(s)):
                r[:] = z
                Sendrecv([s, count, type],
                         [r, count, type])
                for a, b in zip(s, r):
                    self.assertEqual(a, b)

    def check5(self, z, s, r, typecode):
        datatype = typemap[typecode]
        for type in (None, typecode, datatype):
            for p in range(0, len(s)):
                r[:] = z
                Sendrecv([s, (p, None), type],
                         [r, (p, None), type])
                for a, b in zip(s[:p], r[:p]):
                    self.assertEqual(a, b)
                for q in range(p, len(s)):
                    count, displ = q-p, p
                    r[:] = z
                    Sendrecv([s, (count, displ), type],
                             [r, (count, displ), type])
                    for a, b in zip(r[:p], z[:p]):
                        self.assertEqual(a, b)
                    for a, b in zip(r[p:q], s[p:q]):
                        self.assertEqual(a, b)
                    for a, b in zip(r[q:], z[q:]):
                        self.assertEqual(a, b)

    def check6(self, z, s, r, typecode):
        datatype = typemap[typecode]
        for type in (None, typecode, datatype):
            for p in range(0, len(s)):
                r[:] = z
                Sendrecv([s, p, None, type],
                         [r, p, None, type])
                for a, b in zip(s[:p], r[:p]):
                    self.assertEqual(a, b)
                for q in range(p, len(s)):
                    count, displ = q-p, p
                    r[:] = z
                    Sendrecv([s, count, displ, type],
                             [r, count, displ, type])
                    for a, b in zip(r[:p], z[:p]):
                        self.assertEqual(a, b)
                    for a, b in zip(r[p:q], s[p:q]):
                        self.assertEqual(a, b)
                    for a, b in zip(r[q:], z[q:]):
                        self.assertEqual(a, b)

    def check(self, test):
        for t in tuple(self.TYPECODES):
            for n in range(1, 10):
                z = self.array(t, [0]*n)
                s = self.array(t, list(range(n)))
                r = self.array(t, [0]*n)
                test(z, s, r, t)

    def testArray1(self):
        self.check(self.check1)

    def testArray2(self):
        self.check(self.check2)

    def testArray3(self):
        self.check(self.check3)

    def testArray4(self):
        self.check(self.check4)

    def testArray5(self):
        self.check(self.check5)

    def testArray6(self):
        self.check(self.check6)


@unittest.skipIf(array is None, 'array')
class TestMessageSimpleArray(unittest.TestCase,
                             BaseTestMessageSimpleArray):

    def array(self, typecode, initializer):
        return array.array(typecode, initializer)


@unittest.skipIf(numpy is None, 'numpy')
class TestMessageSimpleNumPy(unittest.TestCase,
                             BaseTestMessageSimpleArray):

    def array(self, typecode, initializer):
        return numpy.array(initializer, dtype=typecode)

    def testOrderC(self):
        sbuf = numpy.ones([3,2])
        rbuf = numpy.zeros([3,2])
        Sendrecv(sbuf, rbuf)
        self.assertTrue((sbuf == rbuf).all())

    def testOrderFortran(self):
        sbuf = numpy.ones([3,2]).T
        rbuf = numpy.zeros([3,2]).T
        Sendrecv(sbuf, rbuf)
        self.assertTrue((sbuf == rbuf).all())

    def testReadonly(self):
        sbuf = numpy.ones([3])
        rbuf = numpy.zeros([3])
        sbuf.flags.writeable = False
        Sendrecv(sbuf, rbuf)
        self.assertTrue((sbuf == rbuf).all())

    def testNotWriteable(self):
        sbuf = numpy.ones([3])
        rbuf = numpy.zeros([3])
        rbuf.flags.writeable = False
        self.assertRaises((BufferError, ValueError),
                          Sendrecv, sbuf, rbuf)

    def testNotContiguous(self):
        sbuf = numpy.ones([3,2])[:,0]
        rbuf = numpy.zeros([3])
        sbuf.flags.writeable = False
        self.assertRaises((BufferError, ValueError),
                          Sendrecv, sbuf, rbuf)


@unittest.skipIf(array is None, 'array')
class TestMessageSimpleGPUBuf(unittest.TestCase,
                              BaseTestMessageSimpleArray):

    def array(self, typecode, initializer):
        return GPUBuf(typecode, initializer)


@unittest.skipIf(cupy is None, 'cupy')
class TestMessageSimpleCuPy(unittest.TestCase,
                            BaseTestMessageSimpleArray):

    def array(self, typecode, initializer):
        return cupy.array(initializer, dtype=typecode)

    def testOrderC(self):
        sbuf = cupy.ones([3,2])
        rbuf = cupy.zeros([3,2])
        Sendrecv(sbuf, rbuf)
        self.assertTrue((sbuf == rbuf).all())

    @unittest.skipIf(cupy_issue_2259, 'cupy-issue-2259')
    def testOrderFortran(self):
        sbuf = cupy.ones([3,2]).T
        rbuf = cupy.zeros([3,2]).T
        Sendrecv(sbuf, rbuf)
        self.assertTrue((sbuf == rbuf).all())

    @unittest.skipIf(cupy_issue_2259, 'cupy-issue-2259')
    def testNotContiguous(self):
        sbuf = cupy.ones([3,2])[:,0]
        rbuf = cupy.zeros([3])
        self.assertRaises((BufferError, ValueError),
                          Sendrecv, sbuf, rbuf)


@unittest.skipIf(numba is None, 'numba')
class TestMessageSimpleNumba(unittest.TestCase,
                             BaseTestMessageSimpleArray):

    def array(self, typecode, initializer):
        n = len(initializer)
        arr = numba.cuda.device_array((n,), dtype=typecode)
        arr[:] = initializer
        return arr

    def testOrderC(self):
        sbuf = numba.cuda.device_array((6,))
        sbuf[:] = 1
        sbuf = sbuf.reshape(3,2)
        rbuf = numba.cuda.device_array((6,))
        rbuf[:] = 0
        rbuf = sbuf.reshape(3,2)
        Sendrecv(sbuf, rbuf)
        # numba arrays do not have the .all() method
        for i in range(3):
            for j in range(2):
                self.assertTrue(sbuf[i,j] == rbuf[i,j])

    def testOrderFortran(self):
        sbuf = numba.cuda.device_array((6,))
        sbuf[:] = 1
        sbuf = sbuf.reshape(3,2,order='F')
        rbuf = numba.cuda.device_array((6,))
        rbuf[:] = 0
        rbuf = sbuf.reshape(3,2,order='F')
        Sendrecv(sbuf, rbuf)
        # numba arrays do not have the .all() method
        for i in range(3):
            for j in range(2):
                self.assertTrue(sbuf[i,j] == rbuf[i,j])

    def testNotContiguous(self):
        sbuf = numba.cuda.device_array((6,))
        sbuf[:] = 1
        sbuf = sbuf.reshape(3,2)[:,0]
        rbuf = numba.cuda.device_array((3,))
        rbuf[:] = 0
        self.assertRaises((BufferError, ValueError),
                          Sendrecv, sbuf, rbuf)


# ---

@unittest.skipIf(array is None, 'array')
class TestMessageGPUBufInterface(unittest.TestCase):

    def testNonReadonly(self):
        smsg = GPUBuf('i', [1,2,3], readonly=True)
        rmsg = GPUBuf('i', [0,0,0], readonly=True)
        if pypy: self.assertRaises(ValueError,  Sendrecv, smsg, rmsg)
        else:    self.assertRaises(BufferError, Sendrecv, smsg, rmsg)

    def testNonContiguous(self):
        smsg = GPUBuf('i', [1,2,3])
        rmsg = GPUBuf('i', [0,0,0])
        strides = rmsg.__cuda_array_interface__['strides']
        bad_strides = strides[:-1] + (7,)
        rmsg.__cuda_array_interface__['strides'] = bad_strides
        self.assertRaises(BufferError, Sendrecv, smsg, rmsg)

    def testAttrNone(self):
        smsg = GPUBuf('B', [1,2,3])
        rmsg = GPUBuf('B', [0,0,0])
        rmsg.__cuda_array_interface__ = None
        self.assertRaises(TypeError, Sendrecv, smsg, rmsg)

    def testAttrEmpty(self):
        smsg = GPUBuf('B', [1,2,3])
        rmsg = GPUBuf('B', [0,0,0])
        rmsg.__cuda_array_interface__ = dict()
        self.assertRaises(KeyError, Sendrecv, smsg, rmsg)

    def testAttrType(self):
        smsg = GPUBuf('B', [1,2,3])
        rmsg = GPUBuf('B', [0,0,0])
        items = list(rmsg.__cuda_array_interface__.items())
        rmsg.__cuda_array_interface__ = items
        self.assertRaises(TypeError, Sendrecv, smsg, rmsg)

    def testDataMissing(self):
        smsg = GPUBuf('B', [1,2,3])
        rmsg = GPUBuf('B', [0,0,0])
        del rmsg.__cuda_array_interface__['data']
        self.assertRaises(KeyError, Sendrecv, smsg, rmsg)

    def testDataNone(self):
        smsg = GPUBuf('B', [1,2,3])
        rmsg = GPUBuf('B', [0,0,0])
        rmsg.__cuda_array_interface__['data'] = None
        self.assertRaises(TypeError, Sendrecv, smsg, rmsg)

    def testDataType(self):
        smsg = GPUBuf('B', [1,2,3])
        rmsg = GPUBuf('B', [0,0,0])
        rmsg.__cuda_array_interface__['data'] = 0
        self.assertRaises(TypeError, Sendrecv, smsg, rmsg)

    def testDataValue(self):
        smsg = GPUBuf('B', [1,2,3])
        rmsg = GPUBuf('B', [0,0,0])
        dev_ptr = rmsg.__cuda_array_interface__['data'][0]
        rmsg.__cuda_array_interface__['data'] = (dev_ptr, )
        self.assertRaises(ValueError, Sendrecv, smsg, rmsg)
        rmsg.__cuda_array_interface__['data'] = ( )
        self.assertRaises(ValueError, Sendrecv, smsg, rmsg)
        rmsg.__cuda_array_interface__['data'] = (dev_ptr, False, None)
        self.assertRaises(ValueError, Sendrecv, smsg, rmsg)

    def testTypestrMissing(self):
        smsg = GPUBuf('B', [1,2,3])
        rmsg = GPUBuf('B', [0,0,0])
        del rmsg.__cuda_array_interface__['typestr']
        self.assertRaises(KeyError, Sendrecv, smsg, rmsg)

    def testTypestrNone(self):
        smsg = GPUBuf('B', [1,2,3])
        rmsg = GPUBuf('B', [0,0,0])
        rmsg.__cuda_array_interface__['typestr'] = None
        self.assertRaises(TypeError, Sendrecv, smsg, rmsg)

    def testTypestrType(self):
        smsg = GPUBuf('B', [1,2,3])
        rmsg = GPUBuf('B', [0,0,0])
        rmsg.__cuda_array_interface__['typestr'] = 42
        self.assertRaises(TypeError, Sendrecv, smsg, rmsg)

    def testTypestrItemsize(self):
        smsg = GPUBuf('B', [1,2,3])
        rmsg = GPUBuf('B', [0,0,0])
        typestr = rmsg.__cuda_array_interface__['typestr']
        rmsg.__cuda_array_interface__['typestr'] = typestr[:2]+'X'
        self.assertRaises(ValueError, Sendrecv, smsg, rmsg)

    def testShapeMissing(self):
        smsg = GPUBuf('B', [1,2,3])
        rmsg = GPUBuf('B', [0,0,0])
        del rmsg.__cuda_array_interface__['shape']
        self.assertRaises(KeyError, Sendrecv, smsg, rmsg)

    def testShapeNone(self):
        smsg = GPUBuf('B', [1,2,3])
        rmsg = GPUBuf('B', [0,0,0])
        rmsg.__cuda_array_interface__['shape'] = None
        self.assertRaises(TypeError, Sendrecv, smsg, rmsg)

    def testShapeType(self):
        smsg = GPUBuf('B', [1,2,3])
        rmsg = GPUBuf('B', [0,0,0])
        rmsg.__cuda_array_interface__['shape'] = 3
        self.assertRaises(TypeError, Sendrecv, smsg, rmsg)

    def testShapeValue(self):
        smsg = GPUBuf('B', [1,2,3])
        rmsg = GPUBuf('B', [0,0,0])
        rmsg.__cuda_array_interface__['shape'] = (3, -1)
        rmsg.__cuda_array_interface__['strides'] = None
        self.assertRaises(BufferError, Sendrecv, smsg, rmsg)

    def testStridesMissing(self):
        smsg = GPUBuf('B', [1,2,3])
        rmsg = GPUBuf('B', [0,0,0])
        del rmsg.__cuda_array_interface__['strides']
        Sendrecv(smsg, rmsg)
        self.assertEqual(smsg, rmsg)

    def testStridesNone(self):
        smsg = GPUBuf('B', [1,2,3])
        rmsg = GPUBuf('B', [0,0,0])
        rmsg.__cuda_array_interface__['strides'] = None
        Sendrecv(smsg, rmsg)
        self.assertEqual(smsg, rmsg)

    def testStridesType(self):
        smsg = GPUBuf('B', [1,2,3])
        rmsg = GPUBuf('B', [0,0,0])
        rmsg.__cuda_array_interface__['strides'] = 42
        self.assertRaises(TypeError, Sendrecv, smsg, rmsg)

    def testDescrMissing(self):
        smsg = GPUBuf('d', [1,2,3])
        rmsg = GPUBuf('d', [0,0,0])
        del rmsg.__cuda_array_interface__['descr']
        Sendrecv(smsg, rmsg)
        self.assertEqual(smsg, rmsg)

    def testDescrNone(self):
        smsg = GPUBuf('d', [1,2,3])
        rmsg = GPUBuf('d', [0,0,0])
        rmsg.__cuda_array_interface__['descr'] = None
        Sendrecv(smsg, rmsg)
        self.assertEqual(smsg, rmsg)

    def testDescrType(self):
        smsg = GPUBuf('B', [1,2,3])
        rmsg = GPUBuf('B', [0,0,0])
        rmsg.__cuda_array_interface__['descr'] = 42
        self.assertRaises(TypeError, Sendrecv, smsg, rmsg)

    def testDescrWarning(self):
        m, n = 5, 3
        smsg = GPUBuf('d', list(range(m*n)))
        rmsg = GPUBuf('d', [0]*(m*n))
        typestr = rmsg.__cuda_array_interface__['typestr']
        itemsize = int(typestr[2:])
        new_typestr = "|V"+str(itemsize*n)
        new_descr = [('', typestr)]*n
        rmsg.__cuda_array_interface__['shape'] = (m,)
        rmsg.__cuda_array_interface__['strides'] = (itemsize*n,)
        rmsg.__cuda_array_interface__['typestr'] = new_typestr
        rmsg.__cuda_array_interface__['descr'] = new_descr
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            self.assertRaises(RuntimeWarning, Sendrecv, smsg, rmsg)
        try:  # Python 3.2+
            self.assertWarns(RuntimeWarning, Sendrecv, smsg, rmsg)
        except AttributeError:  # Python 2
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                Sendrecv(smsg, rmsg)
                self.assertEqual(len(w), 1)
                self.assertEqual(w[-1].category, RuntimeWarning)
        self.assertEqual(smsg, rmsg)


# ---

def Alltoallv(smsg, rmsg):
    comm = MPI.COMM_SELF
    comm.Alltoallv(smsg, rmsg)


@unittest.skipMPI('msmpi(<8.0.0)')
class TestMessageVector(unittest.TestCase):

    def testMessageBad(self):
        buf = MPI.Alloc_mem(5)
        empty = [None, 0, [0], "B"]
        def f(): Alltoallv([buf, 0, [0], "i", None], empty)
        self.assertRaises(ValueError, f)
        def f(): Alltoallv([buf, 0, [0], "\0"], empty)
        self.assertRaises(KeyError, f)
        def f(): Alltoallv([buf, None, [0], MPI.DATATYPE_NULL], empty)
        self.assertRaises(ValueError, f)
        def f(): Alltoallv([buf, None, [0], "i"], empty)
        self.assertRaises(ValueError, f)
        try:
            t = MPI.INT.Create_resized(0, -4).Commit()
            def f(): Alltoallv([buf, None, [0], t], empty)
            self.assertRaises(ValueError, f)
            t.Free()
        except NotImplementedError:
            pass
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


@unittest.skipMPI('msmpi(<8.0.0)')
class BaseTestMessageVectorArray(object):

    TYPECODES = "bhil"+"BHIL"+"fd"

    def array(self, typecode, initializer):
        raise NotImplementedError

    def check1(self, z, s, r, typecode):
        r[:] = z
        Alltoallv(s, r)
        for a, b in zip(s, r):
            self.assertEqual(a, b)

    def check2(self, z, s, r, typecode):
        datatype = typemap[typecode]
        for type in (None, typecode, datatype):
            r[:] = z
            Alltoallv([s, type],
                      [r, type])
            for a, b in zip(s, r):
                self.assertEqual(a, b)

    def check3(self, z, s, r, typecode):
        size = len(r)
        for count in range(size):
            r[:] = z
            Alltoallv([s, count],
                      [r, count])
            for i in range(count):
                self.assertEqual(r[i], s[i])
            for i in range(count, size):
                self.assertEqual(r[i], z[0])
        for count in range(size):
            r[:] = z
            Alltoallv([s, (count, None)],
                      [r, (count, None)])
            for i in range(count):
                self.assertEqual(r[i], s[i])
            for i in range(count, size):
                self.assertEqual(r[i], z[0])
        for disp in range(size):
            for count in range(size-disp):
                r[:] = z
                Alltoallv([s, ([count], [disp])],
                          [r, ([count], [disp])])
                for i in range(0, disp):
                    self.assertEqual(r[i], z[0])
                for i in range(disp, disp+count):
                    self.assertEqual(r[i], s[i])
                for i in range(disp+count, size):
                    self.assertEqual(r[i], z[0])

    def check4(self, z, s, r, typecode):
        datatype = typemap[typecode]
        for type in (None, typecode, datatype):
            for count in (None, len(s)):
                r[:] = z
                Alltoallv([s, count, type],
                          [r, count, type])
                for a, b in zip(s, r):
                    self.assertEqual(a, b)

    def check5(self, z, s, r, typecode):
        datatype = typemap[typecode]
        for type in (None, typecode, datatype):
            for p in range(len(s)):
                r[:] = z
                Alltoallv([s, (p, None), type],
                          [r, (p, None), type])
                for a, b in zip(s[:p], r[:p]):
                    self.assertEqual(a, b)
                for q in range(p, len(s)):
                    count, displ = q-p, p
                    r[:] = z
                    Alltoallv([s, (count, [displ]), type],
                              [r, (count, [displ]), type])
                    for a, b in zip(r[:p], z[:p]):
                        self.assertEqual(a, b)
                    for a, b in zip(r[p:q], s[p:q]):
                        self.assertEqual(a, b)
                    for a, b in zip(r[q:], z[q:]):
                        self.assertEqual(a, b)

    def check6(self, z, s, r, typecode):
        datatype = typemap[typecode]
        for type in (None, typecode, datatype):
            for p in range(0, len(s)):
                r[:] = z
                Alltoallv([s, p, None, type],
                          [r, p, None, type])
                for a, b in zip(s[:p], r[:p]):
                    self.assertEqual(a, b)
                for q in range(p, len(s)):
                    count, displ = q-p, p
                    r[:] = z
                    Alltoallv([s, count, [displ], type],
                              [r, count, [displ], type])
                    for a, b in zip(r[:p], z[:p]):
                        self.assertEqual(a, b)
                    for a, b in zip(r[p:q], s[p:q]):
                        self.assertEqual(a, b)
                    for a, b in zip(r[q:], z[q:]):
                        self.assertEqual(a, b)

    def check(self, test):
        for t in tuple(self.TYPECODES):
            for n in range(1, 10):
                z = self.array(t, [0]*n)
                s = self.array(t, list(range(n)))
                r = self.array(t, [0]*n)
                test(z, s, r, t)

    def testArray1(self):
        self.check(self.check1)

    def testArray2(self):
        self.check(self.check2)

    def testArray3(self):
        self.check(self.check3)

    def testArray4(self):
        self.check(self.check4)

    def testArray5(self):
        self.check(self.check5)

    def testArray6(self):
        self.check(self.check6)


@unittest.skipIf(array is None, 'array')
class TestMessageVectorArray(unittest.TestCase,
                             BaseTestMessageVectorArray):

    def array(self, typecode, initializer):
        return array.array(typecode, initializer)


@unittest.skipIf(numpy is None, 'numpy')
class TestMessageVectorNumPy(unittest.TestCase,
                             BaseTestMessageVectorArray):

    def array(self, typecode, initializer):
        return numpy.array(initializer, dtype=typecode)


@unittest.skipIf(array is None, 'array')
class TestMessageVectorGPUBuf(unittest.TestCase,
                              BaseTestMessageVectorArray):

    def array(self, typecode, initializer):
        return GPUBuf(typecode, initializer)


@unittest.skipIf(cupy is None, 'cupy')
class TestMessageVectorCuPy(unittest.TestCase,
                            BaseTestMessageVectorArray):

    def array(self, typecode, initializer):
        return cupy.array(initializer, dtype=typecode)


@unittest.skipIf(numba is None, 'numba')
class TestMessageVectorNumba(unittest.TestCase,
                             BaseTestMessageVectorArray):

    def array(self, typecode, initializer):
        n = len(initializer)
        arr = numba.cuda.device_array((n,), dtype=typecode)
        arr[:] = initializer
        return arr


# ---

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
        def f(): Alltoallw([sbuf],[rbuf])
        self.assertRaises(ValueError, f)
        def f(): Alltoallw([sbuf, [0], [0], [MPI.BYTE], None],
                           [rbuf, [0], [0], [MPI.BYTE]])
        self.assertRaises(ValueError, f)
        def f(): Alltoallw([sbuf, [0], [0], [MPI.BYTE]],
                           [rbuf, [0], [0], [MPI.BYTE], None])
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
        sbuf = bytearray(b"abc")
        rbuf = bytearray(3)
        smsg = [sbuf, None, None, [MPI.CHAR]]
        rmsg = [rbuf, [MPI.CHAR]]
        Alltoallw(smsg, rmsg)
        self.assertEqual(sbuf[0], rbuf[0])
        self.assertEqual(bytearray(2), rbuf[1:])

    @unittest.skipIf(array is None, 'array')
    def testMessageArray(self):
        sbuf = array.array('i', [1,2,3])
        rbuf = array.array('i', [0,0,0])
        smsg = [sbuf, [3], [0], [MPI.INT]]
        rmsg = [rbuf, ([3], [0]), [MPI.INT]]
        Alltoallw(smsg, rmsg)
        self.assertEqual(sbuf, rbuf)

    @unittest.skipIf(numpy is None, 'numpy')
    def testMessageNumPy(self):
        sbuf = numpy.array([1,2,3], dtype='i')
        rbuf = numpy.array([0,0,0], dtype='i')
        smsg = [sbuf, [3], [0], [MPI.INT]]
        rmsg = [rbuf, ([3], [0]), [MPI.INT]]
        Alltoallw(smsg, rmsg)
        self.assertTrue((sbuf == rbuf).all())

    @unittest.skipIf(array is None, 'array')
    def testMessageGPUBuf(self):
        sbuf = GPUBuf('i', [1,2,3], readonly=True)
        rbuf = GPUBuf('i', [0,0,0], readonly=False)
        smsg = [sbuf, [3], [0], [MPI.INT]]
        rmsg = [rbuf, ([3], [0]), [MPI.INT]]
        Alltoallw(smsg, rmsg)
        self.assertEqual(sbuf, rbuf)

    @unittest.skipIf(cupy is None, 'cupy')
    def testMessageCuPy(self):
        sbuf = cupy.array([1,2,3], 'i')
        rbuf = cupy.array([0,0,0], 'i')
        smsg = [sbuf, [3], [0], [MPI.INT]]
        rmsg = [rbuf, ([3], [0]), [MPI.INT]]
        Alltoallw(smsg, rmsg)
        self.assertTrue((sbuf == rbuf).all())

    @unittest.skipIf(numba is None, 'numba')
    def testMessageNumba(self):
        sbuf = numba.cuda.device_array((3,), 'i')
        sbuf[:] = [1,2,3]
        rbuf = numba.cuda.device_array((3,), 'i')
        rbuf[:] = [0,0,0]
        smsg = [sbuf, [3], [0], [MPI.INT]]
        rmsg = [rbuf, ([3], [0]), [MPI.INT]]
        Alltoallw(smsg, rmsg)
        # numba arrays do not have the .all() method
        for i in range(3):
            self.assertTrue(sbuf[i] == rbuf[i])


# ---

def PutGet(smsg, rmsg, target=None):
    try: win =  MPI.Win.Allocate(256, 1, MPI.INFO_NULL, MPI.COMM_SELF)
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

    @unittest.skipIf(py3, 'python3')
    @unittest.skipIf(pypy2, 'pypy2')
    @unittest.skipIf(hasattr(MPI, 'ffi'), 'mpi4py-cffi')
    def testMessageUnicode(self):  # Test for Issue #120
        sbuf = unicode("abc")
        rbuf = bytearray(len(buffer(sbuf)))
        PutGet([sbuf, MPI.BYTE], [rbuf, MPI.BYTE], None)

    @unittest.skipMPI('msmpi')
    @unittest.skipIf(array is None, 'array')
    def testMessageArray(self):
        sbuf = array.array('i', [1,2,3])
        rbuf = array.array('i', [0,0,0])
        PutGet(sbuf, rbuf)
        self.assertEqual(sbuf, rbuf)

    @unittest.skipMPI('msmpi')
    @unittest.skipIf(numpy is None, 'numpy')
    def testMessageNumPy(self):
        sbuf = numpy.array([1,2,3], dtype='i')
        rbuf = numpy.array([0,0,0], dtype='i')
        PutGet(sbuf, rbuf)
        self.assertTrue((sbuf == rbuf).all())

    @unittest.skipMPI('msmpi')
    @unittest.skipIf(array is None, 'array')
    def testMessageGPUBuf(self):
        sbuf = GPUBuf('i', [1,2,3], readonly=True)
        rbuf = GPUBuf('i', [0,0,0], readonly=False)
        PutGet(sbuf, rbuf)
        self.assertEqual(sbuf, rbuf)

    @unittest.skipMPI('msmpi')
    @unittest.skipMPI('mvapich2')
    @unittest.skipIf(cupy is None, 'cupy')
    def testMessageCuPy(self):
        sbuf = cupy.array([1,2,3], 'i')
        rbuf = cupy.array([0,0,0], 'i')
        PutGet(sbuf, rbuf)
        self.assertTrue((sbuf == rbuf).all())

    @unittest.skipMPI('msmpi')
    @unittest.skipMPI('mvapich2')
    @unittest.skipIf(numba is None, 'numba')
    def testMessageNumba(self):
        sbuf = numba.cuda.device_array((3,), 'i')
        sbuf[:] = [1,2,3]
        rbuf = numba.cuda.device_array((3,), 'i')
        rbuf[:] = [0,0,0]
        PutGet(sbuf, rbuf)
        # numba arrays do not have the .all() method
        for i in range(3):
            self.assertTrue(sbuf[i] == rbuf[i])


# ---

if __name__ == '__main__':
    unittest.main()
