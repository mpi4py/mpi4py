from mpi4py import MPI
import mpiunittest as unittest


class TestMemory(unittest.TestCase):

    def testMemory1(self):
        for size in range(0, 10000, 100):
            size = max(1, size)  # Open MPI
            try:
                mem1 = MPI.Alloc_mem(size)
                self.assertEqual(len(mem1), size)
                MPI.Free_mem(mem1)
            except NotImplementedError:
                self.skipTest('mpi-alloc_mem')

    def testMemory2(self):
        for size in range(0, 10000, 100):
            size = max(1, size)  # Open MPI
            try:
                mem2 = MPI.Alloc_mem(size, MPI.INFO_NULL)
                self.assertEqual(len(mem2), size)
                MPI.Free_mem(mem2)
            except NotImplementedError:
                self.skipTest('mpi-alloc_mem')


if __name__ == '__main__':
    unittest.main()
