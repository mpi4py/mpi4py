from mpi4py import MPI
import mpiunittest as unittest
import sys

# ---

class MyBaseComm(object):

    def free(self):
        if self != MPI.COMM_NULL:
            MPI.Comm.Free(self)

class BaseTestBaseComm(object):

    def setUp(self):
        self.comm = self.CommType(self.COMM_BASE)

    def testSubType(self):
        self.assertTrue(type(self.comm) not in [
                MPI.Comm,
                MPI.Intracomm,
                MPI.Cartcomm,
                MPI.Graphcomm,
                MPI.Distgraphcomm,
                MPI.Intercomm])
        self.assertTrue(isinstance(self.comm, self.CommType))

    def testCloneFree(self):
        if self.COMM_BASE != MPI.COMM_NULL:
            comm = self.comm.Clone()
        else:
            comm = self.CommType()
        self.assertTrue(isinstance(comm, MPI.Comm))
        self.assertTrue(isinstance(comm, self.CommType))
        comm.free()

    def tearDown(self):
        self.comm.free()

# ---

class MyComm(MPI.Comm, MyBaseComm):

    def __new__(cls, comm=None):
        if comm is not None:
            if comm != MPI.COMM_NULL:
                comm = comm.Clone()
        return super(MyComm, cls).__new__(cls, comm)

class BaseTestMyComm(BaseTestBaseComm):
    CommType = MyComm

class TestMyCommNULL(BaseTestMyComm, unittest.TestCase):
    COMM_BASE = MPI.COMM_NULL

class TestMyCommSELF(BaseTestMyComm, unittest.TestCase):
    COMM_BASE = MPI.COMM_SELF

class TestMyCommWORLD(BaseTestMyComm, unittest.TestCase):
    COMM_BASE = MPI.COMM_WORLD

# ---

class MyIntracomm(MPI.Intracomm, MyBaseComm):

    def __new__(cls, comm=None):
        if comm is not None:
            if comm != MPI.COMM_NULL:
                comm = comm.Dup()
        return super(MyIntracomm, cls).__new__(cls, comm)

class BaseTestMyIntracomm(BaseTestBaseComm):
    CommType = MyIntracomm

class TestMyIntracommNULL(BaseTestMyIntracomm, unittest.TestCase):
    COMM_BASE = MPI.COMM_NULL

class TestMyIntracommSELF(BaseTestMyIntracomm, unittest.TestCase):
    COMM_BASE = MPI.COMM_SELF

class TestMyIntracommWORLD(BaseTestMyIntracomm, unittest.TestCase):
    COMM_BASE = MPI.COMM_WORLD

# ---

class MyCartcomm(MPI.Cartcomm, MyBaseComm):

    def __new__(cls, comm=None):
        if comm is not None:
            if comm != MPI.COMM_NULL:
                dims = [comm.size]
                comm = comm.Create_cart(dims)
        return super(MyCartcomm, cls).__new__(cls, comm)

class BaseTestMyCartcomm(BaseTestBaseComm):
    CommType = MyCartcomm

class TestMyCartcommNULL(BaseTestMyCartcomm, unittest.TestCase):
    COMM_BASE = MPI.COMM_NULL

class TestMyCartcommSELF(BaseTestMyCartcomm, unittest.TestCase):
    COMM_BASE = MPI.COMM_SELF

class TestMyCartcommWORLD(BaseTestMyCartcomm, unittest.TestCase):
    COMM_BASE = MPI.COMM_WORLD

# ---

class MyGraphcomm(MPI.Graphcomm, MyBaseComm):

    def __new__(cls, comm=None):
        if comm is not None:
            if comm != MPI.COMM_NULL:
                index = list(range(0, comm.size+1))
                edges = list(range(0, comm.size))
                comm = comm.Create_graph(index, edges)
        return super(MyGraphcomm, cls).__new__(cls, comm)

class BaseTestMyGraphcomm(BaseTestBaseComm):
    CommType = MyGraphcomm

class TestMyGraphcommNULL(BaseTestMyGraphcomm, unittest.TestCase):
    COMM_BASE = MPI.COMM_NULL

class TestMyGraphcommSELF(BaseTestMyGraphcomm, unittest.TestCase):
    COMM_BASE = MPI.COMM_SELF

class TestMyGraphcommWORLD(BaseTestMyGraphcomm, unittest.TestCase):
    COMM_BASE = MPI.COMM_WORLD

# ---

class MyRequest(MPI.Request):
    def __new__(cls, request=None):
        return super(MyRequest, cls).__new__(cls, request)
    def test(self):
        return super(type(self), self).Test()
    def wait(self):
        return super(type(self), self).Wait()

class MyPrequest(MPI.Prequest):
    def __new__(cls, request=None):
        return super(MyPrequest, cls).__new__(cls, request)
    def test(self):
        return super(type(self), self).Test()
    def wait(self):
        return super(type(self), self).Wait()
    def start(self):
        return super(type(self), self).Start()

class MyGrequest(MPI.Grequest):
    def __new__(cls, request=None):
        return super(MyGrequest, cls).__new__(cls, request)
    def test(self):
        return super(type(self), self).Test()
    def wait(self):
        return super(type(self), self).Wait()

class BaseTestMyRequest(object):

    def setUp(self):
        self.req = self.MyRequestType(MPI.REQUEST_NULL)

    def testSubType(self):
        self.assertTrue(type(self.req) is not self.MPIRequestType)
        self.assertTrue(isinstance(self.req, self.MPIRequestType))
        self.assertTrue(isinstance(self.req, self.MyRequestType))
        self.req.test()

class TestMyRequest(BaseTestMyRequest, unittest.TestCase):
    MPIRequestType = MPI.Request
    MyRequestType = MyRequest

class TestMyPrequest(BaseTestMyRequest, unittest.TestCase):
    MPIRequestType = MPI.Prequest
    MyRequestType = MyPrequest

class TestMyGrequest(BaseTestMyRequest, unittest.TestCase):
    MPIRequestType = MPI.Grequest
    MyRequestType = MyGrequest

class TestMyRequest2(TestMyRequest):

    def setUp(self):
        req = MPI.COMM_SELF.Isend(
            [MPI.BOTTOM, 0, MPI.BYTE],
            dest=MPI.PROC_NULL, tag=0)
        self.req = MyRequest(req)

class TestMyPrequest2(TestMyPrequest):

    def setUp(self):
        req = MPI.COMM_SELF.Send_init(
            [MPI.BOTTOM, 0, MPI.BYTE],
            dest=MPI.PROC_NULL, tag=0)
        self.req = MyPrequest(req)

    def tearDown(self):
        self.req.Free()

    def testStart(self):
        for i in range(5):
            self.req.start()
            self.req.test()
            self.req.start()
            self.req.wait()

# ---

class MyWin(MPI.Win):

    def __new__(cls, win=None):
        return MPI.Win.__new__(cls, win)

    def free(self):
        if self != MPI.WIN_NULL:
            MPI.Win.Free(self)

class BaseTestMyWin(object):

    def setUp(self):
        w = MPI.Win.Create(MPI.BOTTOM)
        self.win = MyWin(w)

    def tearDown(self):
        self.win.free()

    def testSubType(self):
        self.assertTrue(type(self.win) is not MPI.Win)
        self.assertTrue(isinstance(self.win, MPI.Win))
        self.assertTrue(isinstance(self.win, MyWin))

    def testFree(self):
        self.assertTrue(self.win)
        self.win.free()
        self.assertFalse(self.win)

class TestMyWin(BaseTestMyWin, unittest.TestCase):
    pass

SpectrumMPI = MPI.get_vendor()[0] == 'Spectrum MPI'
try:
    if SpectrumMPI: raise NotImplementedError
    MPI.Win.Create(MPI.BOTTOM).Free()
except NotImplementedError:
    unittest.disable(BaseTestMyWin, 'mpi-win')

# ---

import os, tempfile

class MyFile(MPI.File):

    def __new__(cls, file=None):
        return MPI.File.__new__(cls, file)

    def close(self):
        if self != MPI.FILE_NULL:
            MPI.File.Close(self)


class BaseTestMyFile(object):

    def openfile(self):
        fd, fname = tempfile.mkstemp(prefix='mpi4py')
        os.close(fd)
        amode = MPI.MODE_RDWR | MPI.MODE_CREATE | MPI.MODE_DELETE_ON_CLOSE
        try:
            self.file = MPI.File.Open(MPI.COMM_SELF, fname, amode, MPI.INFO_NULL)
            return self.file
        except Exception:
            os.remove(fname)
            raise

    def setUp(self):
        f = self.openfile()
        self.file = MyFile(f)

    def tearDown(self):
        self.file.close()

    def testSubType(self):
        self.assertTrue(type(self.file) is not MPI.File)
        self.assertTrue(isinstance(self.file, MPI.File))
        self.assertTrue(isinstance(self.file, MyFile))

    def testFree(self):
        self.assertTrue(self.file)
        self.file.close()
        self.assertFalse(self.file)

class TestMyFile(BaseTestMyFile, unittest.TestCase):
    pass


try:
    BaseTestMyFile().openfile().Close()
except NotImplementedError:
    unittest.disable(BaseTestMyFile, 'mpi-file')


if __name__ == '__main__':
    unittest.main()
