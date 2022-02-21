from mpi4py import MPI
import mpiunittest as unittest
import sys

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

    def testBoolEqNe(self):
        for dtype in datatypes:
            self.assertTrue (not not dtype)
            self.assertTrue (dtype == MPI.Datatype(dtype))
            self.assertFalse(dtype != MPI.Datatype(dtype))

    def testGetExtent(self):
        for dtype in datatypes:
            lb, ext = dtype.Get_extent()
            self.assertEqual(dtype.lb, lb)
            self.assertEqual(dtype.ub, lb+ext)
            self.assertEqual(dtype.extent, ext)

    def testGetSize(self):
        for dtype in datatypes:
            size = dtype.Get_size()
            self.assertTrue(dtype.size, size)

    def testGetTrueExtent(self):
        for dtype in datatypes:
            try:
                lb, ext = dtype.Get_true_extent()
                self.assertEqual(dtype.true_lb, lb)
                self.assertEqual(dtype.true_ub, lb+ext)
                self.assertEqual(dtype.true_extent, ext)
            except NotImplementedError:
                self.skipTest('mpi-type-get_true_extent')

    def testGetEnvelope(self):
        for dtype in datatypes:
            try:
                envelope = dtype.Get_envelope()
            except NotImplementedError:
                self.skipTest('mpi-type-get_envelope')
            if ('LAM/MPI' == MPI.get_vendor()[0] and
                "COMPLEX" in dtype.name): continue
            ni, na, nc, nd, combiner = envelope
            self.assertEqual(combiner, MPI.COMBINER_NAMED)
            self.assertEqual(ni, 0)
            self.assertEqual(na, 0)
            self.assertEqual(nc, 0)
            self.assertEqual(nd, 0)
            self.assertEqual(dtype.envelope, envelope)
            self.assertEqual(dtype.combiner, combiner)
            self.assertTrue(dtype.is_named)
            self.assertTrue(dtype.is_predefined)
            otype = dtype.decode()
            self.assertTrue(dtype is otype)

    def check_datatype_contents(self, oldtype, factory, newtype):
        try:
            envelope = newtype.Get_envelope()
            contents = newtype.Get_contents()
        except NotImplementedError:
            self.skipTest('mpi-type-get_envelope')
        ni, na, nc, nd, combiner = envelope
        i, a, c, d = contents
        self.assertEqual(ni, len(i))
        self.assertEqual(na, len(a))
        self.assertEqual(nc, len(c))
        self.assertEqual(nd, len(d))
        self.assertTrue(combiner != MPI.COMBINER_NAMED)
        self.assertEqual(newtype.envelope, envelope)
        self.assertEqual(newtype.contents, contents)
        self.assertEqual(newtype.combiner, combiner)
        self.assertFalse(newtype.is_named)
        if combiner in (MPI.COMBINER_F90_INTEGER,
                        MPI.COMBINER_F90_REAL,
                        MPI.COMBINER_F90_COMPLEX,):
            self.assertTrue(newtype.is_predefined)
        else:
            self.assertFalse(newtype.is_predefined)
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
        newtype2 = getattr(oldtype, constructor)(**kargs)
        decoded2 = newtype2.decode()
        self.assertEqual(decoded[1], decoded2[1])
        self.assertEqual(decoded[2], decoded2[2])
        if combiner not in (MPI.COMBINER_F90_INTEGER,
                            MPI.COMBINER_F90_REAL,
                            MPI.COMBINER_F90_COMPLEX,):
            self.assertFalse(newtype2.is_predefined)
            newtype2.Free()
        else:
            self.assertTrue(newtype2.is_predefined)

    def check_datatype(self, oldtype, factory, *args):
        try:
            if isinstance(oldtype, MPI.Datatype):
                newtype = factory(oldtype, *args)
            else:
                newtype = factory(*args)
        except NotImplementedError:
            self.skipTest('mpi-type-constructor')
        self.check_datatype_contents(oldtype, factory,  newtype)
        newtype.Commit()
        self.check_datatype_contents(oldtype, factory,  newtype)
        combiner = newtype.Get_envelope()[-1]
        if combiner not in (MPI.COMBINER_F90_INTEGER,
                            MPI.COMBINER_F90_REAL,
                            MPI.COMBINER_F90_COMPLEX,):
            newtype.Free()

    def testDup(self):
        for dtype in datatypes:
            factory = MPI.Datatype.Dup
            self.check_datatype(dtype, factory)

    def testCreateContiguous(self):
        for dtype in datatypes:
            for count in range(5):
                factory = MPI.Datatype.Create_contiguous
                args = (count, )
                self.check_datatype(dtype, factory, *args)

    def testCreateVector(self):
        for dtype in datatypes:
            for count in range(5):
                for blocklength in range(5):
                    for stride in range(5):
                        factory = MPI.Datatype.Create_vector
                        args = (count, blocklength, stride)
                        self.check_datatype(dtype, factory, *args)

    def testCreateHvector(self):
        for dtype in datatypes:
            for count in range(5):
                for blocklength in range(5):
                    for stride in range(5):
                        factory = MPI.Datatype.Create_hvector
                        args = (count, blocklength, stride)
                        self.check_datatype(dtype, factory, *args)

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
                self.check_datatype(dtype, factory, *args)
                #args = (block, displacements) XXX
                #self.check_datatype(dtype, factory, *args)  XXX

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
                self.check_datatype(dtype, factory, *args)

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
                self.check_datatype(dtype, factory, *args)
                #args = (block, displacements) XXX
                #self.check_datatype(dtype, factory, *args)  XXX

    @unittest.skipMPI('openmpi(<=1.8.1)', MPI.VERSION == 3)
    def testCreateHindexedBlock(self):
        for dtype in datatypes:
            for block in range(5):
                displacements = [0]
                for i in range(5):
                    stride = displacements[-1] + block * dtype.extent + 1
                    displacements.append(stride)
                factory = MPI.Datatype.Create_hindexed_block
                args = (block, displacements)
                self.check_datatype(dtype, factory, *args)

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
                self.check_datatype(dtypes, factory, *args)

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
                                self.check_datatype(dtype, factory, *args)

    def testCreateDarray(self):
        for dtype in datatypes:
            for ndim in range(1, 3+1):
                for size in (4, 8, 9, 27):
                    for rank in (0, size-1):
                        for dist in [MPI.DISTRIBUTE_BLOCK, MPI.DISTRIBUTE_CYCLIC]:
                            for order in [MPI.ORDER_C, MPI.ORDER_F]:
                                gsizes = [size]*ndim
                                distribs = [dist]*ndim
                                dargs = [MPI.DISTRIBUTE_DFLT_DARG]*ndim
                                psizes = MPI.Compute_dims(size, [0]*ndim)
                                factory = MPI.Datatype.Create_darray
                                args = size, rank, gsizes, distribs, dargs, psizes, order
                                self.check_datatype(dtype, factory, *args)

    def testCreateF90Integer(self):
        for r in (1, 2, 4):
            factory = MPI.Datatype.Create_f90_integer
            args = (r,)
            self.check_datatype(None, factory, *args)

    @unittest.skipMPI('openmpi(<3.0.0)')
    @unittest.skipMPI('msmpi')
    @unittest.skipMPI('SpectrumMPI')
    def testCreateF90RealSingle(self):
        (p, r) = (6, 30)
        factory = MPI.Datatype.Create_f90_real
        args = (p, r)
        self.check_datatype(None, factory, *args)

    @unittest.skipMPI('openmpi(<3.0.0)')
    @unittest.skipMPI('msmpi')
    @unittest.skipMPI('SpectrumMPI')
    def testCreateF90RealDouble(self):
        (p, r) = (15, 300)
        factory = MPI.Datatype.Create_f90_real
        args = (p, r)
        self.check_datatype(None, factory, *args)

    @unittest.skipMPI('openmpi(<3.0.0)')
    @unittest.skipMPI('msmpi')
    @unittest.skipMPI('SpectrumMPI')
    def testCreateF90ComplexSingle(self):
        (p, r) = (6, 30)
        factory = MPI.Datatype.Create_f90_complex
        args = (p, r)
        self.check_datatype(None, factory, *args)

    @unittest.skipMPI('openmpi(<3.0.0)')
    @unittest.skipMPI('msmpi')
    @unittest.skipMPI('SpectrumMPI')
    def testCreateF90ComplexDouble(self):
        (p, r) = (15, 300)
        factory = MPI.Datatype.Create_f90_complex
        args = (p, r)
        self.check_datatype(None, factory, *args)

    match_size_integer = [1, 2, 4, 8]
    match_size_real    = [4, 8]
    match_size_complex = [8, 16]
    @unittest.skipMPI('MPI(<2.0)')
    @unittest.skipMPI('openmpi', (MPI.CHARACTER == MPI.DATATYPE_NULL or
                                  MPI.CHARACTER.Get_size() == 0))
    def testMatchSize(self):
        typeclass = MPI.TYPECLASS_INTEGER
        for size in self.match_size_integer:
            datatype = MPI.Datatype.Match_size(typeclass, size)
            self.assertEqual(size, datatype.size)
        typeclass = MPI.TYPECLASS_REAL
        for size in self.match_size_real:
            datatype = MPI.Datatype.Match_size(typeclass, size)
            self.assertEqual(size, datatype.size)
        typeclass  = MPI.TYPECLASS_COMPLEX
        for size in self.match_size_complex:
            datatype = MPI.Datatype.Match_size(typeclass, size)
            self.assertEqual(size, datatype.size)

    def testCreateResized(self):
        for dtype in datatypes:
            for lb in range(-10, 10):
                for extent in range(1, 10):
                    factory = MPI.Datatype.Create_resized
                    args = lb, extent
                    self.check_datatype(dtype, factory, *args)

    def testGetSetName(self):
        for dtype in datatypes:
            try:
                name = dtype.Get_name()
                self.assertTrue(name)
                dtype.Set_name(name)
                self.assertEqual(name, dtype.Get_name())
            except NotImplementedError:
                self.skipTest('mpi-type-name')

    def testCommit(self):
        for dtype in datatypes:
            dtype.Commit()


name, version = MPI.get_vendor()
if name == 'LAM/MPI':
    combiner_map[MPI.COMBINER_INDEXED_BLOCK] = MPI.COMBINER_INDEXED
elif name == 'MPICH1':
    combiner_map[MPI.COMBINER_VECTOR]  = None
    combiner_map[MPI.COMBINER_HVECTOR] = None
    combiner_map[MPI.COMBINER_INDEXED] = None
    combiner_map[MPI.COMBINER_HINDEXED_BLOCK] = None
    for t in datatypes_f: datatypes.remove(t)
elif MPI.Get_version() < (2,0):
    combiner_map = None
if name == 'Open MPI':
    for t in datatypes_f + datatypes_f90:
        if t != MPI.DATATYPE_NULL:
            if t.Get_size() == 0:
                if t in datatypes:
                    datatypes.remove(t)
    if (1,6,0) < version < (1,7,0):
        TestDatatype.match_size_complex[:] = []
    if version < (1,5,2):
        for t in datatypes_f90[-4:]:
            if t != MPI.DATATYPE_NULL:
                datatypes.remove(t)
if name == 'Platform MPI':
    combiner_map[MPI.COMBINER_INDEXED_BLOCK] = MPI.COMBINER_INDEXED
    combiner_map[MPI.COMBINER_DARRAY] = MPI.COMBINER_STRUCT
    combiner_map[MPI.COMBINER_SUBARRAY] = MPI.COMBINER_STRUCT
    TestDatatype.match_size_complex[:] = []


if __name__ == '__main__':
    unittest.main()
