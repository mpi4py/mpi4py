import os
import pathlib
import tempfile

import mpiunittest as unittest

from mpi4py import MPI

# ---


class MyBaseComm:
    #
    def free(self):
        if self != MPI.COMM_NULL:
            MPI.Comm.Free(self)


class BaseTestBaseComm:
    #
    def setUp(self):
        self.comm = self.CommType(self.COMM_BASE)

    def testSubType(self):
        self.assertNotIn(
            type(self.comm),
            [
                MPI.Comm,
                MPI.Intracomm,
                MPI.Cartcomm,
                MPI.Graphcomm,
                MPI.Distgraphcomm,
                MPI.Intercomm,
            ],
        )
        self.assertIsInstance(self.comm, self.CommType)

    def testCloneFree(self):
        if self.COMM_BASE != MPI.COMM_NULL:
            comm = self.comm.Clone()
        else:
            comm = self.CommType()
        self.assertIsInstance(comm, MPI.Comm)
        self.assertIsInstance(comm, self.CommType)
        comm.free()

    def tearDown(self):
        self.comm.free()


# ---


class MyComm(MPI.Comm, MyBaseComm):
    #
    def __new__(cls, comm=None):
        if comm is not None:
            if comm != MPI.COMM_NULL:
                comm = comm.Clone()
        return super().__new__(cls, comm)


class BaseTestMyComm(BaseTestBaseComm):
    #
    CommType = MyComm


class TestMyCommNULL(BaseTestMyComm, unittest.TestCase):
    #
    COMM_BASE = MPI.COMM_NULL


class TestMyCommSELF(BaseTestMyComm, unittest.TestCase):
    #
    COMM_BASE = MPI.COMM_SELF


class TestMyCommWORLD(BaseTestMyComm, unittest.TestCase):
    #
    COMM_BASE = MPI.COMM_WORLD


# ---


class MyIntracomm(MPI.Intracomm, MyBaseComm):
    #
    def __new__(cls, comm=None):
        if comm is not None:
            if comm != MPI.COMM_NULL:
                comm = comm.Dup()
        return super().__new__(cls, comm)


class BaseTestMyIntracomm(BaseTestBaseComm):
    #
    CommType = MyIntracomm


class TestMyIntracommNULL(BaseTestMyIntracomm, unittest.TestCase):
    #
    COMM_BASE = MPI.COMM_NULL


class TestMyIntracommSELF(BaseTestMyIntracomm, unittest.TestCase):
    #
    COMM_BASE = MPI.COMM_SELF


class TestMyIntracommWORLD(BaseTestMyIntracomm, unittest.TestCase):
    #
    COMM_BASE = MPI.COMM_WORLD


# ---


class MyCartcomm(MPI.Cartcomm, MyBaseComm):
    #
    def __new__(cls, comm=None):
        if comm is not None:
            if comm != MPI.COMM_NULL:
                dims = [comm.size]
                comm = comm.Create_cart(dims)
        return super().__new__(cls, comm)


class BaseTestMyCartcomm(BaseTestBaseComm):
    #
    CommType = MyCartcomm


class TestMyCartcommNULL(BaseTestMyCartcomm, unittest.TestCase):
    #
    COMM_BASE = MPI.COMM_NULL


class TestMyCartcommSELF(BaseTestMyCartcomm, unittest.TestCase):
    #
    COMM_BASE = MPI.COMM_SELF


class TestMyCartcommWORLD(BaseTestMyCartcomm, unittest.TestCase):
    #
    COMM_BASE = MPI.COMM_WORLD


# ---


class MyGraphcomm(MPI.Graphcomm, MyBaseComm):
    #
    def __new__(cls, comm=None):
        if comm is not None:
            if comm != MPI.COMM_NULL:
                index = list(range(comm.size + 1))
                edges = list(range(comm.size))
                comm = comm.Create_graph(index, edges)
        return super().__new__(cls, comm)


class BaseTestMyGraphcomm(BaseTestBaseComm):
    #
    CommType = MyGraphcomm


class TestMyGraphcommNULL(BaseTestMyGraphcomm, unittest.TestCase):
    #
    COMM_BASE = MPI.COMM_NULL


class TestMyGraphcommSELF(BaseTestMyGraphcomm, unittest.TestCase):
    #
    COMM_BASE = MPI.COMM_SELF


class TestMyGraphcommWORLD(BaseTestMyGraphcomm, unittest.TestCase):
    #
    COMM_BASE = MPI.COMM_WORLD


# ---


class MyRequest(MPI.Request):
    #
    def __new__(cls, request=None):
        return super().__new__(cls, request)

    def test(self):
        return super(type(self), self).Test()

    def wait(self):
        return super(type(self), self).Wait()


class MyPrequest(MPI.Prequest):
    #
    def __new__(cls, request=None):
        return super().__new__(cls, request)

    def test(self):
        return super(type(self), self).Test()

    def wait(self):
        return super(type(self), self).Wait()

    def start(self):
        return super(type(self), self).Start()


class MyGrequest(MPI.Grequest):
    #
    def __new__(cls, request=None):
        return super().__new__(cls, request)

    def test(self):
        return super(type(self), self).Test()

    def wait(self):
        return super(type(self), self).Wait()


class BaseTestMyRequest:
    #
    def setUp(self):
        self.req = self.MyRequestType(MPI.REQUEST_NULL)

    def testSubType(self):
        self.assertIsNot(type(self.req), self.MPIRequestType)
        self.assertIsInstance(self.req, self.MPIRequestType)
        self.assertIsInstance(self.req, self.MyRequestType)
        self.req.test()


class TestMyRequest(BaseTestMyRequest, unittest.TestCase):
    #
    MPIRequestType = MPI.Request
    MyRequestType = MyRequest


class TestMyPrequest(BaseTestMyRequest, unittest.TestCase):
    #
    MPIRequestType = MPI.Prequest
    MyRequestType = MyPrequest


class TestMyGrequest(BaseTestMyRequest, unittest.TestCase):
    #
    MPIRequestType = MPI.Grequest
    MyRequestType = MyGrequest


class TestMyRequest2(TestMyRequest):
    #
    def setUp(self):
        req = MPI.COMM_SELF.Isend(
            [MPI.BOTTOM, 0, MPI.BYTE], dest=MPI.PROC_NULL, tag=0
        )
        self.req = MyRequest(req)


@unittest.skipMPI("mpich(==3.4.1)")
class TestMyPrequest2(TestMyPrequest):
    #
    def setUp(self):
        req = MPI.COMM_SELF.Send_init(
            [MPI.BOTTOM, 0, MPI.BYTE], dest=MPI.PROC_NULL, tag=0
        )
        self.req = MyPrequest(req)

    def tearDown(self):
        self.req.Free()

    def testStart(self):
        for _i in range(5):
            self.req.start()
            self.req.test()
            self.req.start()
            self.req.wait()


# ---


class MyInfo(MPI.Info):
    #
    def __new__(cls, info=None):
        return MPI.Info.__new__(cls, info)

    def free(self):
        if self != MPI.INFO_NULL:
            MPI.Info.Free(self)


class BaseTestMyInfo:
    #
    def setUp(self):
        info = MPI.Info.Create()
        self.info = MyInfo(info)

    def tearDown(self):
        self.info.free()

    def testSubType(self):
        self.assertIsNot(type(self.info), MPI.Info)
        self.assertIsInstance(self.info, MPI.Info)
        self.assertIsInstance(self.info, MyInfo)

    def testFree(self):
        self.assertTrue(self.info)
        self.info.free()
        self.assertFalse(self.info)

    def testCreateDupType(self):
        for info in (
            MyInfo.Create(),
            self.info.Dup(),
            self.info.copy(),
        ):
            self.assertIsNot(type(info), MPI.Info)
            self.assertIsInstance(info, MPI.Info)
            self.assertIsInstance(info, MyInfo)
            info.free()

    def testCreateEnvType(self):
        try:
            info = MyInfo.Create_env()
        except NotImplementedError:
            if MPI.Get_version() >= (4, 0):
                raise
            raise unittest.SkipTest("mpi-info-create-env") from None
        self.assertIsNot(type(info), MPI.Info)
        self.assertIsInstance(info, MPI.Info)
        self.assertIsInstance(info, MyInfo)

    def testPickle(self):
        from pickle import dumps, loads

        items = list(zip("abc", "123"))
        self.info.update(items)
        info = loads(dumps(self.info))
        self.assertIs(type(info), MyInfo)
        self.assertEqual(info.items(), items)
        info.free()


class TestMyInfo(BaseTestMyInfo, unittest.TestCase):
    #
    pass


try:
    MPI.Info.Create().Free()
except (NotImplementedError, MPI.Exception):
    unittest.disable(BaseTestMyInfo, "mpi-info")

# ---


class MyWin(MPI.Win):
    #
    def __new__(cls, win=None):
        return MPI.Win.__new__(cls, win)

    def free(self):
        if self != MPI.WIN_NULL:
            MPI.Win.Free(self)


class BaseTestMyWin:
    #
    def setUp(self):
        w = MPI.Win.Create(MPI.BOTTOM)
        self.win = MyWin(w)

    def tearDown(self):
        self.win.free()

    def testSubType(self):
        self.assertIsNot(type(self.win), MPI.Win)
        self.assertIsInstance(self.win, MPI.Win)
        self.assertIsInstance(self.win, MyWin)

    def testFree(self):
        self.assertTrue(self.win)
        self.win.free()
        self.assertFalse(self.win)


class TestMyWin(BaseTestMyWin, unittest.TestCase):
    #
    pass


try:
    MPI.Win.Create(MPI.BOTTOM).Free()
except (NotImplementedError, MPI.Exception):
    unittest.disable(BaseTestMyWin, "mpi-win")

# ---


class MyFile(MPI.File):
    #
    def __new__(cls, file=None):
        return MPI.File.__new__(cls, file)

    def close(self):
        if self != MPI.FILE_NULL:
            MPI.File.Close(self)


class BaseTestMyFile:
    #
    def openfile(self):
        fd, fname = tempfile.mkstemp(prefix="mpi4py")
        os.close(fd)
        fname = pathlib.Path(fname)
        amode = MPI.MODE_RDWR | MPI.MODE_CREATE | MPI.MODE_DELETE_ON_CLOSE
        try:
            self.file = MPI.File.Open(
                MPI.COMM_SELF, fname, amode, MPI.INFO_NULL
            )
        except Exception:
            fname.unlink()
            raise
        return self.file

    def setUp(self):
        f = self.openfile()
        self.file = MyFile(f)

    def tearDown(self):
        self.file.close()

    def testSubType(self):
        self.assertIsNot(type(self.file), MPI.File)
        self.assertIsInstance(self.file, MPI.File)
        self.assertIsInstance(self.file, MyFile)

    def testFree(self):
        self.assertTrue(self.file)
        self.file.close()
        self.assertFalse(self.file)


class TestMyFile(BaseTestMyFile, unittest.TestCase):
    #
    pass


try:
    BaseTestMyFile().openfile().Close()
except NotImplementedError:
    unittest.disable(BaseTestMyFile, "mpi-file")

# ---

if __name__ == "__main__":
    unittest.main()
