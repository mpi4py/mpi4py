from mpi4py import MPI
from mpi4py.util.dtlib import from_numpy_dtype as fromnumpy
from mpi4py.util.dtlib import to_numpy_dtype   as tonumpy
import itertools
import os
import sys
try:
    import mpiunittest as unittest
    import mpitestutil as testutil
except ImportError:
    sys.path.append(
        os.path.dirname(
            os.path.abspath(__file__)))
    import mpiunittest as unittest
    import mpitestutil as testutil

try:
    import numpy
    np_dtype = numpy.dtype
    np_version = tuple(map(int, numpy.__version__.split('.', 2)[:2]))
except ImportError:
    numpy = None
    np_dtype = None
    np_version = None

typecodes = list("?cbhilqpBHILQPefdgFDG")
typecodes += [f'b{n:d}' for n in (1,)]
typecodes += [f'i{n:d}' for n in (1,2,4,8)]
typecodes += [f'u{n:d}' for n in (1,2,4,8)]
typecodes += [f'f{n:d}' for n in (2,4,8)]
if os.environ.get('COVERAGE_RUN') == 'true':
    typecodes = list("cif") + ['b1', 'i8', 'f8']

if np_version and np_version < (1, 17):
    for tc in 'LFDG':
        if tc in typecodes:
            typecodes.remove(tc)

if (
    MPI.FLOAT16_T == MPI.DATATYPE_NULL
    or unittest.is_mpi('mpich(<5.0.0)')
    or unittest.is_mpi('openmpi(<5.0.0)')
    or unittest.is_mpi('impi')
):
    for tc in ('e', 'f2'):
        if tc in typecodes:
            typecodes.remove(tc)

if unittest.is_mpi('mpich(<4.0.0)'):
    for tc in 'FDG':
        if tc in typecodes:
            typecodes.remove(tc)

if unittest.is_mpi('impi(>=2021.12.0)') and os.name == 'nt':
    for tc in (*'lLg', 'i4', 'u4'):
        if tc in typecodes:
            typecodes.remove(tc)

datatypes_c = [
    MPI.Datatype.fromcode(t)
    for t in typecodes
] + [
    MPI.BYTE,
    MPI.AINT,
    MPI.OFFSET,
    MPI.COUNT,
]

mpipairtypes = [
    MPI.SHORT_INT,
    MPI.INT_INT,
    MPI.LONG_INT,
    MPI.FLOAT_INT,
    MPI.DOUBLE_INT,
    MPI.LONG_DOUBLE_INT,
]

mpif77types = [
    MPI.CHARACTER,
    MPI.LOGICAL,
    MPI.INTEGER,
    MPI.REAL,
    MPI.DOUBLE_PRECISION,
    MPI.COMPLEX,
    MPI.DOUBLE_COMPLEX,
]

mpif90types = [
    MPI.LOGICAL1,
    MPI.LOGICAL2,
    MPI.LOGICAL4,
    MPI.LOGICAL8,
    MPI.LOGICAL16,
    MPI.INTEGER1,
    MPI.INTEGER2,
    MPI.INTEGER4,
    MPI.INTEGER8,
    MPI.INTEGER16,
    MPI.REAL2,
    MPI.REAL4,
    MPI.REAL8,
    MPI.REAL16,
    MPI.COMPLEX4,
    MPI.COMPLEX8,
    MPI.COMPLEX16,
    MPI.COMPLEX32,
]

for typelist in [
    datatypes_c,
    mpif77types,
    mpif90types,
]:
    typelist[:] = [
        t for t in typelist
        if testutil.has_datatype(t)
    ]
del typelist

datatypes = []
datatypes += datatypes_c
datatypes += mpif77types
datatypes += mpif90types


def try_dtype(*args):
    for spec in args:
        if isinstance(spec, MPI.Datatype):
            spec = spec.typestr
        if np_dtype is not None:
            try:
                np_dtype(spec)
            except TypeError:
                return False
    return True


class TestUtilDTLib(unittest.TestCase):

    def check(self, arg, *args):
        if numpy is None:
            if isinstance(arg, MPI.Datatype):
                mt1 = arg.Dup()
                dt1 = tonumpy(mt1)
                mt1.Free()
            return
        if not try_dtype(arg):
            return
        if isinstance(arg, MPI.Datatype):
            mt1 = arg.Dup()
            dt1 = tonumpy(mt1)
        else:
            dt1 = np_dtype(arg, *args)
            mt1 = fromnumpy(dt1)
        dt2 = tonumpy(mt1)
        mt2 = fromnumpy(dt2)
        dt3 = tonumpy(mt2)
        mt3 = fromnumpy(dt3)
        try:
            self.assertEqual(dt1, dt2)
            self.assertEqual(dt2, dt3)
            if isinstance(arg, MPI.Datatype):
                if arg.combiner not in (
                    MPI.COMBINER_INDEXED,
                    MPI.COMBINER_HINDEXED,
                    MPI.COMBINER_INDEXED_BLOCK,
                    MPI.COMBINER_HINDEXED_BLOCK,
                ):
                    self.assertEqual(dt1.itemsize, mt1.extent)
            self.assertEqual(dt2.itemsize, mt2.extent)
            self.assertEqual(dt3.itemsize, mt3.extent)
        finally:
            mt1.Free()
            mt2.Free()
            mt3.Free()

    def testBasic(self):
        for spec in typecodes:
            with self.subTest(spec=spec):
                self.check(spec)
        for mpit in datatypes:
            with self.subTest(name=mpit.name):
                self.check(mpit)

    def testSubarray1(self):
        shapes = [(1,), (1, 1), (1, 1, 1), (3,), (3, 4), (2, 3, 4),]
        for dt, shape in itertools.product(typecodes, shapes):
            spec = f"{shape}{dt}"
            with self.subTest(spec=spec):
                self.check(spec)

    def testSubarray2(self):
        shapes = [(1,), (1, 1), (1, 1, 1), (3,), (3, 4), (2, 3, 4),]
        orders = [MPI.ORDER_C, MPI.ORDER_FORTRAN]
        for mt, shape, order in itertools.product(datatypes, shapes, orders):
            if not try_dtype(mt): continue
            with self.subTest(name=mt.name, shape=shape, order=order):
                starts = (0,) * len(shape)
                mt1 = mt.Create_subarray(shape, shape, starts, order)
                self.check(mt1)
                mt1.Free()

    @unittest.skipMPI('msmpi')
    def testStruct1(self):
        shapes = [(), (1,), (3,), (3, 5),]
        iter1 = itertools.product(shapes, typecodes)
        iter2 = itertools.product(shapes, typecodes)
        iterN = itertools.product(iter1, iter2)
        iterA = iter([False, True])
        for nt, align in itertools.product(iterN, iterA):
            s1, t1, s2, t2 = sum(nt, ())
            spec = f"{s1}{t1},{s2}{t2}"
            with self.subTest(spec=spec, align=align):
                self.check(spec, align)

    @unittest.skipMPI('msmpi')
    def testStruct2(self):
        iter1 = iter(typecodes)
        iter2 = iter(typecodes)
        iter3 = iter(typecodes)
        iterN = itertools.product(iter1, iter2, iter3)
        iterA = iter([False, True])
        for tp, align in itertools.product(iterN, iterA):
            t1, t2, t3 = tp
            spec = f"{t1},{t2},{t3}"
            with self.subTest(spec=spec, align=align):
                self.check(spec, align)

    @unittest.skipMPI('msmpi')
    def testStruct3(self):
        blens = [1,  2,  3]
        disps = [1, 27, 71]
        types = [MPI.INT, MPI.DOUBLE, MPI.INT]
        mt1 = MPI.Datatype.Create_struct(blens, disps, types)
        mt2 = MPI.Datatype.Create_struct([1], [0], [mt1])
        self.check(mt1)
        self.check(mt2)
        mt1.Free()
        mt2.Free()

    def makeStruct(self, dt, mt):
        dt = numpy.dtype(dt).str
        stp = numpy.dtype(",".join(['B', dt, 'B']), align=True)
        off = lambda i: stp.fields[stp.names[i]][1]
        blens = [1, 1, 1]
        disps = [0, off(1), off(2)]
        types = [MPI.BYTE, mt, MPI.BYTE]
        mtp = MPI.Datatype.Create_struct(blens, disps, types)
        return stp, mtp

    @unittest.skipMPI('msmpi')
    @unittest.skipIf(numpy is None, 'numpy')
    def testStruct4(self):
        for t in typecodes:
            with self.subTest(typecode=t):
                dt0 = np_dtype(t)
                mt0 = fromnumpy(dt0)
                stp, mt1 = self.makeStruct(t, mt0)
                ex1 = stp.itemsize
                for n, mt in (
                    (1, mt1),
                    (1, mt1.Dup()),
                    (1, mt1.Create_resized(0, 1*ex1)),
                    (3, mt1.Create_resized(0, 3*ex1)),
                    (3, mt1.Create_contiguous(3)),
                    (5, mt1.Create_subarray([5], [5], [0])),
                    (7, MPI.Datatype.Create_struct([7], [0], [mt1])),
                ):
                    dt = tonumpy(mt)
                    self.assertEqual(mt.extent, n*ex1)
                    self.assertEqual(dt.itemsize, n*ex1)
                    self.assertTrue(dt.isalignedstruct)
                    self.check(mt)
                    self.check(dt)
                    if mt != mt1:
                        mt.Free()
                mt0.Free()
                mt1.Free()

    @unittest.skipMPI('msmpi')
    @unittest.skipIf(numpy is None, 'numpy')
    def testStruct5(self):
        for t1, t2 in itertools.product(*[typecodes]*2):
            with self.subTest(t1=t1, t2=t2):
                dtlist = []
                dt = np_dtype(f"c,{t1},{t2},c", align=True)
                dtlist.append(dt)
                for _ in range(3):
                    dt = np_dtype([('', dt)]*2, align=True)
                    dtlist.append(dt)
                for dt in dtlist:
                    mt = fromnumpy(dt)
                    dt2 = tonumpy(mt)
                    mt.Free()
                    self.assertEqual(dt, dt2)

    def testVector(self):
        for mt in datatypes:
            if not try_dtype(mt): continue
            with self.subTest(name=mt.name):
                mt1 = mt.Create_vector(3, 4, 6)
                mt2 = mt.Create_hvector(3, 4, 6*mt.extent)
                self.check(mt1)
                self.check(mt2)
                dt1 = tonumpy(mt1)
                dt2 = tonumpy(mt2)
                self.check(dt1)
                self.check(dt2)
                self.assertEqual(dt1, dt2)
                mt3 = mt1.Create_vector(2, 3, 4)
                mt4 = mt2.Create_hvector(2, 3, 4*mt2.extent)
                self.check(mt3)
                self.check(mt4)
                dt3 = tonumpy(mt3)
                dt4 = tonumpy(mt4)
                self.check(dt3)
                self.check(dt4)
                self.assertEqual(dt3, dt4)
                mt3.Free()
                mt4.Free()
                mt1.Free()
                mt2.Free()

    def testHVector(self):
        for mt in datatypes:
            if not try_dtype(mt): continue
            with self.subTest(name=mt.name):
                mt1 = mt.Create_hvector(3, 4, 6*mt.extent+1)
                mt2 = mt1.Dup()
                self.check(mt1)
                self.check(mt2)
                dt1 = tonumpy(mt1)
                dt2 = tonumpy(mt2)
                self.check(dt1)
                self.check(dt2)
                self.assertEqual(dt1, dt2)
                mt3 = mt1.Create_hvector(2, 3, 4*mt1.extent+1)
                mt4 = mt2.Create_hvector(2, 3, 4*mt2.extent+1)
                self.check(mt3)
                self.check(mt4)
                dt3 = tonumpy(mt3)
                dt4 = tonumpy(mt4)
                self.check(dt3)
                self.check(dt4)
                self.assertEqual(dt3, dt4)
                mt3.Free()
                mt4.Free()
                mt1.Free()
                mt2.Free()

    def testIndexed(self):
        disps = [1, 6, 12]
        for mt in datatypes:
            if not try_dtype(mt): continue
            with self.subTest(name=mt.name):
                mt1 = mt.Create_indexed([4]*3,   disps)
                mt2 = mt.Create_indexed_block(4, disps)
                self.check(mt1)
                self.check(mt2)
                dt1 = tonumpy(mt1)
                dt2 = tonumpy(mt2)
                self.check(dt1)
                self.check(dt2)
                self.assertEqual(dt1, dt2)
                mt3 = mt1.Create_indexed([1], [0])
                mt4 = mt2.Create_indexed_block(1, [0])
                self.check(mt3)
                self.check(mt4)
                dt3 = tonumpy(mt3)
                dt4 = tonumpy(mt4)
                self.check(dt3)
                self.check(dt4)
                self.assertEqual(dt3, dt4)
                mt3.Free()
                mt4.Free()
                mt1.Free()
                mt2.Free()

    def testHIndexed(self):
        disps = [0, 6, 12]
        for mt in datatypes:
            if not try_dtype(mt): continue
            with self.subTest(name=mt.name):
                mt1 = mt.Create_hindexed([4]*3,   [d*mt.extent+1 for d in disps])
                mt2 = mt.Create_hindexed_block(4, [d*mt.extent+1 for d in disps])
                self.check(mt1)
                self.check(mt2)
                dt1 = tonumpy(mt1)
                dt2 = tonumpy(mt2)
                self.check(dt1)
                self.check(dt2)
                self.assertEqual(dt1, dt2)
                mt3 = mt1.Create_hindexed([1], [0])
                mt4 = mt2.Create_hindexed_block(1, [0])
                self.check(mt3)
                self.check(mt4)
                mt3.Free()
                mt4.Free()
                mt1.Free()
                mt2.Free()

    @unittest.skipMPI('msmpi')
    def testF77(self):
        for mt in mpif77types:
            dt = tonumpy(mt)
            if np_dtype is not None:
                self.assertEqual(dt.itemsize, mt.extent)

    @unittest.skipMPI('msmpi')
    def testF90(self):
        for mt in mpif90types:
            if np_dtype is not None:
                typestr = mt.typestr
                try:
                    np_dtype(typestr)
                except TypeError:
                    continue
            dt = tonumpy(mt)
            if np_dtype is not None:
                self.assertEqual(dt.itemsize, mt.extent)

    @unittest.skipMPI('msmpi')
    def testF90Integer(self):
        try:
            mt = MPI.Datatype.Create_f90_integer(1)
            if not testutil.has_datatype(mt):
                raise NotImplementedError
        except NotImplementedError:
            self.skipTest('mpi-type-create-f90-integer')
        for r in range(1, 19):
            with self.subTest(r=r):
                mt = MPI.Datatype.Create_f90_integer(r)
                dt = tonumpy(mt)
                if np_dtype is not None:
                    self.assertEqual(dt.kind, 'i')
                    self.assertEqual(dt.itemsize, mt.extent)
                    size = mt.Get_size()
                    tstr = f'i{size}'
                    stp, mtp = self.makeStruct(tstr, mt)
                    self.assertEqual(stp.itemsize, mtp.extent)
                    self.check(mtp)
                    mtp.Free()

    @unittest.skipMPI('msmpi')
    def testF90Real(self):
        try:
            mt = MPI.Datatype.Create_f90_real(7, MPI.UNDEFINED)
            if not testutil.has_datatype(mt):
                raise NotImplementedError
        except NotImplementedError:
            self.skipTest('mpi-type-create-f90-real')
        for p in (6, 7, 14, 15):
            with self.subTest(p=p):
                mt = MPI.Datatype.Create_f90_real(p, MPI.UNDEFINED)
                dt = tonumpy(mt)
                if np_dtype is not None:
                    self.assertEqual(dt.kind, 'f')
                    self.assertEqual(dt.itemsize, mt.extent)
                    size = mt.Get_size()
                    tstr = f'i{size}'
                    stp, mtp = self.makeStruct(tstr, mt)
                    self.assertEqual(stp.itemsize, mtp.extent)
                    self.check(mtp)
                    mtp.Free()

    @unittest.skipMPI('msmpi')
    def testF90Complex(self):
        try:
            mt = MPI.Datatype.Create_f90_complex(7, MPI.UNDEFINED)
            if not testutil.has_datatype(mt):
                raise NotImplementedError
        except NotImplementedError:
            self.skipTest('mpi-type-create-f90-complex')
        for p in (6, 7, 14, 15):
            with self.subTest(p=p):
                mt = MPI.Datatype.Create_f90_complex(p, MPI.UNDEFINED)
                dt = tonumpy(mt)
                if np_dtype is not None:
                    self.assertEqual(dt.kind, 'c')
                    self.assertEqual(dt.itemsize, mt.extent)

    def testPair(self):
        for mt in mpipairtypes:
            with self.subTest(datatype=mt.name):
                dt = tonumpy(mt)
                if np_dtype is not None:
                    self.assertTrue(dt.isalignedstruct)
                    self.assertEqual(dt.itemsize, mt.extent)
        integral = 'bhilqpBHILQP'
        floating = 'fdg'
        vtypes = integral + floating
        itypes = integral
        for vcode, icode in itertools.product(vtypes, itypes):
            value = MPI.Datatype.fromcode(vcode)
            index = MPI.Datatype.fromcode(icode)
            pair  = MPI.Datatype.Get_value_index(value, index)
            if pair == MPI.DATATYPE_NULL:
                continue
            vt, it, pt = map(tonumpy, (value, index, pair))
            dt = (f'{vt},{it}', {'align': True})
            if np_dtype is not None:
                dt = np_dtype(dt[0], **dt[1])
            self.assertEqual(pt, dt)

    def testPairStruct(self):
        cases = [mpipairtypes]*3 +[[False, True]]
        for mt1, mt2, mt3, dup in itertools.product(*cases):
            with self.subTest(mt1=mt1.name, mt2=mt2.name, mt3=mt3.name):
                if dup:
                    mt1 = mt1.Dup()
                    mt2 = mt2.Dup()
                    mt3 = mt3.Dup()
                align = max(mt.extent for mt in (mt1, mt2, mt3))
                structtype = MPI.Datatype.Create_struct(
                    [1, 1, 1], [0, align, align*2], [mt1, mt2, mt3],
                )
                if dup:
                    mt1.Free()
                    mt2.Free()
                    mt3.Free()
                dt = tonumpy(structtype)
                structtype.Free()
                if np_dtype is not None:
                    self.assertTrue(dt.isalignedstruct)

    def testAlignmentComplex(self):
        complexcodes = list('FDG')
        complexcodes += [f'c{n}' for n in (8, 16)]
        for t in typecodes + complexcodes:
            with self.subTest(typecode=t):
                datatype = MPI.Datatype.fromcode(t)
                alignment1 = MPI._typealign(datatype)
                if np_dtype is not None:
                    alignment2 = np_dtype(t).alignment
                    self.assertEqual(alignment1, alignment2)

    def testAlignmentPair(self):
        for pairtype in mpipairtypes:
            alignment1 = MPI._typealign(pairtype)
            self.assertIn(alignment1, (2, 4, 8, 16))
            if np_dtype is not None:
                alignment2 = tonumpy(pairtype).alignment
                self.assertEqual(alignment1, alignment2)

    def testAlignmentStruct(self):
        off = MPI.DOUBLE.extent
        structtype = MPI.Datatype.Create_struct(
            [1, 1], [0, off], [MPI.INT, MPI.DOUBLE],
        )
        alignment = MPI._typealign(structtype)
        self.assertIsNone(alignment)
        structtype.Free()

    def testMissingNumPy(self):
        from mpi4py.util import dtlib
        np_dtype = dtlib._np_dtype
        dtlib._np_dtype = None
        try:
            for t in typecodes:
                with self.subTest(typecode=t):
                    mt = MPI.Datatype.fromcode(t)
                    dt = tonumpy(mt)
                    code = mt.tocode()
                    self.assertEqual(dt, code)
                    arraytype = mt.Create_contiguous(7)
                    dt = tonumpy(arraytype)
                    arraytype.Free()
                    self.assertIsInstance(dt, tuple)
                    self.assertEqual(dt[0], code)
                    self.assertEqual(dt[1], (7,))
                    structtype = MPI.Datatype.Create_struct(
                        [1, 1], [0, mt.extent], [mt, mt],
                    )
                    dt = tonumpy(structtype)
                    structtype.Free()
                    self.assertIsInstance(dt, dict)
                    self.assertEqual(dt['formats'], [code]*2)
                    self.assertEqual(dt['offsets'], [0, mt.extent])
                    self.assertEqual(dt['itemsize'], mt.extent*2)
                    self.assertTrue(dt['aligned'])
            with self.assertRaises(RuntimeError):
                fromnumpy(None)
        finally:
            dtlib._np_dtype = np_dtype

    @unittest.skipIf(numpy is None, 'numpy')
    def testFailures(self):
        endian = '>' if np_dtype('<i').isnative else '<'
        self.assertRaises(ValueError, fromnumpy, np_dtype(endian+'i'))
        self.assertRaises(ValueError, fromnumpy, np_dtype('O'))
        self.assertRaises(ValueError, fromnumpy, np_dtype('V'))
        self.assertRaises(ValueError, tonumpy, MPI.DATATYPE_NULL)
        mt = MPI.INT.Create_resized(0, 32)
        self.assertRaises(ValueError, tonumpy, mt)
        mt.Free()
        mt = MPI.INT.Create_subarray([2], [1], [0])
        self.assertRaises(ValueError, tonumpy, mt)
        mt.Free()


if __name__ == '__main__':
    unittest.main()
