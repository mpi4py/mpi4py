import unittest
from mpi4py import MPI

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

if __name__ == '__main__':
    unittest.main()
