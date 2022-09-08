from mpi4py import MPI
from mpi4py.util.dtlib import from_numpy_dtype as fromnumpy
from mpi4py.util.dtlib import to_numpy_dtype   as tonumpy
import sys, os
import itertools
try:
    import mpiunittest as unittest
except ImportError:
    sys.path.append(
        os.path.abspath(
            os.path.dirname(__file__)))
    import mpiunittest as unittest

try:
    import numpy
    np_dtype = numpy.dtype
    np_version = tuple(map(int, numpy.__version__.split('.', 2)[:2]))
except ImportError:
    numpy = None
    np_dtype = None
    np_version = None

typecodes = list("?cbhilqpBHILQfdgFDG")
typecodes += ['b{:d}'.format(n) for n in (1,)]
typecodes += ['i{:d}'.format(n) for n in (1,2,4,8)]
typecodes += ['u{:d}'.format(n) for n in (1,2,4,8)]
typecodes += ['f{:d}'.format(n) for n in (4,8)]

if np_version and np_version < (1, 17):
    typecodes.remove('L')
    typecodes.remove('F')
    typecodes.remove('D')
    typecodes.remove('G')

name, version = MPI.get_vendor()
mpich_lt_400 = (name == 'MPICH') and version < (4, 0, 0)
if mpich_lt_400:
    typecodes = [t for t in typecodes if t not in 'FDG']

datatypes = [MPI._typedict[t] for t in typecodes]

class TestUtilDTLib(unittest.TestCase):

    def check(self, arg, *args):
        if numpy is None:
            if isinstance(arg, MPI.Datatype):
                mt1 = arg.Dup()
                dt1 = tonumpy(mt1)
                mt1.Free()
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
            spec = "{}{}".format(shape, dt)
            with self.subTest(spec=spec):
                self.check(spec)

    def testSubarray2(self):
        shapes = [(1,), (1, 1), (1, 1, 1), (3,), (3, 4), (2, 3, 4),]
        orders = [MPI.ORDER_C, MPI.ORDER_FORTRAN]
        for mt, shape, order in itertools.product(datatypes, shapes, orders):
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
            spec = "{}{},{}{}".format(*sum(nt, ()))
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
            spec = "{},{},{}".format(*tp)
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

    def testVector(self):
        for mt in datatypes:
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
        mpif77types = [
            MPI.CHARACTER,
            #MPI.LOGICAL,
            MPI.INTEGER,
            MPI.REAL,
            MPI.DOUBLE_PRECISION,
            MPI.COMPLEX,
            MPI.DOUBLE_COMPLEX,
        ]
        for mt in mpif77types:
            if mt == MPI.DATATYPE_NULL:
                continue
            if mt.Get_size() == 0:
                continue
            dt = tonumpy(mt)
            if np_dtype is not None:
                self.assertEqual(dt.itemsize, mt.extent)

    @unittest.skipMPI('msmpi')
    def testF90(self):
        mpif90types = (
            MPI.INTEGER1,
            MPI.INTEGER2,
            MPI.INTEGER4,
            MPI.INTEGER8,
            MPI.INTEGER16,
            MPI.REAL4,
            MPI.REAL8,
            MPI.COMPLEX8,
            MPI.COMPLEX16,
        )
        for mt in mpif90types:
            if mt == MPI.DATATYPE_NULL:
                continue
            if mt.Get_size() == 0:
                continue
            dt = tonumpy(mt)
            if np_dtype is not None:
                self.assertEqual(dt.itemsize, mt.extent)

    @unittest.skipMPI('msmpi')
    def testF90Integer(self):
        try:
            mt = MPI.Datatype.Create_f90_integer(1)
            if mt == MPI.DATATYPE_NULL or mt.Get_size() == 0:
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
                    tstr = 'i{}'.format(mt.Get_size())
                    stp, mtp = self.makeStruct(tstr, mt)
                    self.assertEqual(stp.itemsize, mtp.extent)
                    self.check(mtp)
                    mtp.Free()

    @unittest.skipMPI('msmpi')
    def testF90Real(self):
        try:
            mt = MPI.Datatype.Create_f90_real(7, MPI.UNDEFINED)
            if mt == MPI.DATATYPE_NULL or mt.Get_size() == 0:
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
                    tstr = 'f{}'.format(mt.Get_size())
                    stp, mtp = self.makeStruct(tstr, mt)
                    self.assertEqual(stp.itemsize, mtp.extent)
                    self.check(mtp)
                    mtp.Free()

    @unittest.skipMPI('msmpi')
    def testF90Complex(self):
        try:
            mt = MPI.Datatype.Create_f90_complex(7, MPI.UNDEFINED)
            if mt == MPI.DATATYPE_NULL or mt.Get_size() == 0:
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

    @unittest.skipMPI('msmpi')
    def testCoverage(self):
        from mpi4py.util import dtlib
        mpitypes = (
            MPI.LOGICAL,
        )
        for mt in mpitypes:
            if mt == MPI.DATATYPE_NULL:
                continue
            if mt.Get_size() == 0:
                continue
            dtlib._get_alignment(mt)

    def testAlignment(self):
        from mpi4py.util import dtlib
        complexcodes = ['c{}'.format(n) for n in (8, 16)]
        for t in typecodes + complexcodes:
            with self.subTest(typecode=t):
                alignment1 = dtlib._get_alignment_ctypes(t)
                if np_dtype is not None:
                    alignment2 = numpy.dtype(t).alignment
                    self.assertTrue(alignment1, alignment2)

    @unittest.skipIf(numpy is None, 'numpy')
    def testFailures(self):
        endian = '>' if np_dtype('<i').isnative else '<'
        self.assertRaises(ValueError, fromnumpy, np_dtype(endian+'i'))
        self.assertRaises(ValueError, fromnumpy, np_dtype('O'))
        self.assertRaises(ValueError, fromnumpy, np_dtype('V'))
        self.assertRaises(ValueError, tonumpy, MPI.DATATYPE_NULL)
        self.assertRaises(ValueError, tonumpy, MPI.INT_INT)
        mt = MPI.INT.Create_resized(0, 32)
        self.assertRaises(ValueError, tonumpy, mt)
        mt.Free()
        mt = MPI.INT.Create_subarray([2], [1], [0])
        self.assertRaises(ValueError, tonumpy, mt)
        mt.Free()


if __name__ == '__main__':
    unittest.main()
