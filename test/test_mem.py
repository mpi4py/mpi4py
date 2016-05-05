from mpi4py import MPI
import mpiunittest as unittest

class TestMemory(unittest.TestCase):

    def testMemory1(self):
        for size in range(0, 10000, 100):
            if size == 0: size = 1
            try:
                mem1 = MPI.Alloc_mem(size)
                self.assertEqual(len(mem1), size)
                MPI.Free_mem(mem1)
            except NotImplementedError:
                return

    def testMemory2(self):
        for size in range(0, 10000, 100):
            if size == 0: size = 1
            try:
                mem2 = MPI.Alloc_mem(size, MPI.INFO_NULL)
                self.assertEqual(len(mem2), size)
                MPI.Free_mem(mem2)
            except NotImplementedError:
                return

    def testMemorySequence(self):
        n = 16
        try:
            mem = MPI.Alloc_mem(n, MPI.INFO_NULL)
        except NotImplementedError:
            return
        try:
            mem.address
        except AttributeError:
            MPI.Free_mem(mem)
            return
        try:
            self.assertEqual(len(mem), n)
            self.assertTrue(mem.address != 0)
            self.assertEqual(mem.nbytes, n)
            self.assertFalse(mem.readonly)
            def getitem(): return mem[n]
            def delitem(): del mem[n]
            def setitem1(): mem[n] = 0
            def setitem2(): mem[::2] = 0
            def setitem3(): mem[None] = 0
            self.assertRaises(IndexError, getitem)
            self.assertRaises(Exception,  delitem)
            self.assertRaises(IndexError, setitem1)
            self.assertRaises(IndexError, setitem2)
            self.assertRaises(TypeError,  setitem3)
            for i in range(n):
                mem[i] = i
            for i in range(n):
                self.assertEqual(mem[i], i)
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
        finally:
            MPI.Free_mem(mem)
            self.assertEqual(mem.address, 0)
            self.assertEqual(mem.nbytes, 0)
            self.assertFalse(mem.readonly)

if __name__ == '__main__':
    unittest.main()
