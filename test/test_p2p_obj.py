from mpi4py import MPI
import mpiunittest as unittest

_basic = [None,
          True, False,
          -7, 0, 7,
          -2**63, 2**63-1,
          -2.17, 0.0, 3.14,
          1+2j, 2-3j,
          'mpi4py',
          ]
messages = _basic
messages += [ list(_basic),
              tuple(_basic),
              dict([('k%d' % key, val)
                    for key, val in enumerate(_basic)])
              ]




class BaseTestP2PObj(object):

    COMM = MPI.COMM_NULL

    def testSendAndRecv(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for smess in messages:
            self.COMM.send(smess,  MPI.PROC_NULL)
            rmess = self.COMM.recv(None, MPI.PROC_NULL, 0)
            self.assertEqual(rmess, None)
        if size == 1: return
        for smess in messages:
            if rank == 0:
                self.COMM.send(smess,  rank+1, 0)
                rmess = smess
            elif rank == size - 1:
                rmess = self.COMM.recv(None, rank-1, 0)
            else:
                rmess = self.COMM.recv(None, rank-1, 0)
                self.COMM.send(rmess,  rank+1, 0)
            self.assertEqual(rmess, smess)

    def testSendrecv(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for smess in messages:
            dest = (rank + 1) % size
            source = (rank - 1) % size
            rmess = self.COMM.sendrecv(smess, dest,   0,
                                       None,  source, 0)
            continue
            self.assertEqual(rmess, smess)
            rmess = self.COMM.sendrecv(None,  dest,   0,
                                       None,  source, 0)
            self.assertEqual(rmess, None)
            rmess = self.COMM.sendrecv(smess,  MPI.PROC_NULL, 0,
                                       None,   MPI.PROC_NULL, 0)
            self.assertEqual(rmess, None)

    def testPingPong01(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for smess in messages:
            self.COMM.send(smess,  MPI.PROC_NULL)
            rmess = self.COMM.recv(None, MPI.PROC_NULL, 0)
            self.assertEqual(rmess, None)
        if size == 1: return
        smess = None
        if rank == 0:
            self.COMM.send(smess,  rank+1, 0)
            rmess = self.COMM.recv(None, rank+1, 0)
        elif rank == 1:
            rmess = self.COMM.recv(None, rank-1, 0)
            self.COMM.send(smess,  rank-1, 0)
        else:
            rmess = smess
        self.assertEqual(rmess, smess)
        for smess in messages:
            if rank == 0:
                self.COMM.send(smess,  rank+1, 0)
                rmess = self.COMM.recv(None, rank+1, 0)
            elif rank == 1:
                rmess = self.COMM.recv(None, rank-1, 0)
                self.COMM.send(smess,  rank-1, 0)
            else:
                rmess = smess
            self.assertEqual(rmess, smess)

class BaseTestP2PObjDup(BaseTestP2PObj):
    def setUp(self):
        self.COMM = self.COMM.Dup()
    def tearDown(self):
        self.COMM.Free()

class TestP2PObjSelf(BaseTestP2PObj, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestP2PObjWorld(BaseTestP2PObj, unittest.TestCase):
    COMM = MPI.COMM_WORLD

class TestP2PObjSelfDup(BaseTestP2PObjDup, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestP2PObjWorldDup(BaseTestP2PObjDup, unittest.TestCase):
    COMM = MPI.COMM_WORLD


_name, _version = MPI.get_vendor()
if _name == 'Open MPI':
    if _version < (1, 4, 0):
        if MPI.Query_thread() > MPI.THREAD_SINGLE:
            del TestP2PObjWorldDup

if __name__ == '__main__':
    unittest.main()
