from mpi4py import MPI
import mpiunittest as unittest

datatypes_c = [
MPI.CHAR, MPI.WCHAR,
MPI.SIGNED_CHAR, MPI.SHORT, MPI.INT, MPI.LONG,
MPI.UNSIGNED_CHAR, MPI.UNSIGNED_SHORT, MPI.UNSIGNED, MPI.UNSIGNED_LONG,
MPI.LONG_LONG, MPI.UNSIGNED_LONG_LONG,
MPI.FLOAT, MPI.DOUBLE, MPI.LONG_DOUBLE,
]
datatypes_c99 = [
MPI.C_BOOL,
MPI.INT8_T, MPI.INT16_T, MPI.INT32_T, MPI.INT64_T,
MPI.UINT8_T, MPI.UINT16_T, MPI.UINT32_T, MPI.UINT64_T,
MPI.C_COMPLEX, MPI.C_FLOAT_COMPLEX,
MPI.C_DOUBLE_COMPLEX, MPI.C_LONG_DOUBLE_COMPLEX,
]
datatypes_f = [
MPI.CHARACTER, MPI.LOGICAL, MPI.INTEGER,
MPI.REAL, MPI.DOUBLE_PRECISION,
MPI.COMPLEX, MPI.DOUBLE_COMPLEX,
]
datatypes_f90 = [
MPI.LOGICAL1, MPI.LOGICAL2, MPI.LOGICAL4, MPI.LOGICAL8,
MPI.INTEGER1, MPI.INTEGER2, MPI.INTEGER4, MPI.INTEGER8, MPI.INTEGER16,
MPI.REAL2, MPI.REAL4, MPI.REAL8, MPI.REAL16,
MPI.COMPLEX4, MPI.COMPLEX8, MPI.COMPLEX16, MPI.COMPLEX32,
]
datatypes_mpi = [
MPI.PACKED, MPI.BYTE, MPI.AINT, MPI.OFFSET,
]

datatypes = []
datatypes += datatypes_c
datatypes += datatypes_c99
datatypes += datatypes_f
datatypes += datatypes_f90
datatypes += datatypes_mpi
datatypes = [t for t in datatypes if t != MPI.DATATYPE_NULL]

combiner_map = {}

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

    def testGetEnvelope(self):
        for dtype in datatypes:
            try:
                envelope = dtype.Get_envelope()
            except NotImplementedError:
                return
            if ('LAM/MPI' == MPI.get_vendor()[0] and
                "COMPLEX" in dtype.name): continue
            ni, na, nd, combiner = envelope
            self.assertEqual(combiner, MPI.COMBINER_NAMED)
            self.assertEqual(ni, 0)
            self.assertEqual(na, 0)
            self.assertEqual(nd, 0)

    def _test_derived_contents(self, oldtype, factory, newtype):
        try:
            envelope = newtype.Get_envelope()
            contents = newtype.Get_contents()
        except NotImplementedError:
            return
        ni, na, nd, combiner = envelope
        i, a, d = contents
        self.assertEqual(ni, len(i))
        self.assertEqual(na, len(a))
        self.assertEqual(nd, len(d))
        self.assertTrue(combiner != MPI.COMBINER_NAMED)
        name = factory.__name__
        NAME = name.replace('Create_', '').upper()
        symbol = getattr(MPI, 'COMBINER_' + NAME)
        if symbol == MPI.UNDEFINED: return
        if combiner_map is None: return
        symbol = combiner_map.get(symbol, symbol)
        if symbol is None: return
        self.assertEqual(symbol, combiner)
        decoded = newtype.decode()
        oldtype, constructor, kargs = decoded
        constructor = 'Create_' + constructor.lower()
        if combiner in [MPI.COMBINER_CONTIGUOUS]:
            # Cython could optimize one-arg methods
            newtype2 = getattr(oldtype, constructor)(kargs['count'])
        else:
            newtype2 = getattr(oldtype, constructor)(**kargs)
        decoded2 = newtype2.decode()
        self.assertEqual(decoded[1], decoded2[1])
        self.assertEqual(decoded[2], decoded2[2])
        newtype2.Free()

    def _test_derived(self, oldtype, factory, *args):
        try:
            if isinstance(oldtype, MPI.Datatype):
                newtype = factory(oldtype, *args)
            else:
                newtype = factory(*args)
        except NotImplementedError:
            return
        self._test_derived_contents(oldtype, factory,  newtype)
        newtype.Commit()
        self._test_derived_contents(oldtype, factory,  newtype)
        newtype.Free()

    def testDup(self):
        for dtype in datatypes:
            factory = MPI.Datatype.Dup
            self._test_derived(dtype, factory)

    def testCreateContiguous(self):
        for dtype in datatypes:
            for count in range(5):
                factory = MPI.Datatype.Create_contiguous
                args = (count, )
                self._test_derived(dtype, factory, *args)

    def testCreateVector(self):
        for dtype in datatypes:
            for count in range(5):
                for blocklength in range(5):
                    for stride in range(5):
                        factory = MPI.Datatype.Create_vector
                        args = (count, blocklength, stride)
                        self._test_derived(dtype, factory, *args)

    def testCreateHvector(self):
        for dtype in datatypes:
            for count in range(5):
                for blocklength in range(5):
                    for stride in range(5):
                        factory = MPI.Datatype.Create_hvector
                        args = (count, blocklength, stride)
                        self._test_derived(dtype, factory, *args)

    def testCreateIndexed(self):
        for dtype in datatypes:
            for block in range(5):
                blocklengths = list(range(block, block+5))
                displacements = [0]
                for b in blocklengths[:-1]:
                    stride = displacements[-1] + b * dtype.extent + 1
                    displacements.append(stride)
                factory = MPI.Datatype.Create_indexed
                args = (blocklengths, displacements)
                self._test_derived(dtype, factory, *args)
                #args = (block, displacements) XXX
                #self._test_derived(dtype, factory, *args)  XXX

    def testCreateIndexedBlock(self):
        for dtype in datatypes:
            for block in range(5):
                blocklengths = list(range(block, block+5))
                displacements = [0]
                for b in blocklengths[:-1]:
                    stride = displacements[-1] + b * dtype.extent + 1
                    displacements.append(stride)
                factory = MPI.Datatype.Create_indexed_block
                args = (block, displacements)
                self._test_derived(dtype, factory, *args)

    def testCreateHindexed(self):
        for dtype in datatypes:
            for block in range(5):
                blocklengths = list(range(block, block+5))
                displacements = [0]
                for b in blocklengths[:-1]:
                    stride = displacements[-1] + b * dtype.extent + 1
                    displacements.append(stride)

                factory = MPI.Datatype.Create_hindexed
                args = (blocklengths, displacements)
                self._test_derived(dtype, factory, *args)
                #args = (block, displacements) XXX
                #self._test_derived(dtype, factory, *args)  XXX

    def testCreateStruct(self):
        for dtype1 in datatypes:
            for dtype2 in datatypes:
                dtypes = (dtype1, dtype2)
                blocklengths  = (2, 3)
                displacements = [0]
                for dtype in dtypes[:-1]:
                    stride = displacements[-1] + dtype.extent
                    displacements.append(stride)
                factory = MPI.Datatype.Create_struct
                args = (blocklengths, displacements, dtypes)
                self._test_derived(dtypes, factory, *args)

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
                                factory = MPI.Datatype.Create_subarray
                                args = sizes, subsizes, starts, order
                                self._test_derived(dtype, factory, *args)

    def testResized(self):
        for dtype in datatypes:
            for lb in range(-10, 10):
                for extent in range(1, 10):
                    factory = MPI.Datatype.Create_resized
                    args = lb, extent
                    self._test_derived(dtype, factory, *args)

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

import sys
_name, _version = MPI.get_vendor()
if _name == 'LAM/MPI':
    combiner_map[MPI.COMBINER_INDEXED_BLOCK] = MPI.COMBINER_INDEXED
elif _name == 'MPICH1':
    combiner_map[MPI.COMBINER_VECTOR]  = None
    combiner_map[MPI.COMBINER_HVECTOR] = None
    combiner_map[MPI.COMBINER_INDEXED] = None
    for t in datatypes_f: datatypes.remove(t)
elif MPI.Get_version() < (2, 0):
    combiner_map = None
if _name == 'Open MPI':
    if _version <= (1, 5, 1):
        for t in datatypes_f90[-4:]:
            if t != MPI.DATATYPE_NULL:
                datatypes.remove(t)
    if 'win' in sys.platform:
        del TestDatatype.testCommit
        del TestDatatype.testDup
        del TestDatatype.testResized

if sys.version_info[0] >=3:
    del TestGetAddress

if __name__ == '__main__':
    unittest.main()
