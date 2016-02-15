from mpi4py import MPI
import mpiunittest as unittest

class TestAddress(unittest.TestCase):

    def testGetAddress(self):
        from struct import pack, unpack
        try:
            from array import array
            location = array('i', range(10))
            bufptr, _ = location.buffer_info()
            addr = MPI.Get_address(location)
            addr = unpack('P', pack('P', addr))[0]
            self.assertEqual(addr, bufptr)
        except ImportError:
            pass
        try:
            from numpy import asarray
            location = asarray(range(10), dtype='i')
            bufptr, _ = location.__array_interface__['data']
            addr = MPI.Get_address(location)
            addr = unpack('P', pack('P', addr))[0]
            self.assertEqual(addr, bufptr)
        except ImportError:
            pass

    def testBottom(self):
        base = MPI.Get_address(MPI.BOTTOM)
        addr = MPI.Aint_add(base, 0)
        self.assertEqual(addr, base)
        diff = MPI.Aint_diff(base, base)
        self.assertEqual(diff, 0)

    def testAintAdd(self):
        try:
            from array import array
        except ImportError:
            return
        location = array('i', range(10))
        base = MPI.Get_address(location)
        addr = MPI.Aint_add(base, 4)
        self.assertEqual(addr, base + 4)

    def testAintDiff(self):
        try:
            from array import array
        except ImportError:
            return
        location = array('i', range(10))
        base = MPI.Get_address(location)
        addr1 = base + 8
        addr2 = base + 4
        diff = MPI.Aint_diff(addr1, addr2)
        self.assertEqual(diff, 4)


name, version = MPI.get_vendor()
if name == 'Open MPI':
    if version <= (1,10,2):
        del TestAddress.testBottom


if __name__ == '__main__':
    unittest.main()
