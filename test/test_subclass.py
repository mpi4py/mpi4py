from mpi4py import MPI
import mpiunittest as unittest

# ---

class MyBaseComm(object):

    def free(self):
        if self != MPI.COMM_NULL:
            super(type(self), self).Free()

class BaseTestBaseComm(object):

    def setUp(self):
        self.comm = self.CommType(self.COMM_BASE)

    def testSubType(self):
        self.assertTrue(isinstance(self.comm, self.CommType))

    def testCloneFree(self):
        if self.COMM_BASE != MPI.COMM_NULL:
            comm = self.comm.Clone()
        else:
            comm = self.CommType()
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

if __name__ == '__main__':
    unittest.main()
