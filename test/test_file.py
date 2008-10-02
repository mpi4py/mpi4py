from mpi4py import MPI
import mpiunittest as unittest
import os, tempfile

class TestFileBase(object):

    COMM = MPI.COMM_NULL
    FILE = MPI.FILE_NULL

    prefix = 'mpi4py'

    def setUp(self):
        self.fd, self.fname = tempfile.mkstemp(prefix=self.prefix)
        self.amode = MPI.MODE_RDWR | MPI.MODE_CREATE
        #self.amode |= MPI.MODE_DELETE_ON_CLOSE
        try:
            self.FILE = MPI.File.Open(self.COMM,
                                      self.fname, self.amode,
                                      MPI.INFO_NULL)
        except Exception:
            os.close(self.fd)
            os.remove(self.fname)
            raise

    def tearDown(self):
        if self.FILE == MPI.FILE_NULL: return
        os.close(self.fd)
        amode = self.FILE.amode
        self.FILE.Close()
        if not (amode & MPI.MODE_DELETE_ON_CLOSE):
            MPI.File.Delete(self.fname, MPI.INFO_NULL)

    def testPreallocate(self):
        # XXX MPICH2 generates a warning
        # about nesting level at finalization
        ## self.FILE.Preallocate(0)
        ## size = self.FILE.Get_size()
        ## self.assertEqual(size, 0)
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
                    self.assertEqual(disp,    of)
                    self.assertEqual(etype,   et)
                    self.assertEqual(ftype,   ft)
                    self.assertEqual(datarep, dr)
                    #try: et.Free()
                    #except MPI.Exception: pass
                    #try: ft.Free()
                    #except MPI.Exception: pass

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
        self.eh_bak = MPI.FILE_NULL.Get_errhandler()

    def tearDown(self):
        MPI.FILE_NULL.Set_errhandler(self.eh_bak)
        self.eh_bak.Free()

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


class TestFileSelf(TestFileBase, unittest.TestCase):
    COMM = MPI.COMM_SELF
    prefix = TestFileBase.prefix + ('-%d' % MPI.COMM_WORLD.Get_rank())


_name, _version = MPI.get_vendor()
if _name == 'Open MPI':
    if (_version < (1,2,7) and \
        MPI.Query_thread() > MPI.THREAD_SINGLE):
        del TestFileBase.testPreallocate
        del TestFileBase.testGetSetInfo
        del TestFileBase.testGetSetAtomicity
        del TestFileBase.testSync
        del TestFileBase.testGetSetSize
        del TestFileBase.testGetSetView
        del TestFileBase.testGetByteOffset
        del TestFileBase.testGetTypeExtent
        del TestFileBase.testSeekGetPosition
        del TestFileBase.testSeekGetPositionShared
else:
    try:
        dummy = TestFileBase()
        dummy.COMM = MPI.COMM_SELF
        dummy.setUp()
        dummy.tearDown()
        del dummy
    except NotImplementedError:
        del TestFileNull
        del TestFileBase
        del TestFileSelf

if __name__ == '__main__':
    unittest.main()
