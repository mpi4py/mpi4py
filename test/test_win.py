import sys
from mpi4py import MPI
import mpiunittest as unittest
try:
    from sys import getrefcount
except ImportError:
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
    n = len(m)
    if n == 0: return
    try:
        zero = b'\0'
        m[0] = zero
    except TypeError:
        zero = 0
        m[0] = zero
    for i in range(n):
        m[i] = zero

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
        memory = self.WIN.memory
        pointer = MPI.Get_address(memory)
        length = len(memory)
        base, size, dunit = self.WIN.attrs
        self.assertEqual(size,  length)
        self.assertEqual(dunit, 1)
        self.assertEqual(base,  pointer)

    def testAttributes(self):
        base, size, unit = self.WIN.attrs
        self.assertEqual(size, len(self.memory))
        self.assertEqual(unit, 1)
        self.assertEqual(base, MPI.Get_address(self.memory))

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
            pass

    def testCreateFlavor(self):
        if MPI.WIN_CREATE_FLAVOR == MPI.KEYVAL_INVALID: return
        flavors = (MPI.WIN_FLAVOR_CREATE,
                   MPI.WIN_FLAVOR_ALLOCATE,
                   MPI.WIN_FLAVOR_DYNAMIC,
                   MPI.WIN_FLAVOR_SHARED,)
        flavor = self.WIN.Get_attr(MPI.WIN_CREATE_FLAVOR)
        self.assertTrue (flavor in flavors)
        self.assertEqual(flavor, self.WIN.flavor)
        self.assertEqual(flavor, self.CREATE_FLAVOR)

    def testMemoryModel(self):
        if MPI.WIN_MODEL == MPI.KEYVAL_INVALID: return
        models = (MPI.WIN_SEPARATE, MPI.WIN_UNIFIED)
        model = self.WIN.Get_attr(MPI.WIN_MODEL)
        self.assertTrue (model in models)
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
        self.memory = self.WIN.memory
        memzero(self.memory)

    def tearDown(self):
        self.WIN.Free()

class BaseTestWinAllocateShared(BaseTestWin):

    CREATE_FLAVOR = MPI.WIN_FLAVOR_SHARED

    def setUp(self):
        self.WIN = MPI.Win.Allocate_shared(10, 1, self.INFO, self.COMM)
        self.memory = self.WIN.memory
        memzero(self.memory)

    def tearDown(self):
        self.WIN.Free()

    def testSharedQuery(self):
        memory = self.WIN.memory
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
        disp = self.WIN.Get_attr(MPI.WIN_DISP_UNIT)
        self.assertEqual(base, 0)
        self.assertEqual(size, 0)
        #self.assertEqual(disp, 1)

    def testMemory(self):
        self.assertTrue(self.WIN.memory is None)

    def testAttributes(self):
        pass

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

class TestWinCreateWorld(BaseTestWinCreate, unittest.TestCase):
    COMM = MPI.COMM_WORLD

class TestWinAllocateSelf(BaseTestWinAllocate, unittest.TestCase):
    COMM = MPI.COMM_SELF

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


try:
    MPI.Win.Create(MPI.BOTTOM, 1, MPI.INFO_NULL, MPI.COMM_SELF).Free()
except NotImplementedError:
    del TestWinCreateSelf, TestWinCreateWorld
try:
    MPI.Win.Allocate(1, 1, MPI.INFO_NULL, MPI.COMM_SELF).Free()
except NotImplementedError:
    del TestWinAllocateSelf, TestWinAllocateWorld
try:
    MPI.Win.Allocate_shared(1, 1, MPI.INFO_NULL, MPI.COMM_SELF).Free()
except NotImplementedError:
    del TestWinAllocateSharedSelf, TestWinAllocateSharedWorld
try:
    MPI.Win.Create_dynamic(MPI.INFO_NULL, MPI.COMM_SELF).Free()
except NotImplementedError:
    del TestWinCreateDynamicSelf, TestWinCreateDynamicWorld

name, version = MPI.get_vendor()
if name == 'Open MPI':
    if version < (1,4,0):
        if MPI.Query_thread() > MPI.THREAD_SINGLE:
            del TestWinCreateWorld
            del TestWinAllocateWorld
if name == 'MPICH2':
    if sys.platform.startswith('win'):
        del BaseTestWin.testAttributes


if __name__ == '__main__':
    unittest.main()
