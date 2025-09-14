import os
import sys

import mpitestutil as testutil
import mpiunittest as unittest

from mpi4py import MPI

try:
    _ = sys.getrefcount
except AttributeError:

    class getrefcount:
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
    except IndexError:  # cffi buffer
        m[0 : len(m)] = b"\0" * len(m)


def ch3_sock():
    return "ch3:sock" in MPI.Get_library_version()


class TestWinNull(unittest.TestCase):
    #
    def testConstructor(self):
        win = MPI.Win()
        self.assertEqual(win, MPI.WIN_NULL)
        self.assertIsNot(win, MPI.WIN_NULL)

        def construct():
            MPI.Win((1, 2, 3))

        self.assertRaises(TypeError, construct)

    def testGetName(self):
        name = MPI.WIN_NULL.Get_name()
        self.assertEqual(name, "MPI_WIN_NULL")


class BaseTestWin:
    #
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
        self.assertEqual(memory.format, "B")
        pointer = MPI.Get_address(memory)
        length = len(memory)
        base, size, dunit = self.WIN.attrs
        self.assertEqual(size, length)
        self.assertEqual(dunit, 1)
        self.assertEqual(base, pointer)

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

    @unittest.skipMPI("impi(>=2021.15.0)")
    def testGetSetInfo(self):
        # info = MPI.INFO_NULL
        # self.WIN.Set_info(info)
        info = MPI.Info.Create()
        self.WIN.Set_info(info)
        info.Free()
        info = self.WIN.Get_info()
        self.WIN.Set_info(info)
        info.Free()

    def testGetSetErrhandler(self):
        for ERRHANDLER in [
            MPI.ERRORS_ARE_FATAL,
            MPI.ERRORS_RETURN,
            MPI.ERRORS_ARE_FATAL,
            MPI.ERRORS_RETURN,
        ]:
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
            self.WIN.Set_name("mywin")
            self.assertEqual(self.WIN.Get_name(), "mywin")
            self.WIN.Set_name(name)
            self.assertEqual(self.WIN.Get_name(), name)
            self.WIN.name = self.WIN.name
        except NotImplementedError:
            self.skipTest("mpi-win-name")

    @unittest.skipIf(
        MPI.WIN_CREATE_FLAVOR == MPI.KEYVAL_INVALID, "mpi-win-flavor"
    )
    def testCreateFlavor(self):
        flavors = (
            MPI.WIN_FLAVOR_CREATE,
            MPI.WIN_FLAVOR_ALLOCATE,
            MPI.WIN_FLAVOR_DYNAMIC,
            MPI.WIN_FLAVOR_SHARED,
        )
        flavor = self.WIN.Get_attr(MPI.WIN_CREATE_FLAVOR)
        self.assertIn(flavor, flavors)
        self.assertEqual(flavor, self.WIN.flavor)
        self.assertEqual(flavor, self.CREATE_FLAVOR)

    @unittest.skipIf(MPI.WIN_MODEL == MPI.KEYVAL_INVALID, "mpi-win-model")
    def testMemoryModel(self):
        models = (MPI.WIN_SEPARATE, MPI.WIN_UNIFIED)
        model = self.WIN.Get_attr(MPI.WIN_MODEL)
        self.assertIn(model, models)
        self.assertEqual(model, self.WIN.model)

    def testSharedQuery(self):
        flavor = self.WIN.Get_attr(MPI.WIN_CREATE_FLAVOR)
        if flavor != MPI.WIN_FLAVOR_SHARED:
            if MPI.Get_version() < (4, 1):
                return
            if flavor == MPI.WIN_FLAVOR_DYNAMIC:
                return
            if unittest.is_mpi("impi"):
                i_mpi_compat = os.environ.get("I_MPI_COMPATIBILITY", "mpi-3.1")
                if i_mpi_compat in {"3", "4", "5", "mpi-3.1", "mpi-4.0"}:
                    return
                if flavor == MPI.WIN_FLAVOR_CREATE:  # mpi4py/mpi4py#665
                    return
            if unittest.is_mpi("mpich(<4.2.2)"):
                if flavor == MPI.WIN_FLAVOR_CREATE:
                    return
            if unittest.is_mpi("mpich"):  # pmodels/mpich#7499
                if "ch3:nemesis" in MPI.Get_library_version():
                    return
        memory = self.WIN.tomemory()
        address = MPI.Get_address(memory)
        length = len(memory)
        memories = self.COMM.allgather((address, length))
        for i in range(self.COMM.Get_size()):
            query = target = i
            mem, disp = self.WIN.Shared_query(query)
            base = MPI.Get_address(mem)
            size = len(mem)
            if flavor == MPI.WIN_FLAVOR_SHARED or size != 0:
                if self.COMM.Get_rank() == target:
                    self.assertEqual(base, memories[target][0])
                self.assertEqual(size, memories[target][1])
                self.assertEqual(disp, 1)
        query, target = MPI.PROC_NULL, 0
        mem, disp = self.WIN.Shared_query(query)
        base = MPI.Get_address(mem)
        size = len(mem)
        if flavor == MPI.WIN_FLAVOR_SHARED or size != 0:
            if self.COMM.Get_rank() == target:
                self.assertEqual(base, memories[target][0])
            self.assertEqual(size, memories[target][1])
            self.assertEqual(disp, 1)

    def testPyProps(self):
        win = self.WIN
        #
        group = win.group
        self.assertEqual(type(group), MPI.Group)
        self.assertEqual(win.group_size, group.Get_size())
        self.assertEqual(win.group_rank, group.Get_rank())
        group.Free()
        #
        if not unittest.is_mpi("impi(>=2021.15.0)"):
            info = win.info
            self.assertIs(type(info), MPI.Info)
            win.info = info
            info.Free()
        #
        self.assertEqual(type(win.attrs), tuple)
        self.assertEqual(type(win.flavor), int)
        self.assertEqual(type(win.model), int)
        self.assertEqual(type(win.name), str)
        win.name = "mywin"
        self.assertEqual(win.name, "mywin")

    def testPickle(self):
        from pickle import dumps, loads

        with self.assertRaises(ValueError):
            loads(dumps(self.WIN))


class BaseTestWinCreate(BaseTestWin):
    #
    CREATE_FLAVOR = MPI.WIN_FLAVOR_CREATE

    def setUp(self):
        blen = 10 + self.COMM.Get_rank()
        self.memory = MPI.Alloc_mem(blen)
        memzero(self.memory)
        self.WIN = MPI.Win.Create(self.memory, 1, self.INFO, self.COMM)

    def tearDown(self):
        self.WIN.Free()
        MPI.Free_mem(self.memory)


class BaseTestWinAllocate(BaseTestWin):
    #
    CREATE_FLAVOR = MPI.WIN_FLAVOR_ALLOCATE

    def setUp(self):
        blen = 10 + self.COMM.Get_rank()
        self.WIN = MPI.Win.Allocate(blen, 1, self.INFO, self.COMM)
        self.memory = self.WIN.tomemory()
        memzero(self.memory)

    def tearDown(self):
        self.WIN.Free()


class BaseTestWinAllocateShared(BaseTestWin):
    #
    CREATE_FLAVOR = MPI.WIN_FLAVOR_SHARED

    def setUp(self):
        if self.COMM.Get_size() > 1:
            try:
                self.COMM = self.COMM.Split_type(MPI.COMM_TYPE_SHARED)
            except NotImplementedError:
                self.skipTest("mpi-comm-split_type")
        else:
            self.COMM = self.COMM.Dup()
        try:
            blen = 10 + self.COMM.Get_rank()
            self.WIN = MPI.Win.Allocate_shared(blen, 1, self.INFO, self.COMM)
        except Exception:
            self.COMM.Free()
            raise
        self.memory = self.WIN.tomemory()
        memzero(self.memory)

    def tearDown(self):
        self.COMM.Free()
        self.WIN.Free()

    @unittest.skipMPI("mpich(>=4.2.0,<4.3.0)", sys.platform == "linux")
    def testSharedQuery(self):
        super().testSharedQuery()


@unittest.skipMPI("impi(>=2021.14.0,<2021.15.0)", testutil.github())
class BaseTestWinCreateDynamic(BaseTestWin):
    #
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
        self.assertEqual(memory.format, "B")
        base = MPI.Get_address(memory)
        size = len(memory)
        self.assertEqual(base, 0)
        self.assertEqual(size, 0)

    def testAttributes(self):
        base, size, _ = self.WIN.attrs
        self.assertEqual(base, 0)
        self.assertEqual(size, 0)

    @unittest.skipMPI("msmpi(<9.1.0)")
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
    #
    COMM = MPI.COMM_SELF


@unittest.skipMPI("openmpi(<1.4.0)")
class TestWinCreateWorld(BaseTestWinCreate, unittest.TestCase):
    #
    COMM = MPI.COMM_WORLD


class TestWinAllocateSelf(BaseTestWinAllocate, unittest.TestCase):
    #
    COMM = MPI.COMM_SELF


@unittest.skipMPI("openmpi(<1.4.0)")
class TestWinAllocateWorld(BaseTestWinAllocate, unittest.TestCase):
    #
    COMM = MPI.COMM_WORLD


class TestWinAllocateSharedSelf(BaseTestWinAllocateShared, unittest.TestCase):
    #
    COMM = MPI.COMM_SELF


@unittest.skipMPI("mpich", ch3_sock() and MPI.COMM_WORLD.Get_size() > 1)
class TestWinAllocateSharedWorld(BaseTestWinAllocateShared, unittest.TestCase):
    #
    COMM = MPI.COMM_WORLD


class TestWinCreateDynamicSelf(BaseTestWinCreateDynamic, unittest.TestCase):
    #
    COMM = MPI.COMM_SELF


class TestWinCreateDynamicWorld(BaseTestWinCreateDynamic, unittest.TestCase):
    #
    COMM = MPI.COMM_WORLD


try:
    MPI.Win.Create(MPI.BOTTOM, 1, MPI.INFO_NULL, MPI.COMM_SELF).Free()
except (NotImplementedError, MPI.Exception):
    unittest.disable(BaseTestWinCreate, "mpi-win-create")
try:
    MPI.Win.Allocate(1, 1, MPI.INFO_NULL, MPI.COMM_SELF).Free()
except (NotImplementedError, MPI.Exception):
    unittest.disable(BaseTestWinAllocate, "mpi-win-allocate")
try:
    MPI.Win.Allocate_shared(1, 1, MPI.INFO_NULL, MPI.COMM_SELF).Free()
except (NotImplementedError, MPI.Exception):
    unittest.disable(BaseTestWinAllocateShared, "mpi-win-shared")
try:
    MPI.Win.Create_dynamic(MPI.INFO_NULL, MPI.COMM_SELF).Free()
except (NotImplementedError, MPI.Exception):
    unittest.disable(BaseTestWinCreateDynamic, "mpi-win-dynamic")


if __name__ == "__main__":
    unittest.main()
