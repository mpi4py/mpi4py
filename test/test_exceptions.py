from mpi4py import MPI
import mpiunittest as unittest

# --------------------------------------------------------------------

class TestExcDatatypeNull(unittest.TestCase):

    def testDup(self):
        self.assertRaisesMPI(MPI.ERR_TYPE, MPI.DATATYPE_NULL.Dup)

    def testCommit(self):
        self.assertRaisesMPI(MPI.ERR_TYPE, MPI.DATATYPE_NULL.Commit)

    def testFree(self):
        self.assertRaisesMPI(MPI.ERR_TYPE, MPI.DATATYPE_NULL.Free)

class TestExcDatatype(unittest.TestCase):

    DATATYPES = (MPI.BYTE, MPI.PACKED,
                 MPI.CHAR, MPI.WCHAR,
                 MPI.SIGNED_CHAR,  MPI.UNSIGNED_CHAR,
                 MPI.SHORT,  MPI.UNSIGNED_SHORT,
                 MPI.INT,  MPI.UNSIGNED,  MPI.UNSIGNED_INT,
                 MPI.LONG,  MPI.UNSIGNED_LONG,
                 MPI.LONG_LONG, MPI.UNSIGNED_LONG_LONG,
                 MPI.FLOAT,  MPI.DOUBLE, MPI.LONG_DOUBLE,
                 MPI.SHORT_INT,  MPI.TWOINT,  MPI.INT_INT, MPI.LONG_INT,
                 MPI.FLOAT_INT,  MPI.DOUBLE_INT,  MPI.LONG_DOUBLE_INT,
                 MPI.UB,  MPI.LB,)

    ERR_TYPE   = MPI.ERR_TYPE

    def testFreePredefined(self):
        for dtype in self.DATATYPES:
            if dtype != MPI.DATATYPE_NULL:
                self.assertRaisesMPI(self.ERR_TYPE, dtype.Free)
                self.assertTrue(dtype != MPI.DATATYPE_NULL)

    def testKeyvalInvalid(self):
        for dtype in self.DATATYPES:
            if dtype != MPI.DATATYPE_NULL:
                try:
                    self.assertRaisesMPI(
                        [MPI.ERR_KEYVAL, MPI.ERR_OTHER],
                        dtype.Get_attr, MPI.KEYVAL_INVALID)
                except NotImplementedError:
                    return

_name, _version = MPI.get_vendor()
if _name == 'Open MPI':
    if _version < (1, 4, 3):
        TestExcDatatype.DATATYPES  = TestExcDatatype.DATATYPES[1:]
        TestExcDatatype.ERR_TYPE   = MPI.ERR_INTERN

# --------------------------------------------------------------------

class TestExcStatus(unittest.TestCase):

    def testGetCount(self):
        status = MPI.Status()
        self.assertRaisesMPI(
            MPI.ERR_TYPE, status.Get_count, MPI.DATATYPE_NULL)

    def testGetElements(self):
        status = MPI.Status()
        self.assertRaisesMPI(
            MPI.ERR_TYPE, status.Get_elements, MPI.DATATYPE_NULL)

    def testSetElements(self):
        status = MPI.Status()
        self.assertRaisesMPI(
            MPI.ERR_TYPE, status.Set_elements, MPI.DATATYPE_NULL, 0)

# --------------------------------------------------------------------

class TestExcRequestNull(unittest.TestCase):

    def testFree(self):
        self.assertRaisesMPI(MPI.ERR_REQUEST, MPI.REQUEST_NULL.Free)

    def testCancel(self):
        self.assertRaisesMPI(MPI.ERR_REQUEST, MPI.REQUEST_NULL.Cancel)

# --------------------------------------------------------------------

class TestExcOpNull(unittest.TestCase):

    def testFree(self):
        self.assertRaisesMPI([MPI.ERR_OP, MPI.ERR_ARG], MPI.OP_NULL.Free)

class TestExcOp(unittest.TestCase):

    def testFreePredefined(self):
        for op in (MPI.MAX, MPI.MIN,
                   MPI.SUM, MPI.PROD,
                   MPI.LAND, MPI.BAND,
                   MPI.LOR, MPI.BOR,
                   MPI.LXOR, MPI.BXOR,
                   MPI.MAXLOC, MPI.MINLOC):
            self.assertRaisesMPI([MPI.ERR_OP, MPI.ERR_ARG], op.Free)
        if MPI.REPLACE != MPI.OP_NULL:
            self.assertRaisesMPI([MPI.ERR_OP, MPI.ERR_ARG], op.Free)

# --------------------------------------------------------------------

class TestExcInfoNull(unittest.TestCase):

    def testTruth(self):
        self.assertFalse(bool(MPI.INFO_NULL))

    def testDup(self):
        self.assertRaisesMPI(
            [MPI.ERR_INFO, MPI.ERR_ARG], MPI.INFO_NULL.Dup)

    def testFree(self):
        self.assertRaisesMPI(
            [MPI.ERR_INFO, MPI.ERR_ARG], MPI.INFO_NULL.Free)

    def testGet(self):
        self.assertRaisesMPI(
            [MPI.ERR_INFO, MPI.ERR_ARG], MPI.INFO_NULL.Get, 'key')

    def testSet(self):
        self.assertRaisesMPI(
            [MPI.ERR_INFO, MPI.ERR_ARG], MPI.INFO_NULL.Set, 'key', 'value')

    def testDelete(self):
        self.assertRaisesMPI(
            [MPI.ERR_INFO, MPI.ERR_ARG], MPI.INFO_NULL.Delete, 'key')

    def testGetNKeys(self):
        self.assertRaisesMPI(
            [MPI.ERR_INFO, MPI.ERR_ARG], MPI.INFO_NULL.Get_nkeys)

    def testGetNthKey(self):
        self.assertRaisesMPI(
            [MPI.ERR_INFO, MPI.ERR_ARG], MPI.INFO_NULL.Get_nthkey, 0)

class TestExcInfo(unittest.TestCase):

    def setUp(self):
        self.INFO  = MPI.Info.Create()

    def tearDown(self):
        self.INFO.Free()
        self.INFO = None

    def testDelete(self):
        self.assertRaisesMPI(
            MPI.ERR_INFO_NOKEY, self.INFO.Delete, 'key')

    def testGetNthKey(self):
        self.assertRaisesMPI(
            [MPI.ERR_INFO_KEY, MPI.ERR_ARG], self.INFO.Get_nthkey, 0)

try:
    MPI.Info.Create().Free()
except NotImplementedError:
    del TestExcInfoNull, TestExcInfo
else:
    if _name == 'Microsoft MPI': # ???
        del TestExcInfoNull.testDup

# --------------------------------------------------------------------

class TestExcGroupNull(unittest.TestCase):

    def testCompare(self):
        self.assertRaisesMPI(
            MPI.ERR_GROUP, MPI.Group.Compare, MPI.GROUP_NULL,  MPI.GROUP_NULL)
        self.assertRaisesMPI(
            MPI.ERR_GROUP, MPI.Group.Compare, MPI.GROUP_NULL,  MPI.GROUP_EMPTY)
        self.assertRaisesMPI(
            MPI.ERR_GROUP, MPI.Group.Compare, MPI.GROUP_EMPTY, MPI.GROUP_NULL)

    def testAccessors(self):
        for method in ('Get_size', 'Get_rank'):
            self.assertRaisesMPI(
                MPI.ERR_GROUP, getattr(MPI.GROUP_NULL, method))

class TestExcGroup(unittest.TestCase):

    def testFreeEmpty(self):
        self.assertRaisesMPI(MPI.ERR_GROUP, MPI.GROUP_EMPTY.Free)

# --------------------------------------------------------------------

class TestExcCommNull(unittest.TestCase):

    def testCompare(self):
        self.assertRaisesMPI(
            MPI.ERR_COMM, MPI.Comm.Compare, MPI.COMM_NULL,  MPI.COMM_NULL)
        self.assertRaisesMPI(
            MPI.ERR_COMM, MPI.Comm.Compare, MPI.COMM_SELF,  MPI.COMM_NULL)
        self.assertRaisesMPI(
            MPI.ERR_COMM, MPI.Comm.Compare, MPI.COMM_WORLD, MPI.COMM_NULL)
        self.assertRaisesMPI(
            MPI.ERR_COMM, MPI.Comm.Compare, MPI.COMM_NULL,  MPI.COMM_SELF)
        self.assertRaisesMPI(
            MPI.ERR_COMM, MPI.Comm.Compare, MPI.COMM_NULL,  MPI.COMM_WORLD)

    def testAccessors(self):
        for method in ('Get_size', 'Get_rank',
                       'Is_inter', 'Is_intra',
                       'Get_group', 'Get_topology'):
            self.assertRaisesMPI(MPI.ERR_COMM, getattr(MPI.COMM_NULL, method))

    def testFree(self):
        self.assertRaisesMPI(MPI.ERR_COMM, MPI.COMM_NULL.Free)

    def testDisconnect(self):
        try: self.assertRaisesMPI(MPI.ERR_COMM, MPI.COMM_NULL.Disconnect)
        except NotImplementedError: return

    def testGetAttr(self):
        self.assertRaisesMPI(
            MPI.ERR_COMM, MPI.COMM_NULL.Get_attr, MPI.TAG_UB)

    def testGetErrhandler(self):
        self.assertRaisesMPI(
            [MPI.ERR_COMM, MPI.ERR_ARG], MPI.COMM_NULL.Get_errhandler)

    def testSetErrhandler(self):
        self.assertRaisesMPI(
            MPI.ERR_COMM, MPI.COMM_NULL.Set_errhandler, MPI.ERRORS_RETURN)

    def testIntraNull(self):
        comm_null = MPI.Intracomm()
        self.assertRaisesMPI(MPI.ERR_COMM, comm_null.Dup)
        self.assertRaisesMPI(MPI.ERR_COMM, comm_null.Create, MPI.GROUP_EMPTY)
        self.assertRaisesMPI(MPI.ERR_COMM, comm_null.Split, color=0, key=0)

    def testInterNull(self):
        comm_null = MPI.Intercomm()
        self.assertRaisesMPI(MPI.ERR_COMM, comm_null.Get_remote_group)
        self.assertRaisesMPI(MPI.ERR_COMM, comm_null.Get_remote_size)
        self.assertRaisesMPI(MPI.ERR_COMM, comm_null.Dup)
        self.assertRaisesMPI(MPI.ERR_COMM, comm_null.Create, MPI.GROUP_EMPTY)
        self.assertRaisesMPI(MPI.ERR_COMM, comm_null.Split, color=0, key=0)
        self.assertRaisesMPI(MPI.ERR_COMM, comm_null.Merge, high=True)


class TestExcComm(unittest.TestCase):

    def testFreeSelf(self):
        self.assertRaisesMPI(
            [MPI.ERR_COMM, MPI.ERR_ARG], MPI.COMM_SELF.Free)

    def testFreeWorld(self):
        self.assertRaisesMPI(
            [MPI.ERR_COMM, MPI.ERR_ARG], MPI.COMM_WORLD.Free)

    def testKeyvalInvalid(self):
        self.assertRaisesMPI(
            [MPI.ERR_KEYVAL, MPI.ERR_OTHER],
            MPI.COMM_SELF.Get_attr, MPI.KEYVAL_INVALID)

_name, _version = MPI.get_vendor()
if _name == 'Open MPI':
    if _version < (1, 4, 2):
        del TestExcCommNull.testGetAttr
    if _version < (1, 4, 1):
        del TestExcCommNull.testGetErrhandler

# --------------------------------------------------------------------

class TestExcWinNull(unittest.TestCase):

    def testFree(self):
        self.assertRaisesMPI(
            [MPI.ERR_WIN, MPI.ERR_ARG], MPI.WIN_NULL.Free)

    def testGetErrhandler(self):
        self.assertRaisesMPI(
            [MPI.ERR_WIN, MPI.ERR_ARG], MPI.WIN_NULL.Get_errhandler)

    def testSetErrhandler(self):
        self.assertRaisesMPI(
            [MPI.ERR_WIN, MPI.ERR_ARG],
            MPI.WIN_NULL.Set_errhandler, MPI.ERRORS_RETURN)

    def testCallErrhandler(self):
        self.assertRaisesMPI([MPI.ERR_WIN, MPI.ERR_ARG],
                             MPI.WIN_NULL.Call_errhandler, 0)


class TestExcWin(unittest.TestCase):

    def setUp(self):
        self.WIN = MPI.Win.Create(None, 1, MPI.INFO_NULL, MPI.COMM_SELF)

    def tearDown(self):
        self.WIN.Free()
        self.WIN = None

    def testKeyvalInvalid(self):
        self.assertRaisesMPI(
            [MPI.ERR_KEYVAL, MPI.ERR_OTHER],
            self.WIN.Get_attr, MPI.KEYVAL_INVALID)

try:
    w = MPI.Win.Create(None, 1, MPI.INFO_NULL, MPI.COMM_SELF)
    w.Free()
except NotImplementedError:
    del TestExcWinNull, TestExcWin

# --------------------------------------------------------------------

class TestExcErrhandlerNull(unittest.TestCase):

    def testFree(self):
        self.assertRaisesMPI(MPI.ERR_ARG, MPI.ERRHANDLER_NULL.Free)

    def testCommSetErrhandler(self):
        self.assertRaisesMPI(
            MPI.ERR_ARG, MPI.COMM_SELF.Set_errhandler, MPI.ERRHANDLER_NULL)
        self.assertRaisesMPI(
            MPI.ERR_ARG, MPI.COMM_WORLD.Set_errhandler, MPI.ERRHANDLER_NULL)

class TestExcErrhandler(unittest.TestCase):

    def testFreePredefined(self):
        #self.assertRaisesMPI(MPI.ERR_ARG, MPI.ERRORS_ARE_FATAL.Free)
        #self.assertRaisesMPI(MPI.ERR_ARG, MPI.ERRORS_RETURN.Free)
        pass

# --------------------------------------------------------------------

import sys
name, version = MPI.get_vendor()
if name == 'MPICH2':
    try:
        MPI.DATATYPE_NULL.Get_size()
    except MPI.Exception:
        pass
    else:
        del TestExcDatatypeNull
        del TestExcDatatype
        del TestExcStatus
        del TestExcRequestNull
        del TestExcOpNull
        del TestExcOp
        del TestExcInfoNull
        del TestExcInfo
        del TestExcGroupNull
        del TestExcGroup
        del TestExcCommNull
        del TestExcComm
        del TestExcWinNull
        del TestExcWin
        del TestExcErrhandlerNull
        del TestExcErrhandler
elif name == 'Open MPI':
    if 'win' in sys.platform:
        del TestExcDatatypeNull
        del TestExcDatatype
        del TestExcStatus
        del TestExcRequestNull
        del TestExcOpNull
        del TestExcOp
        del TestExcInfoNull
        del TestExcInfo
        del TestExcGroupNull
        del TestExcGroup
        del TestExcCommNull
        del TestExcComm
        del TestExcWinNull
        del TestExcWin
        del TestExcErrhandlerNull
        del TestExcErrhandler
elif name == 'HP MPI':
        del TestExcDatatypeNull
        del TestExcDatatype
        del TestExcStatus
        del TestExcRequestNull
        del TestExcOpNull
        del TestExcOp
        del TestExcInfoNull
        del TestExcInfo
        del TestExcGroupNull
        del TestExcGroup
        del TestExcCommNull
        del TestExcComm
        del TestExcWinNull
        del TestExcWin
        del TestExcErrhandlerNull
        del TestExcErrhandler

# --------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()

# --------------------------------------------------------------------
