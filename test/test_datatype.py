from mpi4py import MPI
import mpiunittest as unittest
import struct

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

for typelist in [datatypes, datatypes_f, datatypes_f90]:
    typelist[:] = [
        t for t in datatypes
        if t != MPI.DATATYPE_NULL
        and t.Get_name() != 'MPI_DATATYPE_NULL'
        and t.Get_size() != 0
    ]
del typelist

combiner_map = {}

class TestDatatypeNull(unittest.TestCase):

    def testConstructor(self):
        datatype = MPI.Datatype()
        self.assertEqual(datatype, MPI.DATATYPE_NULL)
        self.assertIsNot(datatype, MPI.DATATYPE_NULL)
        def construct(): MPI.Datatype((1,2,3))
        self.assertRaises(TypeError, construct)

    def testGetName(self):
        name = MPI.DATATYPE_NULL.Get_name()
        self.assertEqual(name, "MPI_DATATYPE_NULL")

class TestDatatype(unittest.TestCase):

    def testBoolEqNe(self):
        for dtype in datatypes:
            self.assertTrue(not not dtype)
            eq = (dtype == MPI.Datatype(dtype))
            ne = (dtype != MPI.Datatype(dtype))
            self.assertTrue(eq)
            self.assertFalse(ne)

    def testGetExtent(self):
        for dtype in datatypes:
            lb, ext = dtype.Get_extent()
            self.assertEqual(dtype.lb, lb)
            self.assertEqual(dtype.ub, lb+ext)
            self.assertEqual(dtype.extent, ext)

    def testGetSize(self):
        for dtype in datatypes:
            size = dtype.Get_size()
            self.assertEqual(dtype.size, size)

    def testGetTrueExtent(self):
        for dtype in datatypes:
            try:
                lb, ext = dtype.Get_true_extent()
                self.assertEqual(dtype.true_lb, lb)
                self.assertEqual(dtype.true_ub, lb+ext)
                self.assertEqual(dtype.true_extent, ext)
            except NotImplementedError:
                self.skipTest('mpi-type-get_true_extent')

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

    def testGetValueIndex(self):
        typenames = ('SHORT', 'INT', 'LONG', 'FLOAT', 'DOUBLE', 'LONG_DOUBLE')
        value_types = [getattr(MPI, f'{attr}') for attr in typenames]
        pair_types = [getattr(MPI, f'{attr}_INT') for attr in typenames]
        for value, pair in zip(value_types, pair_types):
            result = MPI.Datatype.Get_value_index(value, MPI.INT)
            self.assertEqual(result, pair)
        for value in value_types:
            result = MPI.Datatype.Get_value_index(value, MPI.FLOAT)
            self.assertEqual(result, MPI.DATATYPE_NULL)

    def testGetEnvelope(self):
        for dtype in datatypes:
            try:
                envelope = dtype.Get_envelope()
            except NotImplementedError:
                self.skipTest('mpi-type-get_envelope')
            if ('LAM/MPI' == MPI.get_vendor()[0] and
                "COMPLEX" in dtype.name):
                continue
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
            otype, combiner, params = dtype.decode()
            self.assertIs(dtype, otype)
            self.assertEqual(combiner, "NAMED")
            self.assertEqual(params, {})

    def testGetSetName(self):
        name = MPI.DATATYPE_NULL.Get_name()
        self.assertEqual(name, "MPI_DATATYPE_NULL")
        for dtype in datatypes:
            try:
                name = dtype.Get_name()
                self.assertTrue(name)
                dtype.Set_name(name)
                self.assertEqual(name, dtype.Get_name())
                dtype.name = dtype.name
            except NotImplementedError:
                self.skipTest('mpi-type-name')

    def testCommit(self):
        for dtype in datatypes:
            dtype.Commit()

    def testCodeCharStr(self):
        f90datatypes = []
        try:
            try:
                for r in (1, 2, 4):
                    f90datatypes.append(MPI.Datatype.Create_f90_integer(r))
                for p, r in ((6, 30), (15,  300)):
                    f90datatypes.append(MPI.Datatype.Create_f90_real(p, r))
                    f90datatypes.append(MPI.Datatype.Create_f90_complex(p, r))
            except MPI.Exception:
                if not unittest.is_mpi('msmpi'): raise
            f90datatypes = [
                dtype for dtype in f90datatypes
                if dtype and dtype.size > 0
            ]
        except NotImplementedError:
            f90datatypes = []
            pass
        largef90datatypes = []
        if MPI.INTEGER16 != MPI.DATATYPE_NULL:
            largef90datatypes += [MPI.INTEGER16]
        if struct.calcsize('P') == 4 or MPI.DOUBLE.extent == MPI.LONG_DOUBLE.extent:
            largef90datatypes += [MPI.REAL16,  MPI.COMPLEX32]
        for dtype in datatypes + f90datatypes:
            with self.subTest(datatype=dtype.name or "f90"):
                if dtype in largef90datatypes: continue
                code = dtype.tocode()
                self.assertIsNotNone(code)
                mpitype = MPI.Datatype.fromcode(code)
                self.assertEqual(dtype.typechar, mpitype.typechar)
                self.assertEqual(dtype.typestr,  mpitype.typestr)
                try:
                    mpitypedup1 = mpitype.Dup()
                    self.assertEqual(mpitypedup1.tocode(), mpitype.tocode())
                    self.assertEqual(mpitypedup1.typestr,  mpitype.typestr)
                    self.assertEqual(mpitypedup1.typechar, mpitype.typechar)
                    mpitypedup2 = mpitypedup1.Dup()
                    self.assertEqual(mpitypedup2.tocode(), mpitype.tocode())
                    self.assertEqual(mpitypedup2.typestr,  mpitype.typestr)
                    self.assertEqual(mpitypedup2.typechar, mpitype.typechar)
                finally:
                    mpitypedup1.Free()
                    mpitypedup2.Free()
        with self.assertRaises(ValueError):
            MPI.Datatype.fromcode("abc@xyz")
        with self.assertRaises(ValueError):
            MPI.DATATYPE_NULL.tocode()
        with self.assertRaises(ValueError):
            MPI.INT_INT.tocode()
        self.assertEqual(MPI.INT_INT.typechar, 'V')
        self.assertEqual(MPI.INT_INT.typestr, f'V{MPI.INT.extent*2}')


class BaseTestDatatypeCreateMixin:

    def free(self, newtype):
        if newtype == MPI.DATATYPE_NULL: return
        *_, combiner = newtype.Get_envelope()
        if combiner in (
            MPI.COMBINER_NAMED,
            MPI.COMBINER_F90_INTEGER,
            MPI.COMBINER_F90_REAL,
            MPI.COMBINER_F90_COMPLEX,
        ): return
        newtype.Free()

    def check_contents(self, factory, newtype, oldtype):
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
        self.assertNotEqual(combiner, MPI.COMBINER_NAMED)
        self.assertEqual(newtype.envelope, envelope)
        self.assertEqual(newtype.combiner, combiner)
        self.assertFalse(newtype.is_named)
        if combiner in (MPI.COMBINER_F90_INTEGER,
                        MPI.COMBINER_F90_REAL,
                        MPI.COMBINER_F90_COMPLEX,):
            self.assertTrue(newtype.is_predefined)
        else:
            self.assertFalse(newtype.is_predefined)
        for dt in d:
            self.free(dt)
        contents = newtype.contents
        self.assertEqual(contents[:-1], (i, a, c))
        for dt in contents[-1]:
            self.free(dt)

    def check_recreate(self, factory, newtype):
        name = factory.__name__
        name = name.replace('Get_value_index', 'Create_value_index')
        NAME = name.replace('Create_', '').upper()
        symbol = getattr(MPI, 'COMBINER_' + NAME)
        if symbol == MPI.UNDEFINED: return
        if combiner_map is None: return
        symbol = combiner_map.get(symbol, symbol)
        if symbol is None: return
        self.assertEqual(symbol, newtype.combiner)
        decoded1 = newtype.decode()
        oldtype, constructor, kwargs = decoded1
        prefix = 'create' if constructor != 'VALUE_INDEX' else 'get'
        constructor = prefix.title() + '_' + constructor.lower()
        newtype2 = getattr(oldtype, constructor)(**kwargs)
        decoded2 = newtype2.decode()
        types1 = decoded1[2].pop('datatypes', [])
        types2 = decoded2[2].pop('datatypes', [])
        for dt1, dt2 in zip(types1, types2):
            self.assertEqual(dt1.combiner, dt2.combiner)
            self.assertEqual(dt1.typechar, dt2.typechar)
            self.assertEqual(dt1.typestr,  dt2.typestr)
            self.free(dt1)
            self.free(dt2)
        self.assertEqual(decoded1[1], decoded2[1])
        self.assertEqual(decoded2[2], decoded2[2])
        for dec in (decoded1, decoded2):
            self.free(dec[0])
        self.free(newtype2)

    def testDup(self):
        for dtype in datatypes:
            factory = MPI.Datatype.Dup
            self.check(dtype, factory)

    def testContiguous(self):
        for dtype in datatypes:
            for count in range(5):
                factory = MPI.Datatype.Create_contiguous
                args = (count, )
                self.check(dtype, factory, *args)

    def testVector(self):
        for dtype in datatypes:
            for count in range(5):
                for blocklength in range(5):
                    for stride in range(5):
                        factory = MPI.Datatype.Create_vector
                        args = (count, blocklength, stride)
                        self.check(dtype, factory, *args)

    def testHvector(self):
        for dtype in datatypes:
            for count in range(5):
                for blocklength in range(5):
                    for stride in range(5):
                        factory = MPI.Datatype.Create_hvector
                        args = (count, blocklength, stride)
                        self.check(dtype, factory, *args)

    def testIndexed(self):
        for dtype in datatypes:
            for block in range(5):
                blocklengths = list(range(block, block+5))
                displacements = [0]
                for b in blocklengths[:-1]:
                    stride = displacements[-1] + b * dtype.extent + 1
                    displacements.append(stride)
                factory = MPI.Datatype.Create_indexed
                args = (blocklengths, displacements)
                self.check(dtype, factory, *args)
                #args = (block, displacements) XXX
                #self.check(dtype, factory, *args)  XXX

    def testIndexedBlock(self):
        for dtype in datatypes:
            for block in range(5):
                blocklengths = list(range(block, block+5))
                displacements = [0]
                for b in blocklengths[:-1]:
                    stride = displacements[-1] + b * dtype.extent + 1
                    displacements.append(stride)
                factory = MPI.Datatype.Create_indexed_block
                args = (block, displacements)
                self.check(dtype, factory, *args)

    def testHindexed(self):
        for dtype in datatypes:
            for block in range(5):
                blocklengths = list(range(block, block+5))
                displacements = [0]
                for b in blocklengths[:-1]:
                    stride = displacements[-1] + b * dtype.extent + 1
                    displacements.append(stride)

                factory = MPI.Datatype.Create_hindexed
                args = (blocklengths, displacements)
                self.check(dtype, factory, *args)
                #args = (block, displacements) XXX
                #self.check(dtype, factory, *args)  XXX

    @unittest.skipMPI('openmpi(<=1.8.1)', MPI.VERSION == 3)
    def testHindexedBlock(self):
        for dtype in datatypes:
            for block in range(5):
                displacements = [0]
                for i in range(5):
                    stride = displacements[-1] + block * dtype.extent + 1
                    displacements.append(stride)
                factory = MPI.Datatype.Create_hindexed_block
                args = (block, displacements)
                self.check(dtype, factory, *args)

    def testStruct(self):
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
                self.check(None, factory, *args)
        for dtype in datatypes:
            factory = MPI.Datatype.Create_struct
            dtypes = [dtype.Dup()]
            dtypes.append(dtypes[-1].Create_contiguous(2))
            dtypes.append(dtypes[-1].Dup())
            dtypes.append(dtypes[-1].Create_struct([1],[0],[dtypes[-1]]))
            dtypes.append(dtypes[-1].Dup())
            dtypes.append(dtypes[-1].Create_resized(0, dtypes[-1].extent))
            dtypes.append(dtypes[-1].Dup())
            for dt in dtypes:
                args = [[1, 1], [0, dt.extent*2], (dt, dt)]
                self.check(None, factory, *args)
                dt.Free()
        with self.assertRaises(ValueError):
            factory = MPI.Datatype.Create_struct
            factory([1], [0], [MPI.INT, MPI.FLOAT])

    def testSubarray(self):
        for dtype in datatypes:
            for ndim in range(1, 5):
                for size in range(1, 5):
                    for subsize in range(1, size):
                        for start in range(size-subsize):
                            for order in [
                                MPI.ORDER_C,
                                MPI.ORDER_FORTRAN,
                                MPI.ORDER_F,
                            ]:
                                sizes = [size] * ndim
                                subsizes = [subsize] * ndim
                                starts = [start] * ndim
                                factory = MPI.Datatype.Create_subarray
                                args = sizes, subsizes, starts, order
                                self.check(dtype, factory, *args)

    def testDarray(self):
        for dtype in datatypes:
            for ndim in range(1, 3+1):
                for size in (4, 8, 9, 27):
                    for rank in (0, size-1):
                        for dist in [
                            MPI.DISTRIBUTE_BLOCK,
                            MPI.DISTRIBUTE_CYCLIC
                        ]:
                            for order in [MPI.ORDER_C, MPI.ORDER_F]:
                                gsizes = [size]*ndim
                                distribs = [dist]*ndim
                                dargs = [MPI.DISTRIBUTE_DFLT_DARG]*ndim
                                psizes = MPI.Compute_dims(size, [0]*ndim)
                                factory = MPI.Datatype.Create_darray
                                args = (
                                    size, rank,
                                    gsizes, distribs,
                                    dargs, psizes, order,
                                )
                                self.check(dtype, factory, *args)

    def testF90Integer(self):
        for r in (1, 2, 4):
            factory = MPI.Datatype.Create_f90_integer
            args = (r,)
            self.check(None, factory, *args)

    @unittest.skipMPI('openmpi(<3.0.0)')
    @unittest.skipMPI('msmpi')
    def testF90RealSingle(self):
        (p, r) = (6, 30)
        factory = MPI.Datatype.Create_f90_real
        args = (p, r)
        self.check(None, factory, *args)

    @unittest.skipMPI('openmpi(<3.0.0)')
    @unittest.skipMPI('msmpi')
    def testF90RealDouble(self):
        (p, r) = (15, 300)
        factory = MPI.Datatype.Create_f90_real
        args = (p, r)
        self.check(None, factory, *args)

    @unittest.skipMPI('openmpi(<3.0.0)')
    @unittest.skipMPI('msmpi')
    def testF90ComplexSingle(self):
        (p, r) = (6, 30)
        factory = MPI.Datatype.Create_f90_complex
        args = (p, r)
        self.check(None, factory, *args)

    @unittest.skipMPI('openmpi(<3.0.0)')
    @unittest.skipMPI('msmpi')
    def testF90ComplexDouble(self):
        (p, r) = (15, 300)
        factory = MPI.Datatype.Create_f90_complex
        args = (p, r)
        self.check(None, factory, *args)

    def testResized(self):
        for dtype in datatypes:
            for lb in range(-10, 10):
                for extent in range(1, 10):
                    factory = MPI.Datatype.Create_resized
                    args = lb, extent
                    self.check(dtype, factory, *args)

    def testValueIndex(self):
        integral_types = datatypes_c[2:-3] + datatypes_c99[1:9]
        floating_types = datatypes_c[-3:]
        value_types = integral_types + floating_types
        index_types = integral_types
        for value in value_types:
            if value == MPI.DATATYPE_NULL: continue
            for index in index_types:
                if index == MPI.DATATYPE_NULL: continue
                factory = MPI.Datatype.Get_value_index
                pair = factory(value, index)
                if pair == MPI.DATATYPE_NULL: continue
                if pair.is_named: continue
                self.check(None, factory, value, index)


class TestDatatypeCreate(BaseTestDatatypeCreateMixin, unittest.TestCase):

    def check(self, oldtype, factory, *args):
        try:
            if oldtype is not None:
                newtype = factory(oldtype, *args)
            else:
                newtype = factory(*args)
            if newtype == MPI.DATATYPE_NULL:
                return
        except NotImplementedError:
            self.skipTest('mpi-type-constructor')
        self.check_contents(factory, newtype, oldtype)
        self.check_recreate(factory, newtype)
        newtype.Commit()
        self.check_contents(factory, newtype, oldtype)
        self.check_recreate(factory, newtype)
        self.free(newtype)


class TestDatatypePickle(BaseTestDatatypeCreateMixin, unittest.TestCase):

    def check(self, oldtype, factory, *args):
        from pickle import dumps, loads
        try:
            if oldtype is not None:
                newtype0 = factory(oldtype, *args)
            else:
                newtype0 = factory(*args)
            if newtype0 == MPI.DATATYPE_NULL:
                return
        except NotImplementedError:
            self.skipTest('mpi-type-constructor')
        newtype1 = loads(dumps(newtype0))
        self.check_contents(factory, newtype1, oldtype)
        self.free(newtype1)
        self.free(newtype0)


    def testNamed(self):
        from pickle import dumps, loads
        for dtype in [MPI.DATATYPE_NULL] + datatypes:
            newdtype = loads(dumps(dtype))
            self.assertIs(newdtype, dtype)
            newdtype = loads(dumps(MPI.Datatype(dtype)))
            self.assertIsNot(newdtype, dtype)
            self.assertEqual(newdtype, dtype)


name, version = MPI.get_vendor()
if name == 'LAM/MPI':
    combiner_map[MPI.COMBINER_INDEXED_BLOCK] = MPI.COMBINER_INDEXED
elif name == 'MPICH1':
    combiner_map[MPI.COMBINER_VECTOR]  = None
    combiner_map[MPI.COMBINER_HVECTOR] = None
    combiner_map[MPI.COMBINER_INDEXED] = None
    combiner_map[MPI.COMBINER_HINDEXED_BLOCK] = None
    for t in datatypes_f:
        if t in datatypes:
            datatypes.remove(t)
        if t in datatypes_f:
            datatypes_f.remove(t)
elif MPI.Get_version() < (2,0):
    combiner_map = None
if name == 'Open MPI':
    if (1,6,0) < version < (1,7,0):
        TestDatatype.match_size_complex[:] = []
    if version < (1,5,2):
        for t in [getattr(MPI, f'COMPLEX{i}') for i in (4, 8, 16, 32)]:
            if t in datatypes:
                datatypes.remove(t)
            if t in datatypes_f90:
                datatypes_f90.remove(t)


if __name__ == '__main__':
    unittest.main()
