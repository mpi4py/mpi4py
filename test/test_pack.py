from mpi4py import MPI
import mpiunittest as unittest
from arrayimpl import allclose
import arrayimpl


class BaseTestPack(object):

    COMM = MPI.COMM_NULL

    skipdtype = []

    def testPackSize(self):
        for array, typecode in arrayimpl.subTest(self):
            if typecode in self.skipdtype: continue
            datatype = array.TypeMap[typecode]
            itemsize = datatype.Get_size()
            overhead = datatype.Pack_size(0, self.COMM)
            for count in range(10):
                pack_size = datatype.Pack_size(count, self.COMM)
                self.assertEqual(pack_size - overhead, count*itemsize)

    def testPackUnpack(self):
        for array, typecode1 in arrayimpl.subTest(self):
            if typecode1 in self.skipdtype: continue
            for typecode2 in array.TypeMap:
                if typecode2 in self.skipdtype: continue
                datatype1 = array.TypeMap[typecode1]
                datatype2 = array.TypeMap[typecode2]
                for items in range(10):
                    # input and output arrays
                    iarray1 = array(range(items), typecode1).as_raw()
                    iarray2 = array(range(items), typecode2).as_raw()
                    oarray1 = array(items, typecode1, items).as_raw()
                    oarray2 = array(items, typecode2, items).as_raw()
                    # temp array for packing
                    size1 = datatype1.Pack_size(len(iarray1), self.COMM)
                    size2 = datatype2.Pack_size(len(iarray2), self.COMM)
                    tmpbuf = array(0, 'b', size1 + size2 + 1).as_raw()
                    # pack input arrays
                    position = 0
                    position = datatype1.Pack(iarray1, tmpbuf, position, self.COMM)
                    position = datatype2.Pack(iarray2, tmpbuf, position, self.COMM)
                    # unpack output arrays
                    position = 0
                    position = datatype1.Unpack(tmpbuf, position, oarray1, self.COMM)
                    position = datatype2.Unpack(tmpbuf, position, oarray2, self.COMM)
                    # test
                    self.assertTrue(allclose(iarray1, oarray1))
                    self.assertTrue(allclose(iarray2, oarray2))

EXT32 = 'external32'

class BaseTestPackExternal(object):

    skipdtype = []

    def testPackSize(self):
        for array, typecode in arrayimpl.subTest(self):
            if typecode in self.skipdtype: continue
            datatype = array.TypeMap[typecode]
            itemsize = datatype.Get_size()
            overhead = datatype.Pack_external_size(EXT32, 0)
            for count in range(10):
                pack_size = datatype.Pack_external_size(EXT32, count)
                real_size = pack_size - overhead

    def testPackUnpackExternal(self):
        for array, typecode1 in arrayimpl.subTest(self):
            if unittest.is_mpi_gpu('mpich', array): continue
            if unittest.is_mpi_gpu('openmpi', array): continue
            if unittest.is_mpi_gpu('mvapich2', array): continue
            if typecode1 in self.skipdtype: continue
            for typecode2 in array.TypeMap:
                if typecode2 in self.skipdtype: continue
                datatype1 = array.TypeMap[typecode1]
                datatype2 = array.TypeMap[typecode2]
                for items in range(1, 10):
                    # input and output arrays
                    if typecode1 == 'b':
                        iarray1 = array(127, typecode1, items).as_raw()
                    else:
                        iarray1 = array(255, typecode1, items).as_raw()
                    iarray2 = array(range(items), typecode2).as_raw()
                    oarray1 = array(-1, typecode1, items).as_raw()
                    oarray2 = array(-1, typecode2, items).as_raw()
                    # temp array for packing
                    size1 = datatype1.Pack_external_size(EXT32, len(iarray1))
                    size2 = datatype2.Pack_external_size(EXT32, len(iarray2))
                    tmpbuf = array(0, 'b', size1 + size2 + 1).as_raw()
                    # pack input arrays
                    position = 0
                    position = datatype1.Pack_external(EXT32, iarray1, tmpbuf, position)
                    position = datatype2.Pack_external(EXT32, iarray2, tmpbuf, position)
                    # unpack output arrays
                    position = 0
                    position = datatype1.Unpack_external(EXT32, tmpbuf, position, oarray1)
                    position = datatype2.Unpack_external(EXT32, tmpbuf, position, oarray2)
                    # test result
                    self.assertTrue(allclose(iarray1, oarray1))
                    self.assertTrue(allclose(iarray2, oarray2))


class TestPackSelf(BaseTestPack, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestPackWorld(BaseTestPack, unittest.TestCase):
    COMM = MPI.COMM_SELF

@unittest.skipMPI('openmpi(<3.0.0)')
class TestPackExternal(BaseTestPackExternal, unittest.TestCase):
    pass


name, version = MPI.get_vendor()
if name == 'MPICH':
    if version < (4, 0, 0):
        BaseTestPackExternal.skipdtype += 'ldgFDG'
elif name == 'Open MPI':
    if version < (5, 0, 0):
        BaseTestPackExternal.skipdtype += 'gG'
elif name == 'Intel MPI':
    BaseTestPackExternal.skipdtype += 'ldgFDG'
elif name == 'Microsoft MPI':
    BaseTestPackExternal.skipdtype += 'gFDG'
elif name == 'MVAPICH2':
    BaseTestPackExternal.skipdtype += 'ldgFDG'
elif name =='MPICH2':
    BaseTestPackExternal.skipdtype += 'ldgFDG'
else:
    try:
        MPI.BYTE.Pack_external_size(EXT32, 0)
    except NotImplementedError:
        unittest.disable(BaseTestPackExternal, 'mpi-ext32')


if __name__ == '__main__':
    unittest.main()
