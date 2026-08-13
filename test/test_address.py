import mpiunittest as unittest

from mpi4py import MPI

try:
    import array
except ImportError:
    array = None

try:
    import numpy
except ImportError:
    numpy = None


class TestAddress(unittest.TestCase):
    #
    @unittest.skipIf(array is None, "array")
    def testGetAddressArray(self):
        from struct import pack, unpack

        assert array is not None
        location = array.array("i", range(10))
        bufptr, _ = location.buffer_info()
        addr = MPI.Get_address(location)
        addr = unpack("P", pack("P", addr))[0]
        self.assertEqual(addr, bufptr)

    @unittest.skipIf(numpy is None, "numpy")
    def testGetAddressNumPy(self):
        from struct import pack, unpack

        assert numpy is not None
        location = numpy.asarray(range(10), dtype="i")
        bufptr, _ = location.__array_interface__["data"]
        addr = MPI.Get_address(location)
        addr = unpack("P", pack("P", addr))[0]
        self.assertEqual(addr, bufptr)

    def testNone(self):
        base = MPI.Get_address(None)
        addr = MPI.Aint_add(base, 0)
        self.assertEqual(addr, base)
        diff = MPI.Aint_diff(base, base)
        self.assertEqual(diff, 0)

    def testBottom(self):
        base = MPI.Get_address(MPI.BOTTOM)
        addr = MPI.Aint_add(base, 0)
        self.assertEqual(addr, base)
        diff = MPI.Aint_diff(base, base)
        self.assertEqual(diff, 0)

    @unittest.skipIf(array is None, "array")
    def testAintAdd(self):
        assert array is not None
        location = array.array("i", range(10))
        base = MPI.Get_address(location)
        addr = MPI.Aint_add(base, 4)
        self.assertEqual(addr, base + 4)

    @unittest.skipIf(array is None, "array")
    def testAintDiff(self):
        assert array is not None
        location = array.array("i", range(10))
        base = MPI.Get_address(location)
        addr1 = base + 8
        addr2 = base + 4
        diff = MPI.Aint_diff(addr1, addr2)
        self.assertEqual(diff, 4)


if __name__ == "__main__":
    unittest.main()
