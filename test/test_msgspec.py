from mpi4py import MPI
import mpiunittest as unittest
import sys

from arrayimpl import (
    array,
    numpy,
    cupy,
    numba,
)

from arrayimpl import typestr
typemap = MPI._typedict

# ---

class BaseBuf(object):

    def __init__(self, typecode, initializer):
        self._buf = array.array(typecode, initializer)

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

# ---

try:
    import dlpackimpl as dlpack
except ImportError:
    dlpack = None

class DLPackCPUBuf(BaseBuf):

    def __init__(self, typecode, initializer):
        super(DLPackCPUBuf, self).__init__(typecode, initializer)
        self.managed = dlpack.make_dl_managed_tensor(self._buf)

    def __del__(self):
        self.managed = None
        if sys and not hasattr(sys, 'pypy_version_info'):
            if sys.getrefcount(self._buf) > 2:
                raise RuntimeError('dlpack: possible reference leak')

    def __dlpack_device__(self):
        device = self.managed.dl_tensor.device
        return (device.device_type, device.device_id)

    def __dlpack__(self, stream=None):
        managed = self.managed
        if managed.dl_tensor.device.device_type == \
           dlpack.DLDeviceType.kDLCPU:
            assert stream == None
        capsule = dlpack.make_py_capsule(managed)
        return capsule


if cupy is not None:

    class DLPackGPUBuf(BaseBuf):

        has_dlpack = None
        dev_type = None

        def __init__(self, typecode, initializer):
            self._buf = cupy.array(initializer, dtype=typecode)
            self.has_dlpack = hasattr(self._buf, '__dlpack_device__')
            # TODO(leofang): test CUDA managed memory?
            if cupy.cuda.runtime.is_hip:
                self.dev_type = dlpack.DLDeviceType.kDLROCM
            else:
                self.dev_type = dlpack.DLDeviceType.kDLCUDA

        def __del__(self):
            if sys and not hasattr(sys, 'pypy_version_info'):
                if sys.getrefcount(self._buf) > 2:
                    raise RuntimeError('dlpack: possible reference leak')

        def __dlpack_device__(self):
            if self.has_dlpack:
                return self._buf.__dlpack_device__()
            else:
                return (self.dev_type, self._buf.device.id)

        def __dlpack__(self, stream=None):
            cupy.cuda.get_current_stream().synchronize()
            if self.has_dlpack:
                return self._buf.__dlpack__(stream=-1)
            else:
                return self._buf.toDlpack()


# ---

class CAIBuf(BaseBuf):

    def __init__(self, typecode, initializer, readonly=False):
        super(CAIBuf, self).__init__(typecode, initializer)
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

    def testMessageBytes(self):
        sbuf = b"abc"
        rbuf = bytearray(3)
        Sendrecv([sbuf, "c"], [rbuf, MPI.CHAR])
        self.assertEqual(sbuf, rbuf)

    def testMessageBytearray(self):
        sbuf = bytearray(b"abc")
        rbuf = bytearray(3)
        Sendrecv([sbuf, "c"], [rbuf, MPI.CHAR])
        self.assertEqual(sbuf, rbuf)

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

    @unittest.skipIf(numpy.__version__[:5] == '1.22.', 'numpy==1.22.*')
    def testNotWriteable(self):
        sbuf = numpy.ones([3])
        rbuf = numpy.zeros([3])
        rbuf.flags.writeable = False
        self.assertRaises((BufferError, ValueError),
                          Sendrecv, sbuf, rbuf)

    def testNotContiguous(self):
        sbuf = numpy.ones([3,2])[:,0]
        rbuf = numpy.zeros([3])
        self.assertRaises((BufferError, ValueError),
                          Sendrecv, sbuf, rbuf)


@unittest.skipIf(array is None, 'array')
@unittest.skipIf(dlpack is None, 'dlpack')
class TestMessageSimpleDLPackCPUBuf(unittest.TestCase,
                                    BaseTestMessageSimpleArray):

    def array(self, typecode, initializer):
        return DLPackCPUBuf(typecode, initializer)


@unittest.skipIf(cupy is None, 'cupy')
class TestMessageSimpleDLPackGPUBuf(unittest.TestCase,
                                    BaseTestMessageSimpleArray):

    def array(self, typecode, initializer):
        return DLPackGPUBuf(typecode, initializer)


@unittest.skipIf(array is None, 'array')
class TestMessageSimpleCAIBuf(unittest.TestCase,
                              BaseTestMessageSimpleArray):

    def array(self, typecode, initializer):
        return CAIBuf(typecode, initializer)


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
@unittest.skipIf(dlpack is None, 'dlpack')
class TestMessageDLPackCPUBuf(unittest.TestCase):

    def testDevice(self):
        buf = DLPackCPUBuf('i', [0,1,2,3])
        buf.__dlpack_device__ = None
        self.assertRaises(TypeError, MPI.Get_address, buf)
        buf.__dlpack_device__ = lambda: None
        self.assertRaises(TypeError, MPI.Get_address, buf)
        buf.__dlpack_device__ = lambda: (None, 0)
        self.assertRaises(TypeError, MPI.Get_address, buf)
        buf.__dlpack_device__ = lambda: (1, None)
        self.assertRaises(TypeError, MPI.Get_address, buf)
        buf.__dlpack_device__ = lambda: (1,)
        self.assertRaises(ValueError, MPI.Get_address, buf)
        buf.__dlpack_device__ = lambda: (1, 0, 1)
        self.assertRaises(ValueError, MPI.Get_address, buf)
        del buf.__dlpack_device__
        MPI.Get_address(buf)

    def testCapsule(self):
        buf = DLPackCPUBuf('i', [0,1,2,3])
        #
        capsule = buf.__dlpack__()
        MPI.Get_address(buf)
        MPI.Get_address(buf)
        del capsule
        #
        capsule = buf.__dlpack__()
        retvals = [capsule] * 2
        buf.__dlpack__ = lambda *args, **kwargs: retvals.pop()
        MPI.Get_address(buf)
        self.assertRaises(BufferError, MPI.Get_address, buf)
        del buf.__dlpack__
        del capsule
        #
        buf.__dlpack__ = lambda *args, **kwargs:  None
        self.assertRaises(BufferError, MPI.Get_address, buf)
        del buf.__dlpack__

    def testNdim(self):
        buf = DLPackCPUBuf('i', [0,1,2,3])
        dltensor = buf.managed.dl_tensor
        #
        for ndim in (2, 1, 0):
            dltensor.ndim = ndim
            MPI.Get_address(buf)
        #
        dltensor.ndim = -1
        self.assertRaises(BufferError, MPI.Get_address, buf)
        #
        del dltensor

    def testShape(self):
        buf = DLPackCPUBuf('i', [0,1,2,3])
        dltensor = buf.managed.dl_tensor
        #
        dltensor.ndim = 1
        dltensor.shape[0] = -1
        self.assertRaises(BufferError, MPI.Get_address, buf)
        #
        dltensor.ndim = 0
        dltensor.shape = None
        MPI.Get_address(buf)
        #
        dltensor.ndim = 1
        dltensor.shape = None
        self.assertRaises(BufferError, MPI.Get_address, buf)
        #
        del dltensor

    def testStrides(self):
        buf = DLPackCPUBuf('i', range(8))
        dltensor = buf.managed.dl_tensor
        #
        for order in ('C', 'F'):
            dltensor.ndim, dltensor.shape, dltensor.strides = \
                dlpack.make_dl_shape([2, 2, 2], order=order)
            MPI.Get_address(buf)
            dltensor.strides[0] = -1
            self.assertRaises(BufferError, MPI.Get_address, buf)
        #
        del dltensor

    def testContiguous(self):
        buf = DLPackCPUBuf('i', range(8))
        dltensor = buf.managed.dl_tensor
        #
        dltensor.ndim, dltensor.shape, dltensor.strides = \
            dlpack.make_dl_shape([2, 2, 2], order='C')
        s = dltensor.strides
        strides = [s[i] for i in range(dltensor.ndim)]
        s[0], s[1], s[2] = [strides[i] for i in [0, 1, 2]]
        MPI.Get_address(buf)
        s[0], s[1], s[2] = [strides[i] for i in [2, 1, 0]]
        MPI.Get_address(buf)
        s[0], s[1], s[2] = [strides[i] for i in [0, 2, 1]]
        self.assertRaises(BufferError, MPI.Get_address, buf)
        s[0], s[1], s[2] = [strides[i] for i in [1, 0, 2]]
        self.assertRaises(BufferError, MPI.Get_address, buf)
        del s
        #
        del dltensor

    def testByteOffset(self):
        buf = DLPackCPUBuf('B', [0,1,2,3])
        dltensor = buf.managed.dl_tensor
        #
        dltensor.ndim = 1
        for i in range(len(buf)):
            dltensor.byte_offset = i
            mem = MPI.memory(buf)
            self.assertEqual(mem[0], buf[i])
        #
        del dltensor

# ---

@unittest.skipIf(array is None, 'array')
class TestMessageCAIBuf(unittest.TestCase):

    def testNonReadonly(self):
        smsg = CAIBuf('i', [1,2,3], readonly=True)
        rmsg = CAIBuf('i', [0,0,0], readonly=True)
        self.assertRaises(BufferError, Sendrecv, smsg, rmsg)

    def testNonContiguous(self):
        smsg = CAIBuf('i', [1,2,3])
        rmsg = CAIBuf('i', [0,0,0])
        strides = rmsg.__cuda_array_interface__['strides']
        bad_strides = strides[:-1] + (7,)
        rmsg.__cuda_array_interface__['strides'] = bad_strides
        self.assertRaises(BufferError, Sendrecv, smsg, rmsg)

    def testAttrNone(self):
        smsg = CAIBuf('B', [1,2,3])
        rmsg = CAIBuf('B', [0,0,0])
        rmsg.__cuda_array_interface__ = None
        self.assertRaises(TypeError, Sendrecv, smsg, rmsg)

    def testAttrEmpty(self):
        smsg = CAIBuf('B', [1,2,3])
        rmsg = CAIBuf('B', [0,0,0])
        rmsg.__cuda_array_interface__ = dict()
        self.assertRaises(KeyError, Sendrecv, smsg, rmsg)

    def testAttrType(self):
        smsg = CAIBuf('B', [1,2,3])
        rmsg = CAIBuf('B', [0,0,0])
        items = list(rmsg.__cuda_array_interface__.items())
        rmsg.__cuda_array_interface__ = items
        self.assertRaises(TypeError, Sendrecv, smsg, rmsg)

    def testDataMissing(self):
        smsg = CAIBuf('B', [1,2,3])
        rmsg = CAIBuf('B', [0,0,0])
        del rmsg.__cuda_array_interface__['data']
        self.assertRaises(KeyError, Sendrecv, smsg, rmsg)

    def testDataNone(self):
        smsg = CAIBuf('B', [1,2,3])
        rmsg = CAIBuf('B', [0,0,0])
        rmsg.__cuda_array_interface__['data'] = None
        self.assertRaises(TypeError, Sendrecv, smsg, rmsg)

    def testDataType(self):
        smsg = CAIBuf('B', [1,2,3])
        rmsg = CAIBuf('B', [0,0,0])
        rmsg.__cuda_array_interface__['data'] = 0
        self.assertRaises(TypeError, Sendrecv, smsg, rmsg)

    def testDataValue(self):
        smsg = CAIBuf('B', [1,2,3])
        rmsg = CAIBuf('B', [0,0,0])
        dev_ptr = rmsg.__cuda_array_interface__['data'][0]
        rmsg.__cuda_array_interface__['data'] = (dev_ptr, )
        self.assertRaises(ValueError, Sendrecv, smsg, rmsg)
        rmsg.__cuda_array_interface__['data'] = ( )
        self.assertRaises(ValueError, Sendrecv, smsg, rmsg)
        rmsg.__cuda_array_interface__['data'] = (dev_ptr, False, None)
        self.assertRaises(ValueError, Sendrecv, smsg, rmsg)

    def testTypestrMissing(self):
        smsg = CAIBuf('B', [1,2,3])
        rmsg = CAIBuf('B', [0,0,0])
        del rmsg.__cuda_array_interface__['typestr']
        self.assertRaises(KeyError, Sendrecv, smsg, rmsg)

    def testTypestrNone(self):
        smsg = CAIBuf('B', [1,2,3])
        rmsg = CAIBuf('B', [0,0,0])
        rmsg.__cuda_array_interface__['typestr'] = None
        self.assertRaises(TypeError, Sendrecv, smsg, rmsg)

    def testTypestrType(self):
        smsg = CAIBuf('B', [1,2,3])
        rmsg = CAIBuf('B', [0,0,0])
        rmsg.__cuda_array_interface__['typestr'] = 42
        self.assertRaises(TypeError, Sendrecv, smsg, rmsg)

    def testTypestrItemsize(self):
        smsg = CAIBuf('B', [1,2,3])
        rmsg = CAIBuf('B', [0,0,0])
        typestr = rmsg.__cuda_array_interface__['typestr']
        rmsg.__cuda_array_interface__['typestr'] = typestr[:2]+'X'
        self.assertRaises(ValueError, Sendrecv, smsg, rmsg)

    def testShapeMissing(self):
        smsg = CAIBuf('B', [1,2,3])
        rmsg = CAIBuf('B', [0,0,0])
        del rmsg.__cuda_array_interface__['shape']
        self.assertRaises(KeyError, Sendrecv, smsg, rmsg)

    def testShapeNone(self):
        smsg = CAIBuf('B', [1,2,3])
        rmsg = CAIBuf('B', [0,0,0])
        rmsg.__cuda_array_interface__['shape'] = None
        self.assertRaises(TypeError, Sendrecv, smsg, rmsg)

    def testShapeType(self):
        smsg = CAIBuf('B', [1,2,3])
        rmsg = CAIBuf('B', [0,0,0])
        rmsg.__cuda_array_interface__['shape'] = 3
        self.assertRaises(TypeError, Sendrecv, smsg, rmsg)

    def testShapeValue(self):
        smsg = CAIBuf('B', [1,2,3])
        rmsg = CAIBuf('B', [0,0,0])
        rmsg.__cuda_array_interface__['shape'] = (3, -1)
        rmsg.__cuda_array_interface__['strides'] = None
        self.assertRaises(BufferError, Sendrecv, smsg, rmsg)

    def testStridesMissing(self):
        smsg = CAIBuf('B', [1,2,3])
        rmsg = CAIBuf('B', [0,0,0])
        del rmsg.__cuda_array_interface__['strides']
        Sendrecv(smsg, rmsg)
        self.assertEqual(smsg, rmsg)

    def testStridesNone(self):
        smsg = CAIBuf('B', [1,2,3])
        rmsg = CAIBuf('B', [0,0,0])
        rmsg.__cuda_array_interface__['strides'] = None
        Sendrecv(smsg, rmsg)
        self.assertEqual(smsg, rmsg)

    def testStridesType(self):
        smsg = CAIBuf('B', [1,2,3])
        rmsg = CAIBuf('B', [0,0,0])
        rmsg.__cuda_array_interface__['strides'] = 42
        self.assertRaises(TypeError, Sendrecv, smsg, rmsg)

    def testDescrMissing(self):
        smsg = CAIBuf('d', [1,2,3])
        rmsg = CAIBuf('d', [0,0,0])
        del rmsg.__cuda_array_interface__['descr']
        Sendrecv(smsg, rmsg)
        self.assertEqual(smsg, rmsg)

    def testDescrNone(self):
        smsg = CAIBuf('d', [1,2,3])
        rmsg = CAIBuf('d', [0,0,0])
        rmsg.__cuda_array_interface__['descr'] = None
        Sendrecv(smsg, rmsg)
        self.assertEqual(smsg, rmsg)

    def testDescrType(self):
        smsg = CAIBuf('B', [1,2,3])
        rmsg = CAIBuf('B', [0,0,0])
        rmsg.__cuda_array_interface__['descr'] = 42
        self.assertRaises(TypeError, Sendrecv, smsg, rmsg)

    def testDescrWarning(self):
        m, n = 5, 3
        smsg = CAIBuf('d', list(range(m*n)))
        rmsg = CAIBuf('d', [0]*(m*n))
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
        self.assertWarns(RuntimeWarning, Sendrecv, smsg, rmsg)
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

    def testMessageBytes(self):
        sbuf = b"abc"
        rbuf = bytearray(3)
        Alltoallv([sbuf, "c"], [rbuf, MPI.CHAR])
        self.assertEqual(sbuf, rbuf)

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
class TestMessageVectorCAIBuf(unittest.TestCase,
                              BaseTestMessageVectorArray):

    def array(self, typecode, initializer):
        return CAIBuf(typecode, initializer)


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

    def testMessageBottom(self):
        sbuf = b"abcxyz"
        rbuf = bytearray(6)
        saddr = MPI.Get_address(sbuf)
        raddr = MPI.Get_address(rbuf)
        stype = MPI.Datatype.Create_struct([6], [saddr], [MPI.CHAR]).Commit()
        rtype = MPI.Datatype.Create_struct([6], [raddr], [MPI.CHAR]).Commit()
        smsg = [MPI.BOTTOM,  [1], [0] , [stype]]
        rmsg = [MPI.BOTTOM, ([1], [0]), [rtype]]
        try:
            Alltoallw(smsg, rmsg)
            self.assertEqual(sbuf, rbuf)
        finally:
            stype.Free()
            rtype.Free()

    def testMessageBytes(self):
        sbuf = b"abc"
        rbuf = bytearray(3)
        smsg = [sbuf, [3], [0], [MPI.CHAR]]
        rmsg = [rbuf, ([3], [0]), [MPI.CHAR]]
        Alltoallw(smsg, rmsg)
        self.assertEqual(sbuf, rbuf)

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
    def testMessageCAIBuf(self):
        sbuf = CAIBuf('i', [1,2,3], readonly=True)
        rbuf = CAIBuf('i', [0,0,0], readonly=False)
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

    def testMessageBytes(self):
        for target in (None, 0, [0, 3, MPI.BYTE]):
            sbuf = b"abc"
            rbuf = bytearray(3)
            PutGet(sbuf, rbuf, target)
            self.assertEqual(sbuf, rbuf)

    def testMessageBytearray(self):
        for target in (None, 0, [0, 3, MPI.BYTE]):
            sbuf = bytearray(b"abc")
            rbuf = bytearray(3)
            PutGet(sbuf, rbuf, target)
            self.assertEqual(sbuf, rbuf)

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
    def testMessageCAIBuf(self):
        sbuf = CAIBuf('i', [1,2,3], readonly=True)
        rbuf = CAIBuf('i', [0,0,0], readonly=False)
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
