from mpi4py import MPI
import mpiunittest as unittest
import arrayimpl

class BaseTestPack(object):

    COMM = MPI.COMM_NULL

    def testPackSize(self):
        for array in arrayimpl.ArrayTypes:
            for typecode, datatype in arrayimpl.TypeMap.items():
                itemsize = array(0, typecode).itemsize
                overhead = datatype.Pack_size(0, self.COMM)
                for count in range(10):
                    pack_size = datatype.Pack_size(count, self.COMM)
                    self.assertEqual(pack_size - overhead, count*itemsize)

    def testPackUnpack(self):
        for array in arrayimpl.ArrayTypes:
            for typecode1, datatype1 in arrayimpl.TypeMap.items():
                for typecode2, datatype2 in arrayimpl.TypeMap.items():
                    for items in range(10):
                        # input and output arrays
                        iarray1 = array(range(items), typecode1)
                        iarray2 = array(range(items), typecode2)
                        oarray1 = array(items, typecode1, items)
                        oarray2 = array(items, typecode2, items)
                        # temp array for packing
                        size1 = datatype1.Pack_size(len(iarray1), self.COMM)
                        size2 = datatype2.Pack_size(len(iarray2), self.COMM)
                        tmpbuf = array(0, 'b', size1 + size2 + 1)
                        # pack input arrays
                        position = 0
                        position = datatype1.Pack(iarray1, tmpbuf, position, self.COMM)
                        position = datatype2.Pack(iarray2, tmpbuf, position, self.COMM)
                        # unpack output arrays
                        position = 0
                        position = datatype1.Unpack(tmpbuf, position, oarray1, self.COMM)
                        position = datatype2.Unpack(tmpbuf, position, oarray2, self.COMM)
                        # test
                        equal = array.allclose
                        self.assertTrue(equal(iarray1, oarray1))
                        self.assertTrue(equal(iarray2, oarray2))

EXT32 = 'external32'

class BaseTestPackExternal(object):

    skipdtype = []

    def testPackSize(self):
        for array in arrayimpl.ArrayTypes:
            for typecode, datatype in arrayimpl.TypeMap.items():
                itemsize = array(0, typecode).itemsize
                overhead = datatype.Pack_external_size(EXT32, 0)
                for count in range(10):
                    pack_size = datatype.Pack_external_size(EXT32, count)
                    real_size = pack_size - overhead

    def testPackUnpackExternal(self):
        for array in arrayimpl.ArrayTypes:
            for typecode1, datatype1 in arrayimpl.TypeMap.items():
                for typecode2, datatype2 in arrayimpl.TypeMap.items():
                    for items in range(1, 10):
                        if typecode1 in self.skipdtype: continue
                        if typecode2 in self.skipdtype: continue
                        # input and output arrays
                        if typecode1 == 'b':
                            iarray1 = array(127, typecode1, items)
                        else:
                            iarray1 = array(255, typecode1, items)
                        iarray2 = array(range(items), typecode2)
                        oarray1 = array(-1, typecode1, items)
                        oarray2 = array(-1, typecode2, items)
                        # temp array for packing
                        size1 = datatype1.Pack_external_size(EXT32, iarray1.size)
                        size2 = datatype2.Pack_external_size(EXT32, iarray2.size)
                        tmpbuf = array(0, 'b', size1 + size2 + 1)
                        # pack input arrays
                        position = 0
                        position = datatype1.Pack_external(EXT32, iarray1, tmpbuf, position)
                        position = datatype2.Pack_external(EXT32, iarray2, tmpbuf, position)
                        # unpack output arrays
                        position = 0
                        position = datatype1.Unpack_external(EXT32, tmpbuf, position, oarray1)
                        position = datatype2.Unpack_external(EXT32, tmpbuf, position, oarray2)
                        # test result
                        equal = array.allclose
                        self.assertTrue(equal(iarray1, oarray1))
                        self.assertTrue(equal(iarray2, oarray2))


class TestPackSelf(BaseTestPack, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestPackWorld(BaseTestPack, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestPackExternal(BaseTestPackExternal, unittest.TestCase):
    pass


_name, _version = MPI.get_vendor()
if _name == 'Open MPI':
    if _version < (1, 5, 0):
        del BaseTestPackExternal
        del TestPackExternal
elif _name in ('MPICH2', 'DeinoMPI'):
    BaseTestPackExternal.skipdtype += ['l']
    BaseTestPackExternal.skipdtype += ['d']
else:
    try:
        MPI.BYTE.Pack_external_size(EXT32, 0)
    except NotImplementedError:
        del BaseTestPackExternal
        del TestPackExternal


if __name__ == '__main__':
    unittest.main()
