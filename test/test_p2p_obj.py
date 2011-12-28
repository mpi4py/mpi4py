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
messages = list(_basic)
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

    def testISendAndRecv(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for smess in messages:
            req = self.COMM.isend(smess,  MPI.PROC_NULL)
            self.assertTrue(req)
            req.Wait()
            self.assertFalse(req)
            rmess = self.COMM.recv(None, MPI.PROC_NULL, 0)
            self.assertEqual(rmess, None)
        for smess in messages:
            req = self.COMM.isend(smess,  rank, 0)
            self.assertTrue(req)
            #flag = req.Test()
            #self.assertFalse(flag)
            #self.assertTrue(req)
            rmess = self.COMM.recv(None, rank, 0)
            self.assertTrue(req)
            flag = req.Test()
            self.assertTrue(flag)
            self.assertFalse(req)
            self.assertEqual(rmess, smess)
        for smess in messages:
            dst = (rank+1)%size
            src = (rank-1)%size
            req = self.COMM.isend(smess,  dst, 0)
            self.assertTrue(req)
            rmess = self.COMM.recv(None,  src, 0)
            req.Wait()
            self.assertFalse(req)
            self.assertEqual(rmess, smess)

    def testIRecvAndSend(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        for smess in messages:
            req = comm.irecv(0, MPI.PROC_NULL)
            self.assertTrue(req)
            comm.send(smess,  MPI.PROC_NULL)
            rmess = req.wait()
            self.assertFalse(req)
            self.assertEqual(rmess, None)
        for smess in messages:
            try:
                buf = bytearray(512)
            except NameError:
                from array import array
                buf = array('B', [0]) * 512
            req = comm.irecv(buf,  rank, 0)
            self.assertTrue(req)
            flag, rmess = req.test()
            self.assertTrue(req)
            self.assertFalse(flag)
            self.assertEqual(rmess, None)
            comm.send(smess, rank, 0)
            self.assertTrue(req)
            flag, rmess = req.test()
            self.assertTrue(flag)
            self.assertFalse(req)
            self.assertEqual(rmess, smess)
        try:
            tmp = bytearray(1024)
        except NameError:
            from array import array
            tmp = array('B', [0]) * 1024
        for buf in (None, tmp):
            for smess in messages:
                dst = (rank+1)%size
                src = (rank-1)%size
                req = comm.irecv(buf, src, 0)
                self.assertTrue(req)
                comm.send(smess, dst, 0)
                rmess = req.wait()
                self.assertFalse(req)
                self.assertEqual(rmess, smess)

    def testIRecvAndISend(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        try:
            tmp = bytearray(512)
        except NameError:
            from array import array
            tmp = array('B', [0]) * 512
        for buf in (None, tmp):
            for smess in messages:
                dst = (rank+1)%size
                src = (rank-1)%size
                rreq = comm.irecv(buf, src, 0)
                self.assertTrue(rreq)
                sreq = comm.isend(smess, dst, 0)
                self.assertTrue(sreq)
                dummy, rmess = MPI.Request.waitall([sreq,rreq])
                self.assertFalse(sreq)
                self.assertFalse(rreq)
                self.assertEqual(dummy, None)
                self.assertEqual(rmess, smess)
        for buf in (None, tmp):
            for smess in messages:
                src = dst = rank
                rreq = comm.irecv(buf, src, 1)
                flag, msg = MPI.Request.testall([rreq])
                self.assertEqual(flag, False)
                self.assertEqual(msg, None)
                sreq = comm.isend(smess, dst, 1)
                while True:
                    flag, msg = MPI.Request.testall([sreq,rreq])
                    if not flag:
                        self.assertEqual(msg, None)
                        continue
                    (dummy, rmess) = msg
                    self.assertEqual(dummy, None)
                    self.assertEqual(rmess, smess)
                    break

    def testManyISendAndRecv(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for smess in messages:
            reqs = []
            for k in range(6):
                r = self.COMM.isend(smess,  rank, 0)
                reqs.append(r)
            flag = MPI.Request.Testall(reqs)
            if not flag:
                index, flag = MPI.Request.Testany(reqs)
                count, indices = MPI.Request.Testsome(reqs)
                self.assertTrue(count in  [0, MPI.UNDEFINED])
            for k in range(3):
                rmess = self.COMM.recv(None, rank, 0)
                self.assertEqual(rmess, smess)
            flag = MPI.Request.Testall(reqs)
            if not flag:
                index, flag = MPI.Request.Testany(reqs)
                self.assertEqual(index,  0)
                self.assertTrue(flag)
                count, indices = MPI.Request.Testsome(reqs)
                self.assertTrue(count >= 2)
                indices = list(indices)
                indices.sort()
                self.assertTrue(indices[:2] == [1, 2])
            for k in range(3):
                rmess = self.COMM.recv(None, rank, 0)
                self.assertEqual(rmess, smess)
            flag = MPI.Request.Testall(reqs)
            self.assertTrue(flag)
        for smess in messages:
            reqs = []
            for k in range(6):
                r = self.COMM.isend(smess,  rank, 0)
                reqs.append(r)
            for k in range(3):
                rmess = self.COMM.recv(None, rank, 0)
                self.assertEqual(rmess, smess)
            index = MPI.Request.Waitany(reqs)
            self.assertTrue(index == 0)
            self.assertTrue(flag)
            count1, indices1 = MPI.Request.Waitsome(reqs)
            for k in range(3):
                rmess = self.COMM.recv(None, rank, 0)
                self.assertEqual(rmess, smess)
            count2, indices2 = MPI.Request.Waitsome(reqs)
            if count1 == MPI.UNDEFINED: count1 = 0
            if count2 == MPI.UNDEFINED: count2 = 0
            self.assertEqual(6, 1+count1+count2)
            indices = [0]+list(indices1)+list(indices2)
            indices.sort()
            self.assertEqual(indices, list(range(6)))
            MPI.Request.Waitall(reqs)

    def testSSendAndRecv(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for smess in messages:
            self.COMM.ssend(smess,  MPI.PROC_NULL)
            rmess = self.COMM.recv(None, MPI.PROC_NULL, 0)
            self.assertEqual(rmess, None)
        if size == 1: return
        for smess in messages:
            if rank == 0:
                self.COMM.ssend(smess,  rank+1, 0)
                rmess = smess
            elif rank == size - 1:
                rmess = self.COMM.recv(None, rank-1, 0)
            else:
                rmess = self.COMM.recv(None, rank-1, 0)
                self.COMM.ssend(rmess,  rank+1, 0)
            self.assertEqual(rmess, smess)

    def testISSendAndRecv(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for smess in messages:
            req = self.COMM.issend(smess,  MPI.PROC_NULL)
            self.assertTrue(req)
            req.Wait()
            self.assertFalse(req)
            rmess = self.COMM.recv(None, MPI.PROC_NULL, 0)
            self.assertEqual(rmess, None)
        for smess in messages:
            req = self.COMM.issend(smess,  rank, 0)
            self.assertTrue(req)
            flag = req.Test()
            self.assertFalse(flag)
            self.assertTrue(req)
            rmess = self.COMM.recv(None, rank, 0)
            self.assertTrue(req)
            flag = req.Test()
            self.assertTrue(flag)
            self.assertFalse(req)
            self.assertEqual(rmess, smess)
        for smess in messages:
            dst = (rank+1)%size
            src = (rank-1)%size
            req = self.COMM.issend(smess,  dst, 0)
            self.assertTrue(req)
            rmess = self.COMM.recv(None,  src, 0)
            req.Wait()
            self.assertFalse(req)
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
        del self.COMM

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
