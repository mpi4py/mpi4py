from mpi4py import MPI
import mpiunittest as unittest
import sys
try:
    from array import array
except ImportError:
    array = None

pypy_lt_58 = (hasattr(sys, 'pypy_version_info') and
              sys.pypy_version_info < (5, 8))

class TestMemory(unittest.TestCase):

    def testNewEmpty(self):
        memory = MPI.memory
        mem = memory()
        self.assertEqual(mem.address, 0)
        self.assertEqual(mem.obj, None)
        self.assertEqual(mem.nbytes, 0)
        self.assertEqual(mem.readonly, False)
        self.assertEqual(mem.format, 'B')
        self.assertEqual(mem.itemsize, 1)
        self.assertEqual(len(mem), 0)
        mem[:] = 0
        mem[:] = memory()
        if sys.version_info < (3,0):
            b = buffer(mem)
            self.assertEqual(len(b), 0)
        if sys.version_info >= (2,7):
            m = memoryview(mem)
            self.assertEqual(m.format, 'B')
            self.assertEqual(m.itemsize, 1)
            self.assertEqual(m.ndim, 1)
            if not pypy_lt_58:
                self.assertEqual(m.readonly, False)
            self.assertEqual(m.shape, (0,))
            self.assertEqual(m.strides, (1,))
            self.assertEqual(m.tobytes(), b"")
            self.assertEqual(m.tolist(), [])
        mem.release()
        self.assertEqual(mem.address, 0)
        self.assertEqual(mem.nbytes, 0)
        self.assertEqual(mem.readonly, False)

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
        self.assertEqual(mem.readonly, True)

    def testNewBytearray(self):
        memory = MPI.memory
        obj = bytearray([1,2,3])
        mem = memory(obj)
        self.assertEqual(mem.obj, obj)
        self.assertEqual(mem.nbytes, len(obj))
        self.assertEqual(mem.readonly, False)

    @unittest.skipIf(array is None, 'array')
    def testNewArray(self):
        memory = MPI.memory
        obj = array('i', [1,2,3])
        mem = memory(obj)
        self.assertEqual(mem.obj, obj)
        self.assertEqual(mem.nbytes, len(obj)*obj.itemsize)
        self.assertEqual(mem.readonly, False)

    def testAllocate(self):
        memory = MPI.memory
        for size in (0, 1, 2):
            mem = memory.allocate(size)
            self.assertEqual(mem.nbytes, size)
            self.assertNotEqual(mem.address, 0)
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
        self.assertEqual(mem.readonly, True)
        self.assertEqual(mem.format, 'B')
        self.assertEqual(mem.itemsize, 1)
        self.assertEqual(len(mem), 3)
        if sys.version_info < (3,0):
            b = buffer(mem)
            self.assertEqual(len(b), 3)
        if sys.version_info >= (2,7):
            m = memoryview(mem)
            self.assertEqual(m.format, 'B')
            self.assertEqual(m.itemsize, 1)
            self.assertEqual(m.ndim, 1)
            if not pypy_lt_58:
                self.assertEqual(m.readonly, True)
            self.assertEqual(m.shape, (3,))
            self.assertEqual(m.strides, (1,))
            self.assertEqual(m.tobytes(), b"abc")
            self.assertEqual(m.tolist(), [ord(c) for c in "abc"])
        mem.release()
        self.assertEqual(mem.address, 0)
        self.assertEqual(mem.nbytes, 0)
        self.assertEqual(mem.readonly, False)

    @unittest.skipIf(array is None, 'array')
    def testFromBufferArrayRO(self):
        memory = MPI.memory
        obj = array('B', [1,2,3])
        mem = memory.frombuffer(obj, readonly=True)
        self.assertNotEqual(mem.address, 0)
        self.assertEqual(type(mem.obj), array)
        self.assertEqual(mem.nbytes, 3)
        self.assertEqual(mem.readonly, True)
        self.assertEqual(mem.format, 'B')
        self.assertEqual(mem.itemsize, 1)
        self.assertEqual(len(mem), 3)
        if sys.version_info < (3,0):
            b = buffer(mem)
            self.assertEqual(len(b), 3)
        if sys.version_info >= (2,7):
            m = memoryview(mem)
            self.assertEqual(m.format, 'B')
            self.assertEqual(m.itemsize, 1)
            self.assertEqual(m.ndim, 1)
            if not pypy_lt_58:
                self.assertEqual(m.readonly, True)
            self.assertEqual(m.shape, (3,))
            self.assertEqual(m.strides, (1,))
            self.assertEqual(m.tobytes(), b"\1\2\3")
            self.assertEqual(m.tolist(), [1,2,3])
        mem.release()
        self.assertEqual(mem.address, 0)
        self.assertEqual(mem.nbytes, 0)
        self.assertEqual(mem.readonly, False)

    @unittest.skipIf(array is None, 'array')
    def testFromBufferArrayRW(self):
        memory = MPI.memory
        obj = array('B', [1,2,3])
        mem = memory.frombuffer(obj, readonly=False)
        self.assertNotEqual(mem.address, 0)
        self.assertEqual(mem.nbytes, 3)
        self.assertEqual(mem.readonly, False)
        self.assertEqual(len(mem), 3)
        if sys.version_info < (3,0):
            b = buffer(mem)
            self.assertEqual(len(b), 3)
        if sys.version_info >= (2,7):
            m = memoryview(mem)
            self.assertEqual(m.format, 'B')
            self.assertEqual(m.itemsize, 1)
            self.assertEqual(m.ndim, 1)
            if not pypy_lt_58:
                self.assertEqual(m.readonly, False)
            self.assertEqual(m.shape, (3,))
            self.assertEqual(m.strides, (1,))
            self.assertEqual(m.tobytes(), b"\1\2\3")
            self.assertEqual(m.tolist(), [1,2,3])
        mem[:] = 1
        self.assertEqual(obj, array('B', [1]*3))
        mem[1:] = array('B', [7]*2)
        self.assertEqual(obj, array('B', [1,7,7]))
        mem[1:2] = array('B', [8]*1)
        self.assertEqual(obj, array('B', [1,8,7]))
        mem.release()
        self.assertEqual(mem.address, 0)
        self.assertEqual(mem.nbytes, 0)
        self.assertEqual(mem.readonly, False)

    @unittest.skipIf(array is None, 'array')
    def testFromAddress(self):
        memory = MPI.memory
        obj = array('B', [1,2,3])
        addr, size = obj.buffer_info()
        nbytes = size * obj.itemsize
        mem = memory.fromaddress(addr, nbytes, readonly=False)
        self.assertNotEqual(mem.address, 0)
        self.assertEqual(mem.nbytes, 3)
        self.assertEqual(mem.readonly, False)
        self.assertEqual(len(mem), 3)
        if sys.version_info < (3,0):
            b = buffer(mem)
            self.assertEqual(len(b), 3)
        if sys.version_info >= (2,7):
            m = memoryview(mem)
            self.assertEqual(m.format, 'B')
            self.assertEqual(m.itemsize, 1)
            self.assertEqual(m.ndim, 1)
            if not pypy_lt_58:
                self.assertEqual(m.readonly, False)
            self.assertEqual(m.shape, (3,))
            self.assertEqual(m.strides, (1,))
            self.assertEqual(m.tobytes(), b"\1\2\3")
            self.assertEqual(m.tolist(), [1,2,3])
        mem[:] = 1
        self.assertEqual(obj, array('B', [1]*3))
        mem[1:] = array('B', [7]*2)
        self.assertEqual(obj, array('B', [1,7,7]))
        mem[1:2] = array('B', [8]*1)
        self.assertEqual(obj, array('B', [1,8,7]))
        mem.release()
        self.assertEqual(mem.address, 0)
        self.assertEqual(mem.nbytes, 0)
        self.assertEqual(mem.readonly, False)

    def testToReadonly(self):
        memory = MPI.memory
        obj = bytearray(b"abc")
        mem1 = memory.frombuffer(obj)
        mem2 = mem1.toreadonly()
        self.assertEqual(mem1.readonly, False)
        self.assertEqual(mem2.readonly, True)
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
            self.assertTrue(type(mem) is MPI.memory)
            self.assertTrue(mem.address != 0)
            self.assertEqual(mem.nbytes, n)
            self.assertEqual(mem.readonly, False)
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
            self.assertEqual(mem.readonly, False)

try:
    MPI.memory
except AttributeError:
    unittest.disable(TestMemory, 'mpi4py-memory')


if __name__ == '__main__':
    unittest.main()
