from mpi4py import MPI
import mpiunittest as unittest

try:
    import array
except ImportError:
    array = None
try:
    import numpy
except ImportError:
    numpy = None

class TestAddress(unittest.TestCase):

    @unittest.skipIf(array is None, 'array')
    def testGetAddress1(self):
        from struct import pack, unpack
        location = array.array('i', range(10))
        bufptr, _ = location.buffer_info()
        addr = MPI.Get_address(location)
        addr = unpack('P', pack('P', addr))[0]
        self.assertEqual(addr, bufptr)

    @unittest.skipIf(numpy is None, 'numpy')
    def testGetAddress2(self):
        from struct import pack, unpack
        location = numpy.asarray(range(10), dtype='i')
        bufptr, _ = location.__array_interface__['data']
        addr = MPI.Get_address(location)
        addr = unpack('P', pack('P', addr))[0]
        self.assertEqual(addr, bufptr)

    @unittest.skipMPI('openmpi(<=1.10.2)')
    def testBottom(self):
        base = MPI.Get_address(MPI.BOTTOM)
        addr = MPI.Aint_add(base, 0)
        self.assertEqual(addr, base)
        diff = MPI.Aint_diff(base, base)
        self.assertEqual(diff, 0)

    @unittest.skipIf(array is None, 'array')
    def testAintAdd(self):
        location = array.array('i', range(10))
        base = MPI.Get_address(location)
        addr = MPI.Aint_add(base, 4)
        self.assertEqual(addr, base + 4)

    @unittest.skipIf(array is None, 'array')
    def testAintDiff(self):
        location = array.array('i', range(10))
        base = MPI.Get_address(location)
        addr1 = base + 8
        addr2 = base + 4
        diff = MPI.Aint_diff(addr1, addr2)
        self.assertEqual(diff, 4)


if __name__ == '__main__':
    unittest.main()
