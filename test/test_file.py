from mpi4py import MPI
import mpiunittest as unittest
import sys, os, tempfile


class BaseTestFile(object):

    COMM = MPI.COMM_NULL
    FILE = MPI.FILE_NULL

    prefix = 'mpi4py'

    def setUp(self):
        fd, self.fname = tempfile.mkstemp(prefix=self.prefix)
        os.close(fd)
        self.amode = MPI.MODE_RDWR | MPI.MODE_CREATE
        #self.amode |= MPI.MODE_DELETE_ON_CLOSE
        try:
            self.FILE = MPI.File.Open(self.COMM,
                                      self.fname, self.amode,
                                      MPI.INFO_NULL)
            #self.fname=None
        except Exception:
            os.remove(self.fname)
            raise

    def tearDown(self):
        if self.FILE == MPI.FILE_NULL: return
        amode = self.FILE.amode
        self.FILE.Close()
        if not (amode & MPI.MODE_DELETE_ON_CLOSE):
            MPI.File.Delete(self.fname, MPI.INFO_NULL)

    @unittest.skipMPI('openmpi(==2.0.0)')
    @unittest.skipMPI('MPICH2(<1.1.0)')
    def testPreallocate(self):
        size = self.FILE.Get_size()
        self.assertEqual(size, 0)
        self.FILE.Preallocate(1)
        size = self.FILE.Get_size()
        self.assertEqual(size, 1)
        self.FILE.Preallocate(100)
        size = self.FILE.Get_size()
        self.assertEqual(size, 100)
        self.FILE.Preallocate(10)
        size = self.FILE.Get_size()
        self.assertEqual(size, 100)
        self.FILE.Preallocate(200)
        size = self.FILE.Get_size()
        self.assertEqual(size, 200)

    def testGetSetSize(self):
        size = self.FILE.Get_size()
        self.assertEqual(size, 0)
        size = self.FILE.size
        self.assertEqual(size, 0)
        self.FILE.Set_size(100)
        size = self.FILE.Get_size()
        self.assertEqual(size, 100)
        size = self.FILE.size
        self.assertEqual(size, 100)

    def testGetGroup(self):
        fgroup = self.FILE.Get_group()
        cgroup = self.COMM.Get_group()
        gcomp = MPI.Group.Compare(fgroup, cgroup)
        self.assertEqual(gcomp, MPI.IDENT)
        fgroup.Free()
        cgroup.Free()

    def testGetAmode(self):
        amode = self.FILE.Get_amode()
        self.assertEqual(self.amode, amode)
        self.assertEqual(self.FILE.amode, self.amode)

    def testGetSetInfo(self):
        #info = MPI.INFO_NULL
        #self.FILE.Set_info(info)
        info = MPI.Info.Create()
        self.FILE.Set_info(info)
        info.Free()
        info = self.FILE.Get_info()
        self.FILE.Set_info(info)
        info.Free()

    def testGetSetView(self):
        fsize = 100 * MPI.DOUBLE.size
        self.FILE.Set_size(fsize)
        displacements = range(100)
        datatypes = [MPI.SHORT, MPI.INT, MPI.LONG, MPI.FLOAT, MPI.DOUBLE]
        datareps  = ['native'] #['native', 'internal', 'external32']
        for disp in displacements:
            for dtype in datatypes:
                for datarep in datareps:
                    etype, ftype = dtype, dtype
                    self.FILE.Set_view(disp, etype, ftype,
                                       datarep, MPI.INFO_NULL)
                    of, et, ft, dr = self.FILE.Get_view()
                    self.assertEqual(disp, of)
                    self.assertEqual(etype.Get_extent(), et.Get_extent())
                    self.assertEqual(ftype.Get_extent(), ft.Get_extent())
                    self.assertEqual(datarep, dr)
                    try:
                        if not et.is_predefined: et.Free()
                    except NotImplementedError:
                        if et != etype: et.Free()
                    try:
                        if not ft.is_predefined: ft.Free()
                    except NotImplementedError:
                        if ft != ftype: ft.Free()

    def testGetSetAtomicity(self):
        atom = self.FILE.Get_atomicity()
        self.assertFalse(atom)
        for atomicity in [True, False] * 4:
            self.FILE.Set_atomicity(atomicity)
            atom = self.FILE.Get_atomicity()
            self.assertEqual(atom, atomicity)

    def testSync(self):
        self.FILE.Sync()

    def testSeekGetPosition(self):
        offset = 0
        self.FILE.Seek(offset, MPI.SEEK_END)
        self.FILE.Seek(offset, MPI.SEEK_CUR)
        self.FILE.Seek(offset, MPI.SEEK_SET)
        pos = self.FILE.Get_position()
        self.assertEqual(pos, offset)

    def testSeekGetPositionShared(self):
        offset = 0
        self.FILE.Seek_shared(offset, MPI.SEEK_END)
        self.FILE.Seek_shared(offset, MPI.SEEK_CUR)
        self.FILE.Seek_shared(offset, MPI.SEEK_SET)
        pos = self.FILE.Get_position_shared()
        self.assertEqual(pos, offset)

    @unittest.skipMPI('openmpi(==2.0.0)')
    def testGetByteOffset(self):
        for offset in range(10):
            disp = self.FILE.Get_byte_offset(offset)
            self.assertEqual(disp, offset)

    def testGetTypeExtent(self):
        extent = self.FILE.Get_type_extent(MPI.BYTE)
        self.assertEqual(extent, 1)

    def testGetErrhandler(self):
        eh = self.FILE.Get_errhandler()
        self.assertEqual(eh, MPI.ERRORS_RETURN)
        eh.Free()

class TestFileNull(unittest.TestCase):

    def setUp(self):
        self.eh_save = MPI.FILE_NULL.Get_errhandler()

    def tearDown(self):
        MPI.FILE_NULL.Set_errhandler(self.eh_save)
        self.eh_save.Free()

    def testGetSetErrhandler(self):
        eh = MPI.FILE_NULL.Get_errhandler()
        self.assertEqual(eh, MPI.ERRORS_RETURN)
        eh.Free()
        MPI.FILE_NULL.Set_errhandler(MPI.ERRORS_ARE_FATAL)
        eh = MPI.FILE_NULL.Get_errhandler()
        self.assertEqual(eh, MPI.ERRORS_ARE_FATAL)
        eh.Free()
        MPI.FILE_NULL.Set_errhandler(MPI.ERRORS_RETURN)
        eh = MPI.FILE_NULL.Get_errhandler()
        self.assertEqual(eh, MPI.ERRORS_RETURN)
        eh.Free()


class TestFileSelf(BaseTestFile, unittest.TestCase):
    COMM = MPI.COMM_SELF
    prefix = BaseTestFile.prefix + ('-%d' % MPI.COMM_WORLD.Get_rank())


def have_feature():
    case = BaseTestFile()
    case.COMM = TestFileSelf.COMM
    case.prefix = TestFileSelf.prefix
    case.setUp()
    case.tearDown()
try:
    have_feature()
except NotImplementedError:
    unittest.disable(BaseTestFile, 'mpi-file')
    unittest.disable(TestFileNull, 'mpi-file')


if __name__ == '__main__':
    unittest.main()
