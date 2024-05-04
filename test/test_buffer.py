from mpi4py import MPI
import mpiunittest as unittest

try:
    import array
except ImportError:
    array = None

class TestBuffer(unittest.TestCase):

    def testNewEmpty(self):
        buffer = MPI.buffer
        buf = buffer()
        self.assertEqual(buf.address, 0)
        self.assertIsNone(buf.obj)
        self.assertEqual(buf.nbytes, 0)
        self.assertFalse(buf.readonly)
        self.assertEqual(buf.format, 'B')
        self.assertEqual(buf.itemsize, 1)
        self.assertEqual(len(buf), 0)
        buf[:] = 0
        buf[:] = buffer()
        m = memoryview(buf)
        self.assertEqual(m.format, 'B')
        self.assertEqual(m.itemsize, 1)
        self.assertEqual(m.ndim, 1)
        self.assertIs(m.readonly, False)
        self.assertEqual(m.shape, (0,))
        self.assertEqual(m.strides, (1,))
        self.assertEqual(m.tobytes(), b"")
        self.assertEqual(m.tolist(), [])
        buf.release()
        self.assertEqual(buf.address, 0)
        self.assertEqual(buf.nbytes, 0)
        self.assertFalse(buf.readonly)

    def testNewBad(self):
        buffer = MPI.buffer
        for obj in (None, 0, 0.0, [], (), []):
            self.assertRaises(TypeError,  buffer, obj)

    def testNewBytes(self):
        buffer = MPI.buffer
        obj = b"abc"
        buf = buffer(obj)
        self.assertEqual(buf.obj, obj)
        self.assertEqual(buf.nbytes, len(obj))
        self.assertIs(buf.readonly, True)
        with self.assertRaises(TypeError):
            buf[:] = 0

    def testNewBytearray(self):
        buffer = MPI.buffer
        obj = bytearray([1,2,3])
        buf = buffer(obj)
        self.assertEqual(buf.obj, obj)
        self.assertEqual(buf.nbytes, len(obj))
        self.assertFalse(buf.readonly)
        with self.assertRaises(ValueError):
            buf[0:1] = buf[1:3]

    @unittest.skipIf(array is None, 'array')
    def testNewArray(self):
        buffer = MPI.buffer
        obj = array.array('i', [1,2,3])
        buf = buffer(obj)
        self.assertEqual(buf.obj, obj)
        self.assertEqual(buf.nbytes, len(obj)*obj.itemsize)
        self.assertFalse(buf.readonly)

    def testAllocate(self):
        buffer = MPI.buffer
        for size in (0, 1, 2):
            buf = buffer.allocate(size)
            self.assertEqual(buf.nbytes, size)
            self.assertNotEqual(buf.address, 0)
            view = memoryview(buf.obj)
            self.assertEqual(buf.nbytes, view.nbytes)
        for clear in (False, True):
            buf = buffer.allocate(1024, clear)
            self.assertEqual(buf.nbytes, 1024)
            self.assertNotEqual(buf.address, 0)
            if clear:
                self.assertEqual(buf[0], 0)
                self.assertEqual(buf[-1], 0)
        self.assertRaises(TypeError,  buffer.allocate, None)
        self.assertRaises(ValueError, buffer.allocate, -1)

    def testFromBufferBad(self):
        buffer = MPI.buffer
        for obj in (None, 0, 0.0, [], (), []):
            self.assertRaises(TypeError,  buffer.frombuffer, obj)

    def testFromBufferBytes(self):
        buffer = MPI.buffer
        buf = buffer.frombuffer(b"abc", readonly=True)
        self.assertNotEqual(buf.address, 0)
        self.assertEqual(type(buf.obj), bytes)
        self.assertEqual(buf.obj, b"abc")
        self.assertEqual(buf.nbytes, 3)
        self.assertTrue (buf.readonly)
        self.assertEqual(buf.format, 'B')
        self.assertEqual(buf.itemsize, 1)
        self.assertEqual(len(buf), 3)
        m = memoryview(buf)
        self.assertEqual(m.format, 'B')
        self.assertEqual(m.itemsize, 1)
        self.assertEqual(m.ndim, 1)
        self.assertTrue (m.readonly)
        self.assertEqual(m.shape, (3,))
        self.assertEqual(m.strides, (1,))
        self.assertEqual(m.tobytes(), b"abc")
        self.assertEqual(m.tolist(), [ord(c) for c in "abc"])
        buf.release()
        self.assertEqual(buf.address, 0)
        self.assertEqual(buf.nbytes, 0)
        self.assertFalse(buf.readonly)

    @unittest.skipIf(array is None, 'array')
    def testFromBufferArrayRO(self):
        buffer = MPI.buffer
        obj = array.array('B', [1,2,3])
        buf = buffer.frombuffer(obj, readonly=True)
        self.assertNotEqual(buf.address, 0)
        self.assertEqual(type(buf.obj), array.array)
        self.assertEqual(buf.nbytes, 3)
        self.assertTrue (buf.readonly)
        self.assertEqual(buf.format, 'B')
        self.assertEqual(buf.itemsize, 1)
        self.assertEqual(len(buf), 3)
        m = memoryview(buf)
        self.assertEqual(m.format, 'B')
        self.assertEqual(m.itemsize, 1)
        self.assertEqual(m.ndim, 1)
        self.assertTrue (m.readonly)
        self.assertEqual(m.shape, (3,))
        self.assertEqual(m.strides, (1,))
        self.assertEqual(m.tobytes(), b"\1\2\3")
        self.assertEqual(m.tolist(), [1,2,3])
        buf.release()
        self.assertEqual(buf.address, 0)
        self.assertEqual(buf.nbytes, 0)
        self.assertFalse(buf.readonly)

    @unittest.skipIf(array is None, 'array')
    def testFromBufferArrayRW(self):
        buffer = MPI.buffer
        obj = array.array('B', [1,2,3])
        buf = buffer.frombuffer(obj, readonly=False)
        self.assertNotEqual(buf.address, 0)
        self.assertEqual(buf.nbytes, 3)
        self.assertFalse(buf.readonly)
        self.assertEqual(len(buf), 3)
        m = memoryview(buf)
        self.assertEqual(m.format, 'B')
        self.assertEqual(m.itemsize, 1)
        self.assertEqual(m.ndim, 1)
        self.assertFalse(m.readonly)
        self.assertEqual(m.shape, (3,))
        self.assertEqual(m.strides, (1,))
        self.assertEqual(m.tobytes(), b"\1\2\3")
        self.assertEqual(m.tolist(), [1,2,3])
        buf[:] = 1
        self.assertEqual(obj, array.array('B', [1]*3))
        buf[1:] = array.array('B', [7]*2)
        self.assertEqual(obj, array.array('B', [1,7,7]))
        buf[1:2] = array.array('B', [8]*1)
        self.assertEqual(obj, array.array('B', [1,8,7]))
        buf.release()
        self.assertEqual(buf.address, 0)
        self.assertEqual(buf.nbytes, 0)
        self.assertFalse(buf.readonly)

    @unittest.skipIf(array is None, 'array')
    def testFromAddress(self):
        buffer = MPI.buffer
        obj = array.array('B', [1,2,3])
        addr, size = obj.buffer_info()
        nbytes = size * obj.itemsize
        buf = buffer.fromaddress(addr, nbytes, readonly=False)
        self.assertNotEqual(buf.address, 0)
        self.assertEqual(buf.nbytes, 3)
        self.assertFalse(buf.readonly)
        self.assertEqual(len(buf), 3)
        m = memoryview(buf)
        self.assertEqual(m.format, 'B')
        self.assertEqual(m.itemsize, 1)
        self.assertEqual(m.ndim, 1)
        self.assertFalse(m.readonly)
        self.assertEqual(m.shape, (3,))
        self.assertEqual(m.strides, (1,))
        self.assertEqual(m.tobytes(), b"\1\2\3")
        self.assertEqual(m.tolist(), [1,2,3])
        buf[:] = 1
        self.assertEqual(obj, array.array('B', [1]*3))
        buf[1:] = array.array('B', [7]*2)
        self.assertEqual(obj, array.array('B', [1,7,7]))
        buf[1:2] = array.array('B', [8]*1)
        self.assertEqual(obj, array.array('B', [1,8,7]))
        buf.release()
        self.assertEqual(buf.address, 0)
        self.assertEqual(buf.nbytes, 0)
        self.assertFalse(buf.readonly)
        with self.assertRaises(ValueError):
            buffer.fromaddress(addr, -1)
        with self.assertRaises(ValueError):
            buffer.fromaddress(0, 1)


    def testToReadonly(self):
        buffer = MPI.buffer
        obj = bytearray(b"abc")
        buf1 = buffer.frombuffer(obj)
        buf2 = buf1.toreadonly()
        self.assertFalse(buf1.readonly)
        self.assertTrue (buf2.readonly)
        self.assertEqual(buf1.address, buf2.address)
        self.assertEqual(buf1.obj, buf2.obj)
        self.assertEqual(type(buf1.obj), type(buf2.obj))
        self.assertEqual(buf1.nbytes, buf2.nbytes)

    def testCast(self):
        buffer = MPI.buffer
        buf = buffer.allocate(2 * 3 * 4)
        mem = buf.cast('i')
        for i in range(2 * 3):
            mem[i] = i
        mem = buf.cast('i', (2, 3))
        for i in range(2):
            for j in range(3):
                self.assertEqual(mem[i, j], 3 * i + j)
        mem = buf.cast('i', (3, 2))
        for i in range(3):
            for j in range(2):
                self.assertEqual(mem[i, j], 2 * i + j)

    def testSequence(self):
        n = 16
        try:
            mem = MPI.Alloc_mem(n, MPI.INFO_NULL)
        except NotImplementedError:
            self.skipTest('mpi-alloc_mem')
        try:
            self.assertIs(type(mem), MPI.buffer)
            self.assertNotEqual(mem.address, 0)
            self.assertEqual(mem.nbytes, n)
            self.assertFalse(mem.readonly)
            self.assertEqual(len(mem), n)
            def delitem():  del mem[n]
            def getitem1(): return mem[n]
            def getitem2(): return mem[::2]
            def getitem3(): return mem[None]
            def setitem1(): mem[n] = 0
            def setitem2(): mem[::2] = 0
            def setitem3(): mem[None] = 0
            self.assertRaises(Exception,  delitem)
            self.assertRaises(IndexError, getitem1)
            self.assertRaises(IndexError, getitem2)
            self.assertRaises(TypeError,  getitem3)
            self.assertRaises(IndexError, setitem1)
            self.assertRaises(IndexError, setitem2)
            self.assertRaises(TypeError,  setitem3)
            for i in range(n):
                mem[i] = i
            for i in range(n):
                self.assertEqual(mem[i], i)
            mem[:] = 0
            for i in range(-n, 0):
                mem[i] = abs(i)
            for i in range(-n, 0):
                self.assertEqual(mem[i], abs(i))
            mem[:] = 0
            for i in range(n):
                self.assertEqual(mem[i], 0)
            mem[:] = 255
            for i in range(n):
                self.assertEqual(mem[i], 255)
            mem[:n//2] = 1
            mem[n//2:] = 0
            for i in range(n//2):
                self.assertEqual(mem[i], 1)
            for i in range(n//2, n):
                self.assertEqual(mem[i], 0)
            mem[:] = 0
            mem[1:5] = b"abcd"
            mem[10:13] = b"xyz"
            self.assertEqual(mem[0], 0)
            for i, c in enumerate("abcd"):
                self.assertEqual(mem[1+i], ord(c))
            for i in range(5, 10):
                self.assertEqual(mem[i], 0)
            for i, c in enumerate("xyz"):
                self.assertEqual(mem[10+i], ord(c))
            for i in range(13, n):
                self.assertEqual(mem[i], 0)
            self.assertEqual(mem[1:5].tobytes(), b"abcd")
            self.assertEqual(mem[10:13].tobytes(), b"xyz")
        finally:
            MPI.Free_mem(mem)
            self.assertEqual(mem.address, 0)
            self.assertEqual(mem.nbytes, 0)
            self.assertFalse(mem.readonly)

    def testBuffering(self):
        buf = MPI.Alloc_mem((1<<16)+MPI.BSEND_OVERHEAD)
        MPI.Attach_buffer(buf)
        try:
            with self.catchNotImplementedError(4,1):
                MPI.Flush_buffer()
            with self.catchNotImplementedError(4,1):
                MPI.Iflush_buffer().Wait()
        finally:
            oldbuf = MPI.Detach_buffer()
            self.assertEqual(oldbuf.address, buf.address)
            self.assertEqual(oldbuf.nbytes, buf.nbytes)
            MPI.Free_mem(buf)
        if MPI.BUFFER_AUTOMATIC != 0:
            MPI.Attach_buffer(MPI.BUFFER_AUTOMATIC)
            bufauto = MPI.Detach_buffer()
            self.assertEqual(bufauto, MPI.BUFFER_AUTOMATIC)

    def testAttachBufferReadonly(self):
        buf = MPI.buffer(b"abc")
        self.assertRaises(BufferError, MPI.Attach_buffer, buf)


try:
    MPI.buffer
except AttributeError:
    unittest.disable(TestBuffer, 'mpi4py-buffer')


if __name__ == '__main__':
    unittest.main()
