from mpi4py import MPI
import mpiunittest as unittest
import sys
try:
    sys.getrefcount
except AttributeError:
    class getrefcount(object):
        def __init__(self, arg):
            pass
        def __eq__(self, other):
            return True
        def __add__(self, other):
            return self
        def __sub__(self, other):
            return self

def memzero(m):
    try:
        m[:] = 0
    except IndexError: # cffi buffer
        m[0:len(m)] = b'\0'*len(m)


class BaseTestWin(object):

    COMM = MPI.COMM_NULL
    INFO = MPI.INFO_NULL
    CREATE_FLAVOR = MPI.UNDEFINED

    def testGetAttr(self):
        base = MPI.Get_address(self.memory)
        size = len(self.memory)
        unit = 1
        self.assertEqual(size, self.WIN.Get_attr(MPI.WIN_SIZE))
        self.assertEqual(unit, self.WIN.Get_attr(MPI.WIN_DISP_UNIT))
        self.assertEqual(base, self.WIN.Get_attr(MPI.WIN_BASE))

    def testMemory(self):
        memory = self.WIN.tomemory()
        pointer = MPI.Get_address(memory)
        length = len(memory)
        base, size, dunit = self.WIN.attrs
        self.assertEqual(size,  length)
        self.assertEqual(dunit, 1)
        self.assertEqual(base,  pointer)

    def testAttributes(self):
        base, size, unit = self.WIN.attrs
        self.assertEqual(base, MPI.Get_address(self.memory))
        self.assertEqual(size, len(self.memory))
        self.assertEqual(unit, 1)

    def testGetGroup(self):
        cgroup = self.COMM.Get_group()
        wgroup = self.WIN.Get_group()
        grpcmp = MPI.Group.Compare(cgroup, wgroup)
        cgroup.Free()
        wgroup.Free()
        self.assertEqual(grpcmp, MPI.IDENT)

    def testGetSetInfo(self):
        #info = MPI.INFO_NULL
        #self.WIN.Set_info(info)
        info = MPI.Info.Create()
        self.WIN.Set_info(info)
        info.Free()
        info = self.WIN.Get_info()
        self.WIN.Set_info(info)
        info.Free()

    def testGetSetErrhandler(self):
        for ERRHANDLER in [MPI.ERRORS_ARE_FATAL, MPI.ERRORS_RETURN,
                           MPI.ERRORS_ARE_FATAL, MPI.ERRORS_RETURN,]:
            errhdl_1 = self.WIN.Get_errhandler()
            self.assertNotEqual(errhdl_1, MPI.ERRHANDLER_NULL)
            self.WIN.Set_errhandler(ERRHANDLER)
            errhdl_2 = self.WIN.Get_errhandler()
            self.assertEqual(errhdl_2, ERRHANDLER)
            errhdl_2.Free()
            self.assertEqual(errhdl_2, MPI.ERRHANDLER_NULL)
            self.WIN.Set_errhandler(errhdl_1)
            errhdl_1.Free()
            self.assertEqual(errhdl_1, MPI.ERRHANDLER_NULL)

    def testGetSetName(self):
        try:
            name = self.WIN.Get_name()
            self.WIN.Set_name('mywin')
            self.assertEqual(self.WIN.Get_name(), 'mywin')
            self.WIN.Set_name(name)
            self.assertEqual(self.WIN.Get_name(), name)
        except NotImplementedError:
            self.skipTest('mpi-win-name')

    @unittest.skipIf(MPI.WIN_CREATE_FLAVOR == MPI.KEYVAL_INVALID, 'mpi-win-flavor')
    def testCreateFlavor(self):
        flavors = (MPI.WIN_FLAVOR_CREATE,
                   MPI.WIN_FLAVOR_ALLOCATE,
                   MPI.WIN_FLAVOR_DYNAMIC,
                   MPI.WIN_FLAVOR_SHARED,)
        flavor = self.WIN.Get_attr(MPI.WIN_CREATE_FLAVOR)
        self.assertTrue (flavor in flavors)
        self.assertEqual(flavor, self.WIN.flavor)
        self.assertEqual(flavor, self.CREATE_FLAVOR)

    @unittest.skipIf(MPI.WIN_MODEL == MPI.KEYVAL_INVALID, 'mpi-win-model')
    def testMemoryModel(self):
        models = (MPI.WIN_SEPARATE, MPI.WIN_UNIFIED)
        model = self.WIN.Get_attr(MPI.WIN_MODEL)
        self.assertTrue(model in models)
        self.assertEqual(model, self.WIN.model)

class BaseTestWinCreate(BaseTestWin):

    CREATE_FLAVOR = MPI.WIN_FLAVOR_CREATE

    def setUp(self):
        self.memory = MPI.Alloc_mem(10)
        memzero(self.memory)
        self.WIN = MPI.Win.Create(self.memory, 1, self.INFO, self.COMM)

    def tearDown(self):
        self.WIN.Free()
        MPI.Free_mem(self.memory)

class BaseTestWinAllocate(BaseTestWin):

    CREATE_FLAVOR = MPI.WIN_FLAVOR_ALLOCATE

    def setUp(self):
        self.WIN = MPI.Win.Allocate(10, 1, self.INFO, self.COMM)
        self.memory = self.WIN.tomemory()
        memzero(self.memory)

    def tearDown(self):
        self.WIN.Free()

class BaseTestWinAllocateShared(BaseTestWin):

    CREATE_FLAVOR = MPI.WIN_FLAVOR_SHARED

    def setUp(self):
        self.WIN = MPI.Win.Allocate_shared(10, 1, self.INFO, self.COMM)
        self.memory = self.WIN.tomemory()
        memzero(self.memory)

    def tearDown(self):
        self.WIN.Free()

    def testSharedQuery(self):
        memory = self.WIN.tomemory()
        address = MPI.Get_address(memory)
        length = len(memory)
        memories = self.COMM.allgather((address, length))
        rank = self.COMM.Get_rank()
        size = self.COMM.Get_size()
        for i in range(size):
            mem, disp = self.WIN.Shared_query(rank)
            base = MPI.Get_address(mem)
            size = len(mem)
            if i == rank:
                self.assertEqual(base, memories[i][0])
            self.assertEqual(size, memories[i][1])
            self.assertEqual(disp, 1)

class BaseTestWinCreateDynamic(BaseTestWin):

    CREATE_FLAVOR = MPI.WIN_FLAVOR_DYNAMIC

    def setUp(self):
        self.WIN = MPI.Win.Create_dynamic(self.INFO, self.COMM)

    def tearDown(self):
        self.WIN.Free()

    def testGetAttr(self):
        base = self.WIN.Get_attr(MPI.WIN_BASE)
        size = self.WIN.Get_attr(MPI.WIN_SIZE)
        self.assertEqual(base, 0)
        self.assertEqual(size, 0)

    def testMemory(self):
        memory = self.WIN.tomemory()
        base = MPI.Get_address(memory)
        size = len(memory)
        self.assertEqual(base, 0)
        self.assertEqual(size, 0)

    def testAttributes(self):
        base, size, _ = self.WIN.attrs
        self.assertEqual(base, 0)
        self.assertEqual(size, 0)

    def testAttachDetach(self):
        mem1 = MPI.Alloc_mem(8)
        mem2 = MPI.Alloc_mem(16)
        mem3 = MPI.Alloc_mem(32)
        for mem in (mem1, mem2, mem3):
            self.WIN.Attach(mem)
            self.testMemory()
            self.WIN.Detach(mem)
        for mem in (mem1, mem2, mem3):
            self.WIN.Attach(mem)
        self.testMemory()
        for mem in (mem1, mem2, mem3):
            self.WIN.Detach(mem)
        for mem in (mem1, mem2, mem3):
            self.WIN.Attach(mem)
        self.testMemory()
        for mem in (mem3, mem2, mem1):
            self.WIN.Detach(mem)
        MPI.Free_mem(mem1)
        MPI.Free_mem(mem2)
        MPI.Free_mem(mem3)

class TestWinCreateSelf(BaseTestWinCreate, unittest.TestCase):
    COMM = MPI.COMM_SELF

@unittest.skipMPI('openmpi(<1.4.0)')
class TestWinCreateWorld(BaseTestWinCreate, unittest.TestCase):
    COMM = MPI.COMM_WORLD

class TestWinAllocateSelf(BaseTestWinAllocate, unittest.TestCase):
    COMM = MPI.COMM_SELF

@unittest.skipMPI('openmpi(<1.4.0)')
class TestWinAllocateWorld(BaseTestWinAllocate, unittest.TestCase):
    COMM = MPI.COMM_WORLD

class TestWinAllocateSharedSelf(BaseTestWinAllocateShared, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestWinAllocateSharedWorld(BaseTestWinAllocateShared, unittest.TestCase):
    COMM = MPI.COMM_WORLD

class TestWinCreateDynamicSelf(BaseTestWinCreateDynamic, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestWinCreateDynamicWorld(BaseTestWinCreateDynamic, unittest.TestCase):
    COMM = MPI.COMM_WORLD


SpectrumMPI = MPI.get_vendor()[0] == 'Spectrum MPI'
try:
    if SpectrumMPI: raise NotImplementedError
    MPI.Win.Create(MPI.BOTTOM, 1, MPI.INFO_NULL, MPI.COMM_SELF).Free()
except NotImplementedError:
    unittest.disable(BaseTestWinCreate, 'mpi-win-create')
try:
    if SpectrumMPI: raise NotImplementedError
    MPI.Win.Allocate(1, 1, MPI.INFO_NULL, MPI.COMM_SELF).Free()
except NotImplementedError:
    unittest.disable(BaseTestWinAllocate, 'mpi-win-allocate')
try:
    if SpectrumMPI: raise NotImplementedError
    MPI.Win.Allocate_shared(1, 1, MPI.INFO_NULL, MPI.COMM_SELF).Free()
except NotImplementedError:
    unittest.disable(BaseTestWinAllocateShared, 'mpi-win-shared')
try:
    if SpectrumMPI: raise NotImplementedError
    MPI.Win.Create_dynamic(MPI.INFO_NULL, MPI.COMM_SELF).Free()
except NotImplementedError:
    unittest.disable(BaseTestWinCreateDynamic, 'mpi-win-dynamic')


if __name__ == '__main__':
    unittest.main()
