import mpiunittest as unittest

from mpi4py import MPI

# -----------------------------------------------------------------------------

_errclasscache = {}


def ErrClassName(ierr):
    if not _errclasscache:
        from mpi4py import MPI

        _errclasscache[MPI.SUCCESS] = "SUCCESS"
        for entry in dir(MPI):
            if entry.startswith("ERR_"):
                errcls = getattr(MPI, entry)
                _errclasscache[errcls] = entry
    return _errclasscache.get(ierr, "<unknown>")


@unittest.skipMPI("MPICH2")
class BaseTestCase(unittest.TestCase):
    #
    def setUp(self):
        self.errhdl_world = MPI.COMM_WORLD.Get_errhandler()
        MPI.COMM_WORLD.Set_errhandler(MPI.ERRORS_RETURN)
        self.errhdl_self = MPI.COMM_SELF.Get_errhandler()
        MPI.COMM_SELF.Set_errhandler(MPI.ERRORS_RETURN)

    def tearDown(self):
        MPI.COMM_WORLD.Set_errhandler(self.errhdl_world)
        self.errhdl_world.Free()
        MPI.COMM_SELF.Set_errhandler(self.errhdl_self)
        self.errhdl_self.Free()

    def assertRaisesMPI(self, IErrClass, callableObj, *args, **kwargs):
        from mpi4py import MPI

        excClass = MPI.Exception
        try:
            callableObj(*args, **kwargs)
        except NotImplementedError:
            if MPI.Get_version() >= (2, 0):
                raise
            raise self.failureException("raised NotImplementedError") from None
        except excClass as excValue:
            error_class = excValue.Get_error_class()
        else:
            error_class = None
        if error_class is not None:
            if isinstance(IErrClass, (list, tuple, set)):
                match = error_class in IErrClass
            else:
                match = error_class == IErrClass
            if not match:
                if isinstance(IErrClass, (list, tuple, set)):
                    IErrClassName = [ErrClassName(e) for e in IErrClass]
                    IErrClassName = type(IErrClass)(IErrClassName)
                else:
                    IErrClassName = ErrClassName(IErrClass)
                raise self.failureException(
                    f"generated error class "
                    f"is '{ErrClassName(error_class)}' ({error_class}), "
                    f"but expected '{IErrClassName}' ({IErrClass})"
                )
        else:
            raise self.failureException(f"{excClass.__name__} not raised")


# -----------------------------------------------------------------------------


class TestExcDatatypeNull(BaseTestCase):
    #
    def testDup(self):
        self.assertRaisesMPI(
            MPI.ERR_TYPE,
            MPI.DATATYPE_NULL.Dup,
        )

    def testCommit(self):
        self.assertRaisesMPI(
            MPI.ERR_TYPE,
            MPI.DATATYPE_NULL.Commit,
        )

    def testFree(self):
        self.assertRaisesMPI(
            MPI.ERR_TYPE,
            MPI.DATATYPE_NULL.Free,
        )


class TestExcDatatype(BaseTestCase):
    #
    DATATYPES = (
        MPI.BYTE,
        MPI.PACKED,
        MPI.CHAR,
        MPI.WCHAR,
        MPI.SIGNED_CHAR,
        MPI.UNSIGNED_CHAR,
        MPI.SHORT,
        MPI.UNSIGNED_SHORT,
        MPI.INT,
        MPI.UNSIGNED,
        MPI.UNSIGNED_INT,
        MPI.LONG,
        MPI.UNSIGNED_LONG,
        MPI.LONG_LONG,
        MPI.UNSIGNED_LONG_LONG,
        MPI.FLOAT,
        MPI.DOUBLE,
        MPI.LONG_DOUBLE,
        MPI.SHORT_INT,
        MPI.TWOINT,
        MPI.INT_INT,
        MPI.LONG_INT,
        MPI.FLOAT_INT,
        MPI.DOUBLE_INT,
        MPI.LONG_DOUBLE_INT,
    )

    ERR_TYPE = MPI.ERR_TYPE

    @unittest.skipMPI("msmpi")
    def testFreePredefined(self):
        for dtype in self.DATATYPES:
            if dtype == MPI.DATATYPE_NULL:
                continue
            self.assertRaisesMPI(
                self.ERR_TYPE,
                dtype.Free,
            )
            self.assertNotEqual(dtype, MPI.DATATYPE_NULL)

    def testKeyvalInvalid(self):
        for dtype in self.DATATYPES:
            if dtype == MPI.DATATYPE_NULL:
                continue
            try:
                self.assertRaisesMPI(
                    [MPI.ERR_KEYVAL, MPI.ERR_OTHER],
                    dtype.Get_attr,
                    MPI.KEYVAL_INVALID,
                )
            except NotImplementedError:
                self.skipTest("mpi-type-get_attr")


name, version = MPI.get_vendor()
if name == "Open MPI":
    if version < (1, 4, 3):
        TestExcDatatype.DATATYPES = TestExcDatatype.DATATYPES[1:]
        TestExcDatatype.ERR_TYPE = MPI.ERR_INTERN

# -----------------------------------------------------------------------------


@unittest.skipMPI("msmpi(<=4.2.0)")
class TestExcStatus(BaseTestCase):
    #
    def testGetCount(self):
        status = MPI.Status()
        self.assertRaisesMPI(
            MPI.ERR_TYPE,
            status.Get_count,
            MPI.DATATYPE_NULL,
        )

    def testGetElements(self):
        status = MPI.Status()
        self.assertRaisesMPI(
            MPI.ERR_TYPE,
            status.Get_elements,
            MPI.DATATYPE_NULL,
        )

    @unittest.skipMPI("MPICH1")
    def testSetElements(self):
        status = MPI.Status()
        self.assertRaisesMPI(
            MPI.ERR_TYPE,
            status.Set_elements,
            MPI.DATATYPE_NULL,
            0,
        )


# -----------------------------------------------------------------------------


class TestExcRequestNull(BaseTestCase):
    #
    def testFree(self):
        self.assertRaisesMPI(
            MPI.ERR_REQUEST,
            MPI.REQUEST_NULL.Free,
        )

    def testCancel(self):
        self.assertRaisesMPI(
            MPI.ERR_REQUEST,
            MPI.REQUEST_NULL.Cancel,
        )


# -----------------------------------------------------------------------------


class TestExcOpNull(BaseTestCase):
    #
    def testFree(self):
        self.assertRaisesMPI(
            [MPI.ERR_OP, MPI.ERR_ARG],
            MPI.OP_NULL.Free,
        )


class TestExcOp(BaseTestCase):
    #
    OPS = (
        MPI.MAX,
        MPI.MIN,
        MPI.SUM,
        MPI.PROD,
        MPI.LAND,
        MPI.BAND,
        MPI.LOR,
        MPI.BOR,
        MPI.LXOR,
        MPI.BXOR,
        MPI.MAXLOC,
        MPI.MINLOC,
        MPI.REPLACE,
        MPI.NO_OP,
    )

    def testFreePredefined(self):
        for op in self.OPS:
            if op == MPI.OP_NULL:
                continue
            self.assertRaisesMPI(
                [MPI.ERR_OP, MPI.ERR_ARG],
                op.Free,
            )
            self.assertNotEqual(op, MPI.OP_NULL)


# -----------------------------------------------------------------------------


class TestExcInfoNull(BaseTestCase):
    #
    def testFree(self):
        self.assertRaisesMPI(
            [MPI.ERR_INFO, MPI.ERR_ARG],
            MPI.INFO_NULL.Free,
        )

    def testTruth(self):
        self.assertFalse(bool(MPI.INFO_NULL))

    @unittest.skipMPI("msmpi(<8.1.0)")
    def testDup(self):
        self.assertRaisesMPI(
            [MPI.ERR_INFO, MPI.ERR_ARG],
            MPI.INFO_NULL.Dup,
        )

    def testGet(self):
        self.assertRaisesMPI(
            [MPI.ERR_INFO, MPI.ERR_ARG],
            MPI.INFO_NULL.Get,
            "key",
        )

    def testSet(self):
        self.assertRaisesMPI(
            [MPI.ERR_INFO, MPI.ERR_ARG],
            MPI.INFO_NULL.Set,
            "key",
            "value",
        )

    def testDelete(self):
        self.assertRaisesMPI(
            [MPI.ERR_INFO, MPI.ERR_ARG],
            MPI.INFO_NULL.Delete,
            "key",
        )

    def testGetNKeys(self):
        self.assertRaisesMPI(
            [MPI.ERR_INFO, MPI.ERR_ARG],
            MPI.INFO_NULL.Get_nkeys,
        )

    def testGetNthKey(self):
        self.assertRaisesMPI(
            [MPI.ERR_INFO, MPI.ERR_ARG],
            MPI.INFO_NULL.Get_nthkey,
            0,
        )


class TestExcInfoEnv(BaseTestCase):
    #
    @unittest.skipMPI("mvapich")
    @unittest.skipMPI("mpich(<4.2.0)")
    @unittest.skipMPI("impi(<2021.16.0)")
    @unittest.skipMPI("openmpi", MPI.Get_version() < (5, 0))
    def testFree(self):
        self.assertRaisesMPI(
            [MPI.ERR_INFO, MPI.ERR_ARG],
            MPI.INFO_ENV.Free,
        )


class TestExcInfo(BaseTestCase):
    #
    def setUp(self):
        super().setUp()
        self.INFO = MPI.Info.Create()

    def tearDown(self):
        self.INFO.Free()
        self.INFO = None
        super().tearDown()

    def testDelete(self):
        self.assertRaisesMPI(
            MPI.ERR_INFO_NOKEY,
            self.INFO.Delete,
            "key",
        )

    def testGetNthKey(self):
        self.assertRaisesMPI(
            [MPI.ERR_INFO_KEY, MPI.ERR_ARG],
            self.INFO.Get_nthkey,
            0,
        )


try:
    MPI.Info.Create().Free()
except NotImplementedError:
    unittest.disable(TestExcInfo, "mpi-info")
    unittest.disable(TestExcInfoNull, "mpi-info")

# -----------------------------------------------------------------------------


class TestExcGroupNull(BaseTestCase):
    #
    def testCompare(self):
        self.assertRaisesMPI(
            MPI.ERR_GROUP,
            MPI.Group.Compare,
            MPI.GROUP_NULL,
            MPI.GROUP_NULL,
        )
        self.assertRaisesMPI(
            MPI.ERR_GROUP,
            MPI.Group.Compare,
            MPI.GROUP_NULL,
            MPI.GROUP_EMPTY,
        )
        self.assertRaisesMPI(
            MPI.ERR_GROUP,
            MPI.Group.Compare,
            MPI.GROUP_EMPTY,
            MPI.GROUP_NULL,
        )

    def testAccessors(self):
        for method in ("Get_size", "Get_rank"):
            self.assertRaisesMPI(
                MPI.ERR_GROUP,
                getattr(MPI.GROUP_NULL, method),
            )


class TestExcGroup(BaseTestCase):
    #
    pass


# -----------------------------------------------------------------------------


class TestExcSessionNull(BaseTestCase):
    #
    def testGetNumPsets(self):
        self.assertRaisesMPI(
            MPI.ERR_SESSION,
            MPI.SESSION_NULL.Get_num_psets,
        )

    def testGetNthPset(self):
        self.assertRaisesMPI(
            MPI.ERR_SESSION,
            MPI.SESSION_NULL.Get_nth_pset,
            0,
        )

    def testGetInfo(self):
        self.assertRaisesMPI(
            MPI.ERR_SESSION,
            MPI.SESSION_NULL.Get_info,
        )

    def testGetPsetInfo(self):
        self.assertRaisesMPI(
            MPI.ERR_SESSION,
            MPI.SESSION_NULL.Get_pset_info,
            "mpi://SELF",
        )

    def testCreateGroup(self):
        self.assertRaisesMPI(
            MPI.ERR_SESSION,
            MPI.SESSION_NULL.Create_group,
            "mpi://SELF",
        )

    def testGetErrhandler(self):
        self.assertRaisesMPI(
            MPI.ERR_SESSION,
            MPI.SESSION_NULL.Get_errhandler,
        )

    def testSetErrhandler(self):
        self.assertRaisesMPI(
            MPI.ERR_SESSION,
            MPI.SESSION_NULL.Set_errhandler,
            MPI.ERRORS_RETURN,
        )


class TestExcSession(BaseTestCase):
    #
    def setUp(self):
        super().setUp()
        self.SESSION = MPI.Session.Init()
        self.SESSION.Set_errhandler(MPI.ERRORS_RETURN)

    def tearDown(self):
        self.SESSION.Finalize()
        self.SESSION = None
        super().tearDown()

    def testGetNthPsetNeg(self):
        self.assertRaisesMPI(
            MPI.ERR_ARG,
            self.SESSION.Get_nth_pset,
            -1,
        )

    @unittest.skipMPI("mpich(<4.1.0)")
    def testGetNthPsetPos(self):
        self.assertRaisesMPI(
            MPI.ERR_ARG,
            self.SESSION.Get_nth_pset,
            self.SESSION.Get_num_psets(),
        )

    def testGetPsetInfo(self):
        self.assertRaisesMPI(
            MPI.ERR_ARG,
            self.SESSION.Get_pset_info,
            "@qerty!#$",
        )

    def testCreateGroup(self):
        self.assertRaisesMPI(
            [MPI.ERR_ARG, MPI.ERR_UNSUPPORTED_OPERATION],
            self.SESSION.Create_group,
            "@qerty!#$",
        )


try:
    MPI.Session.Init().Finalize()
except NotImplementedError:
    unittest.disable(TestExcSessionNull, "mpi-session")
    unittest.disable(TestExcSession, "mpi-session")

# -----------------------------------------------------------------------------


class TestExcCommNull(BaseTestCase):
    #
    ERR_COMM = MPI.ERR_COMM

    def testFree(self):
        self.assertRaisesMPI(
            MPI.ERR_COMM,
            MPI.COMM_NULL.Free,
        )

    def testCompare(self):
        self.assertRaisesMPI(
            self.ERR_COMM,
            MPI.Comm.Compare,
            MPI.COMM_NULL,
            MPI.COMM_NULL,
        )
        self.assertRaisesMPI(
            self.ERR_COMM,
            MPI.Comm.Compare,
            MPI.COMM_SELF,
            MPI.COMM_NULL,
        )
        self.assertRaisesMPI(
            self.ERR_COMM,
            MPI.Comm.Compare,
            MPI.COMM_WORLD,
            MPI.COMM_NULL,
        )
        self.assertRaisesMPI(
            self.ERR_COMM,
            MPI.Comm.Compare,
            MPI.COMM_NULL,
            MPI.COMM_SELF,
        )
        self.assertRaisesMPI(
            self.ERR_COMM,
            MPI.Comm.Compare,
            MPI.COMM_NULL,
            MPI.COMM_WORLD,
        )

    def testAccessors(self):
        for method in (
            "Get_size",
            "Get_rank",
            "Is_inter",
            "Is_intra",
            "Get_group",
            "Get_topology",
        ):
            self.assertRaisesMPI(
                MPI.ERR_COMM,
                getattr(MPI.COMM_NULL, method),
            )

    def testDisconnect(self):
        try:
            self.assertRaisesMPI(
                MPI.ERR_COMM,
                MPI.COMM_NULL.Disconnect,
            )
        except NotImplementedError:
            self.skipTest("mpi-comm-disconnect")

    @unittest.skipMPI("openmpi(<1.4.2)")
    def testGetAttr(self):
        self.assertRaisesMPI(
            MPI.ERR_COMM,
            MPI.COMM_NULL.Get_attr,
            MPI.TAG_UB,
        )

    @unittest.skipMPI("openmpi(<1.4.1)")
    def testGetErrhandler(self):
        self.assertRaisesMPI(
            [MPI.ERR_COMM, MPI.ERR_ARG],
            MPI.COMM_NULL.Get_errhandler,
        )

    def testSetErrhandler(self):
        self.assertRaisesMPI(
            MPI.ERR_COMM,
            MPI.COMM_NULL.Set_errhandler,
            MPI.ERRORS_RETURN,
        )

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


class TestExcComm(BaseTestCase):
    #
    @unittest.skipMPI("MPICH1")
    def testFreeSelf(self):
        errhdl = MPI.COMM_SELF.Get_errhandler()
        try:
            MPI.COMM_SELF.Set_errhandler(MPI.ERRORS_RETURN)
            self.assertRaisesMPI(
                [MPI.ERR_COMM, MPI.ERR_ARG],
                MPI.COMM_SELF.Free,
            )
        finally:
            MPI.COMM_SELF.Set_errhandler(errhdl)
            errhdl.Free()

    @unittest.skipMPI("MPICH1")
    def testFreeWorld(self):
        self.assertRaisesMPI(
            [MPI.ERR_COMM, MPI.ERR_ARG],
            MPI.COMM_WORLD.Free,
        )

    def testKeyvalInvalid(self):
        self.assertRaisesMPI(
            [MPI.ERR_KEYVAL, MPI.ERR_OTHER],
            MPI.COMM_WORLD.Get_attr,
            MPI.KEYVAL_INVALID,
        )


# -----------------------------------------------------------------------------


class TestExcWinNull(BaseTestCase):
    #
    ERRORS = [MPI.ERR_WIN, MPI.ERR_ARG]
    if unittest.is_mpi("msmpi"):
        ERRORS += [MPI.ERR_OTHER]

    def testFree(self):
        self.assertRaisesMPI(
            self.ERRORS,
            MPI.WIN_NULL.Free,
        )

    def testGetErrhandler(self):
        self.assertRaisesMPI(
            self.ERRORS,
            MPI.WIN_NULL.Get_errhandler,
        )

    def testSetErrhandler(self):
        self.assertRaisesMPI(
            self.ERRORS,
            MPI.WIN_NULL.Set_errhandler,
            MPI.ERRORS_RETURN,
        )

    def testCallErrhandler(self):
        self.assertRaisesMPI(
            [MPI.ERR_WIN, MPI.ERR_ARG],
            MPI.WIN_NULL.Call_errhandler,
            0,
        )


class TestExcWin(BaseTestCase):
    #
    def setUp(self):
        super().setUp()
        self.WIN = MPI.Win.Create(None, 1, MPI.INFO_NULL, MPI.COMM_SELF)
        self.WIN.Set_errhandler(MPI.ERRORS_RETURN)

    def tearDown(self):
        self.WIN.Free()
        self.WIN = None
        super().tearDown()

    def testKeyvalInvalid(self):
        self.assertRaisesMPI(
            [MPI.ERR_KEYVAL, MPI.ERR_OTHER],
            self.WIN.Get_attr,
            MPI.KEYVAL_INVALID,
        )


try:
    MPI.Win.Create(None, 1, MPI.INFO_NULL, MPI.COMM_SELF).Free()
except (NotImplementedError, MPI.Exception):
    unittest.disable(TestExcWin, "mpi-win")
    unittest.disable(TestExcWinNull, "mpi-win")

# -----------------------------------------------------------------------------


class TestExcErrhandlerNull(BaseTestCase):
    #
    def testFree(self):
        self.assertRaisesMPI(
            [MPI.ERR_ERRHANDLER, MPI.ERR_ARG],
            MPI.ERRHANDLER_NULL.Free,
        )

    def testCommSelfSetErrhandler(self):
        self.assertRaisesMPI(
            [MPI.ERR_ERRHANDLER, MPI.ERR_ARG],
            MPI.COMM_SELF.Set_errhandler,
            MPI.ERRHANDLER_NULL,
        )

    def testCommWorldSetErrhandler(self):
        self.assertRaisesMPI(
            [MPI.ERR_ERRHANDLER, MPI.ERR_ARG],
            MPI.COMM_WORLD.Set_errhandler,
            MPI.ERRHANDLER_NULL,
        )


class TestExcErrhandler(BaseTestCase):
    #
    pass


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()

# -----------------------------------------------------------------------------
