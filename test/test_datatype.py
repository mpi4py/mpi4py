from mpi4py import MPI
import mpiunittest as unittest

datatypes = (MPI.CHAR,  MPI.SHORT,
             MPI.INT,   MPI.LONG,
             MPI.FLOAT, MPI.DOUBLE)

class TestDatatype(unittest.TestCase):

    def testGetExtent(self):
        for dtype in datatypes:
            lb, ext = dtype.Get_extent()

    def testGetSize(self):
        for dtype in datatypes:
            size = dtype.Get_size()

    def testGetTrueExtent(self):
        for dtype in datatypes:
            try:
                lb, ext = dtype.Get_true_extent()
            except NotImplementedError:
                return

    def _create(self, factory, *args):
        try:
            newtype = factory(*args)
        except NotImplementedError:
            return
        newtype.Commit()
        newtype.Free()

    def testDup(self):
        for dtype in datatypes:
            factory = dtype.Dup
            self._create(factory)

    def testCreateContiguous(self):
        for dtype in datatypes:
            for count in range(5):
                factory = dtype.Create_contiguous
                args = (count, )
                self._create(factory, *args)

    def testCreateVector(self):
        for dtype in datatypes:
            for count in range(5):
                for blocklength in range(5):
                    for stride in range(5):
                        factory = dtype.Create_vector
                        args = (count, blocklength, stride)
                        self._create(factory, *args)

    def testCreateHvector(self):
        for dtype in datatypes:
            for count in range(5):
                for blocklength in range(5):
                    for stride in range(5):
                        factory = dtype.Create_hvector
                        args = (count, blocklength, stride)
                        self._create(factory, *args)

    def testCreateIndexed(self):
        for dtype in datatypes:
            for block in range(5):
                blocklengths = list(range(block, block+5))
                displacements = [0]
                for b in blocklengths[:-1]:
                    stride = displacements[-1] + b * dtype.extent + 1
                    displacements.append(stride)
                factory = dtype.Create_indexed
                args = (blocklengths, displacements)
                self._create(factory, *args)
                #args = (block, displacements) XXX
                #self._create(factory, *args)  XXX

    def testCreateIndexedBlock(self):
        for dtype in datatypes:
            for block in range(5):
                blocklengths = list(range(block, block+5))
                displacements = [0]
                for b in blocklengths[:-1]:
                    stride = displacements[-1] + b * dtype.extent + 1
                    displacements.append(stride)
                factory = dtype.Create_indexed_block
                args = (block, displacements)
                self._create(factory, *args)

    def testCreateHindexed(self):
        for dtype in datatypes:
            for block in range(5):
                blocklengths = list(range(block, block+5))
                displacements = [0]
                for b in blocklengths[:-1]:
                    stride = displacements[-1] + b * dtype.extent + 1
                    displacements.append(stride)

                factory = dtype.Create_hindexed
                args = (blocklengths, displacements)
                self._create(factory, *args)
                #args = (block, displacements) XXX
                #self._create(factory, *args)  XXX

    def testCreateStruct(self):
        dtypes = datatypes
        for dtype1 in datatypes:
            for dtype2 in datatypes:
                for dtype3 in datatypes:
                    dtypes = (dtype1, dtype2, dtype3)
                    blocklengths  = list(range(1, len(dtypes) + 1))
                    displacements = [0]
                    for dtype in dtypes[:-1]:
                        stride = displacements[-1] + dtype.extent
                        displacements.append(stride)
                    factory = MPI.Datatype.Create_struct
                    args = (blocklengths, displacements, dtypes)
                    self._create(factory, *args)

    def testCreateSubarray(self):
        for dtype in datatypes:
            for ndim in range(1, 5):
                for size in range(1, 5):
                    for subsize in range(1, size):
                        for start in range(size-subsize):
                            for order in [MPI.ORDER_C,
                                          MPI.ORDER_FORTRAN,
                                          MPI.ORDER_F,
                                          ]:
                                sizes = [size] * ndim
                                subsizes = [subsize] * ndim
                                starts = [start] * ndim
                                factory = dtype.Create_subarray
                                args = sizes, subsizes, starts, order
                                self._create(factory, *args)

    def testResized(self):
        for dtype in datatypes:
            for lb in range(-10, 10):
                for extent in range(1, 10):
                    factory = dtype.Resized
                    args = lb, extent
                    self._create(factory, *args)

    def testGetSetName(self):
        for dtype in datatypes:
            try:
                name = dtype.Get_name()
                self.assertTrue(name)
                dtype.Set_name(name)
                self.assertEqual(name, dtype.Get_name())
            except NotImplementedError:
                return


    def testCommit(self):
        for dtype in datatypes:
            dtype.Commit()


class TestGetAddress(unittest.TestCase):

    def testGetAddress(self):
        from array import array
        location = array('i', range(10))
        addr = MPI.Get_address(location)
        bufptr, buflen = location.buffer_info()
        self.assertEqual(addr, bufptr)


if __name__ == '__main__':
    unittest.main()
