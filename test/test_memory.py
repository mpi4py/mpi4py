from mpi4py import MPI
import mpiunittest as unittest

try:
    import array
except ImportError:
    array = None

class TestMemory(unittest.TestCase):

    def testNewEmpty(self):
        memory = MPI.memory
        mem = memory()
        self.assertEqual(mem.address, 0)
        self.assertIsNone(mem.obj)
        self.assertEqual(mem.nbytes, 0)
        self.assertFalse(mem.readonly)
        self.assertEqual(mem.format, 'B')
        self.assertEqual(mem.itemsize, 1)
        self.assertEqual(len(mem), 0)
        mem[:] = 0
        mem[:] = memory()
        m = memoryview(mem)
        self.assertEqual(m.format, 'B')
        self.assertEqual(m.itemsize, 1)
        self.assertEqual(m.ndim, 1)
        self.assertIs(m.readonly, False)
        self.assertEqual(m.shape, (0,))
        self.assertEqual(m.strides, (1,))
        self.assertEqual(m.tobytes(), b"")
        self.assertEqual(m.tolist(), [])
        mem.release()
        self.assertEqual(mem.address, 0)
        self.assertEqual(mem.nbytes, 0)
        self.assertFalse(mem.readonly)

    def testNewBad(self):
        memory = MPI.memory
        for obj in (None, 0, 0.0, [], (), []):
            self.assertRaises(TypeError,  memory, obj)

    def testNewBytes(self):
        memory = MPI.memory
        obj = b"abc"
        mem = memory(obj)
        self.assertEqual(mem.obj, obj)
        self.assertEqual(mem.nbytes, len(obj))
        self.assertIs(mem.readonly, True)
        with self.assertRaises(TypeError):
            mem[:] = 0

    def testNewBytearray(self):
        memory = MPI.memory
        obj = bytearray([1,2,3])
        mem = memory(obj)
        self.assertEqual(mem.obj, obj)
        self.assertEqual(mem.nbytes, len(obj))
        self.assertFalse(mem.readonly)
        with self.assertRaises(ValueError):
            mem[0:1] = mem[1:3]

    @unittest.skipIf(array is None, 'array')
    def testNewArray(self):
        memory = MPI.memory
        obj = array.array('i', [1,2,3])
        mem = memory(obj)
        self.assertEqual(mem.obj, obj)
        self.assertEqual(mem.nbytes, len(obj)*obj.itemsize)
        self.assertFalse(mem.readonly)

    def testAllocate(self):
        memory = MPI.memory
        for size in (0, 1, 2):
            mem = memory.allocate(size)
            self.assertEqual(mem.nbytes, size)
            self.assertNotEqual(mem.address, 0)
            view = memoryview(mem.obj)
            self.assertEqual(mem.nbytes, view.nbytes)
        for clear in (False, True):
            mem = memory.allocate(1024, clear)
            self.assertEqual(mem.nbytes, 1024)
            self.assertNotEqual(mem.address, 0)
            if clear:
                self.assertEqual(mem[0], 0)
                self.assertEqual(mem[-1], 0)
        self.assertRaises(TypeError,  memory.allocate, None)
        self.assertRaises(ValueError, memory.allocate, -1)

    def testFromBufferBad(self):
        memory = MPI.memory
        for obj in (None, 0, 0.0, [], (), []):
            self.assertRaises(TypeError,  memory.frombuffer, obj)

    def testFromBufferBytes(self):
        memory = MPI.memory
        mem = memory.frombuffer(b"abc", readonly=True)
        self.assertNotEqual(mem.address, 0)
        self.assertEqual(type(mem.obj), bytes)
        self.assertEqual(mem.obj, b"abc")
        self.assertEqual(mem.nbytes, 3)
        self.assertTrue (mem.readonly)
        self.assertEqual(mem.format, 'B')
        self.assertEqual(mem.itemsize, 1)
        self.assertEqual(len(mem), 3)
        m = memoryview(mem)
        self.assertEqual(m.format, 'B')
        self.assertEqual(m.itemsize, 1)
        self.assertEqual(m.ndim, 1)
        self.assertTrue (m.readonly)
        self.assertEqual(m.shape, (3,))
        self.assertEqual(m.strides, (1,))
        self.assertEqual(m.tobytes(), b"abc")
        self.assertEqual(m.tolist(), [ord(c) for c in "abc"])
        mem.release()
        self.assertEqual(mem.address, 0)
        self.assertEqual(mem.nbytes, 0)
        self.assertFalse(mem.readonly)

    @unittest.skipIf(array is None, 'array')
    def testFromBufferArrayRO(self):
        memory = MPI.memory
        obj = array.array('B', [1,2,3])
        mem = memory.frombuffer(obj, readonly=True)
        self.assertNotEqual(mem.address, 0)
        self.assertEqual(type(mem.obj), array.array)
        self.assertEqual(mem.nbytes, 3)
        self.assertTrue (mem.readonly)
        self.assertEqual(mem.format, 'B')
        self.assertEqual(mem.itemsize, 1)
        self.assertEqual(len(mem), 3)
        m = memoryview(mem)
        self.assertEqual(m.format, 'B')
        self.assertEqual(m.itemsize, 1)
        self.assertEqual(m.ndim, 1)
        self.assertTrue (m.readonly)
        self.assertEqual(m.shape, (3,))
        self.assertEqual(m.strides, (1,))
        self.assertEqual(m.tobytes(), b"\1\2\3")
        self.assertEqual(m.tolist(), [1,2,3])
        mem.release()
        self.assertEqual(mem.address, 0)
        self.assertEqual(mem.nbytes, 0)
        self.assertFalse(mem.readonly)

    @unittest.skipIf(array is None, 'array')
    def testFromBufferArrayRW(self):
        memory = MPI.memory
        obj = array.array('B', [1,2,3])
        mem = memory.frombuffer(obj, readonly=False)
        self.assertNotEqual(mem.address, 0)
        self.assertEqual(mem.nbytes, 3)
        self.assertFalse(mem.readonly)
        self.assertEqual(len(mem), 3)
        m = memoryview(mem)
        self.assertEqual(m.format, 'B')
        self.assertEqual(m.itemsize, 1)
        self.assertEqual(m.ndim, 1)
        self.assertFalse(m.readonly)
        self.assertEqual(m.shape, (3,))
        self.assertEqual(m.strides, (1,))
        self.assertEqual(m.tobytes(), b"\1\2\3")
        self.assertEqual(m.tolist(), [1,2,3])
        mem[:] = 1
        self.assertEqual(obj, array.array('B', [1]*3))
        mem[1:] = array.array('B', [7]*2)
        self.assertEqual(obj, array.array('B', [1,7,7]))
        mem[1:2] = array.array('B', [8]*1)
        self.assertEqual(obj, array.array('B', [1,8,7]))
        mem.release()
        self.assertEqual(mem.address, 0)
        self.assertEqual(mem.nbytes, 0)
        self.assertFalse(mem.readonly)

    @unittest.skipIf(array is None, 'array')
    def testFromAddress(self):
        memory = MPI.memory
        obj = array.array('B', [1,2,3])
        addr, size = obj.buffer_info()
        nbytes = size * obj.itemsize
        mem = memory.fromaddress(addr, nbytes, readonly=False)
        self.assertNotEqual(mem.address, 0)
        self.assertEqual(mem.nbytes, 3)
        self.assertFalse(mem.readonly)
        self.assertEqual(len(mem), 3)
        m = memoryview(mem)
        self.assertEqual(m.format, 'B')
        self.assertEqual(m.itemsize, 1)
        self.assertEqual(m.ndim, 1)
        self.assertFalse(m.readonly)
        self.assertEqual(m.shape, (3,))
        self.assertEqual(m.strides, (1,))
        self.assertEqual(m.tobytes(), b"\1\2\3")
        self.assertEqual(m.tolist(), [1,2,3])
        mem[:] = 1
        self.assertEqual(obj, array.array('B', [1]*3))
        mem[1:] = array.array('B', [7]*2)
        self.assertEqual(obj, array.array('B', [1,7,7]))
        mem[1:2] = array.array('B', [8]*1)
        self.assertEqual(obj, array.array('B', [1,8,7]))
        mem.release()
        self.assertEqual(mem.address, 0)
        self.assertEqual(mem.nbytes, 0)
        self.assertFalse(mem.readonly)
        with self.assertRaises(ValueError):
            memory.fromaddress(addr, -1)
        with self.assertRaises(ValueError):
            memory.fromaddress(0, 1)


    def testToReadonly(self):
        memory = MPI.memory
        obj = bytearray(b"abc")
        mem1 = memory.frombuffer(obj)
        mem2 = mem1.toreadonly()
        self.assertFalse(mem1.readonly)
        self.assertTrue (mem2.readonly)
        self.assertEqual(mem1.address, mem2.address)
        self.assertEqual(mem1.obj, mem2.obj)
        self.assertEqual(type(mem1.obj), type(mem2.obj))
        self.assertEqual(mem1.nbytes, mem2.nbytes)

    def testSequence(self):
        n = 16
        try:
            mem = MPI.Alloc_mem(n, MPI.INFO_NULL)
        except NotImplementedError:
            self.skipTest('mpi-alloc_mem')
        try:
            self.assertIs(type(mem), MPI.memory)
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

    def testAttachBufferReadonly(self):
        buf = MPI.memory(b"abc")
        self.assertRaises(BufferError, MPI.Attach_buffer, buf)


try:
    MPI.memory
except AttributeError:
    unittest.disable(TestMemory, 'mpi4py-memory')


if __name__ == '__main__':
    unittest.main()
