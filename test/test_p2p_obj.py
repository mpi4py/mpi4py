from mpi4py import MPI
import mpiunittest as unittest
import threading
import warnings
import sys

def allocate(n):
    return bytearray(n)

_basic = [
    None,
    True, False,
    -7, 0, 7,
    -2**63+1, 2**63-1,
    -2.17, 0.0, 3.14,
    1+2j, 2-3j,
    'mpi4py',
]
messages = list(_basic)
messages += [
    list(_basic),
    tuple(_basic),
    set(_basic),
    frozenset(_basic),
    dict((f'k{k}', v) for k, v in enumerate(_basic)),
]

class BaseTestP2PObj:

    COMM = MPI.COMM_NULL

    def testSendAndRecv(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for smess in messages:
            self.COMM.send(smess, MPI.PROC_NULL)
            rmess = self.COMM.recv(None, MPI.PROC_NULL, 0)
            self.assertIsNone(rmess)
        if size == 1: return
        for smess in messages:
            if rank == 0:
                self.COMM.send(smess, rank+1, 0)
                rmess = smess
            elif rank == size - 1:
                rmess = self.COMM.recv(None, rank-1, 0)
            else:
                rmess = self.COMM.recv(None, rank-1, 0)
                self.COMM.send(rmess, rank+1, 0)
            self.assertEqual(rmess, smess)

    def testISendAndRecv(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        buf = None
        for smess in messages:
            req = self.COMM.isend(smess, MPI.PROC_NULL)
            self.assertTrue(req)
            req.Wait()
            self.assertFalse(req)
            rmess = self.COMM.recv(buf, MPI.PROC_NULL, 0)
            self.assertIsNone(rmess)
        for smess in messages:
            req = self.COMM.isend(smess, rank, 0)
            self.assertTrue(req)
            rmess = self.COMM.recv(buf, rank, 0)
            self.assertTrue(req)
            flag = False
            while not flag:
                flag = req.Test()
            self.assertTrue(flag)
            self.assertFalse(req)
            self.assertEqual(rmess, smess)
        for smess in messages:
            dst = (rank+1)%size
            src = (rank-1)%size
            req = self.COMM.isend(smess, dst, 0)
            self.assertTrue(req)
            rmess = self.COMM.recv(buf, src, 0)
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
            comm.send(smess, MPI.PROC_NULL)
            rmess = req.wait()
            self.assertFalse(req)
            self.assertIsNone(rmess)
        for smess in messages:
            buf = allocate(512)
            req = comm.irecv(buf, rank, 0)
            self.assertTrue(req)
            flag, rmess = req.test()
            self.assertTrue(req)
            self.assertFalse(flag)
            self.assertIsNone(rmess)
            comm.send(smess, rank, 0)
            self.assertTrue(req)
            flag, rmess = req.test()
            while not flag: flag, rmess = req.test()
            self.assertTrue(flag)
            self.assertFalse(req)
            self.assertEqual(rmess, smess)
        tmp = allocate(1024)
        for buf in (None, 1024, tmp):
            for smess in messages + [messages]:
                dst = (rank+1)%size
                src = (rank-1)%size
                req = comm.irecv(buf, src, 0)
                self.assertTrue(req)
                comm.send(smess, dst, 0)
                rmess = req.wait()
                self.assertFalse(req)
                self.assertEqual(rmess, smess)
        for smess in messages:
            src = dst = rank
            rreq1 = comm.irecv(None, src, 1)
            rreq2 = comm.irecv(None, src, 2)
            rreq3 = comm.irecv(None, src, 3)
            rreqs = [rreq1, rreq2, rreq3]
            for i in range(len(rreqs)):
                self.assertTrue(rreqs[i])
                comm.send(smess, dst, i+1)
                index, obj = MPI.Request.waitany(rreqs)
                self.assertEqual(index, i)
                self.assertEqual(obj, smess)
                self.assertFalse(rreqs[index])
            index, obj = MPI.Request.waitany(rreqs)
            self.assertEqual(index, MPI.UNDEFINED)
            self.assertIsNone(obj)
        for smess in messages:
            src = dst = rank
            rreq1 = comm.irecv(None, src, 1)
            rreq2 = comm.irecv(None, src, 2)
            rreq3 = comm.irecv(None, src, 3)
            rreqs = [rreq1, rreq2, rreq3]
            index, flag, obj = MPI.Request.testany(rreqs)
            self.assertEqual(index, MPI.UNDEFINED)
            self.assertFalse(flag)
            self.assertIsNone(obj)
            for i in range(len(rreqs)):
                self.assertTrue(rreqs[i])
                comm.send(smess, dst, i+1)
                index, flag, obj = MPI.Request.testany(rreqs)
                while not flag:
                    index, flag, obj = MPI.Request.testany(rreqs)
                self.assertEqual(index, i)
                self.assertTrue(flag)
                self.assertEqual(obj, smess)
                self.assertFalse(rreqs[i])
            index, flag, obj = MPI.Request.testany(rreqs)
            self.assertEqual(index, MPI.UNDEFINED)
            self.assertTrue(flag)
            self.assertIsNone(obj)

    def testIRecvAndISend(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        tmp = allocate(512)
        for smess in messages:
            dst = (rank+1)%size
            src = (rank-1)%size
            rreq = comm.irecv(None, src, 0)
            self.assertTrue(rreq)
            sreq = comm.isend(smess, dst, 0)
            self.assertTrue(sreq)
            index1, mess1 = MPI.Request.waitany([sreq,rreq])
            self.assertIn(index1, (0, 1))
            if index1 == 0:
                self.assertFalse(sreq)
                self.assertTrue (rreq)
                self.assertIsNone(mess1)
            else:
                self.assertTrue (sreq)
                self.assertFalse(rreq)
                self.assertEqual(mess1, smess)
            index2, mess2 = MPI.Request.waitany([sreq,rreq])
            self.assertIn(index2, (0, 1))
            self.assertNotEqual(index2, index1)
            self.assertFalse(sreq)
            self.assertFalse(rreq)
            if index2 == 0:
                self.assertIsNone(mess2)
            else:
                self.assertEqual(mess2, smess)
        for smess in messages:
            dst = (rank+1)%size
            src = (rank-1)%size
            rreq = comm.irecv(None, src, 0)
            self.assertTrue(rreq)
            sreq = comm.isend(smess, dst, 0)
            self.assertTrue(sreq)
            index1, flag1, mess1 = MPI.Request.testany([sreq,rreq])
            while not flag1:
                index1, flag1, mess1 = MPI.Request.testany([sreq,rreq])
            self.assertIn(index1, (0, 1))
            if index1 == 0:
                self.assertFalse(sreq)
                self.assertTrue (rreq)
                self.assertIsNone(mess1)
            else:
                self.assertTrue (sreq)
                self.assertFalse(rreq)
                self.assertEqual(mess1, smess)
            index2, flag2, mess2 = MPI.Request.testany([sreq,rreq])
            while not flag2:
                index2, flag2, mess2 = MPI.Request.testany([sreq,rreq])
            self.assertIn(index2, (0, 1))
            self.assertNotEqual(index2, index1)
            self.assertFalse(sreq)
            self.assertFalse(rreq)
            if index2 == 0:
                self.assertIsNone(mess2)
            else:
                self.assertEqual(mess2, smess)
        for buf in (None, 512, tmp):
            for smess in messages:
                dst = (rank+1)%size
                src = (rank-1)%size
                rreq = comm.irecv(buf, src, 0)
                self.assertTrue(rreq)
                sreq = comm.isend(smess, dst, 0)
                self.assertTrue(sreq)
                dummy, rmess = MPI.Request.waitall([sreq,rreq], [])
                self.assertFalse(sreq)
                self.assertFalse(rreq)
                self.assertIsNone(dummy)
                self.assertEqual(rmess, smess)
        for buf in (None, 512, tmp):
            for smess in messages:
                src = dst = rank
                rreq = comm.irecv(buf, src, 1)
                flag, msg = MPI.Request.testall([rreq])
                self.assertFalse(flag)
                self.assertIsNone(msg)
                sreq = comm.isend(smess, dst, 1)
                while True:
                    flag, msg = MPI.Request.testall([sreq,rreq], [])
                    if not flag:
                        self.assertIsNone(msg)
                        continue
                    (dummy, rmess) = msg
                    self.assertIsNone(dummy)
                    self.assertEqual(rmess, smess)
                    break

    def testManyISendAndRecv(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for smess in messages:
            reqs = []
            for k in range(6):
                r = self.COMM.isend(smess, rank, 0)
                reqs.append(r)
            flag = MPI.Request.Testall(reqs)
            if not flag:
                index, flag = MPI.Request.Testany(reqs)
                if not flag:
                    self.assertEqual(index, MPI.UNDEFINED)
                indices = MPI.Request.Testsome(reqs)
                self.assertIsInstance(indices, list)
            for k in range(3):
                rmess = self.COMM.recv(None, rank, 0)
                self.assertEqual(rmess, smess)
            flag = MPI.Request.Testall(reqs)
            if not flag:
                index, flag = MPI.Request.Testany(reqs)
                self.assertEqual(index, 0)
                self.assertTrue(flag)
                indices = MPI.Request.Testsome(reqs)
                if indices is None:
                    count = MPI.UNDEFINED
                    indices = []
                else:
                    count = len(indices)
                    indices = sorted(indices)
                self.assertGreaterEqual(count, 2)
                self.assertEqual(indices[:2], [1, 2])
            for k in range(3):
                rmess = self.COMM.recv(None, rank, 0)
                self.assertEqual(rmess, smess)
            flag = MPI.Request.Testall(reqs)
            self.assertTrue(flag)
        for smess in messages:
            reqs = []
            for k in range(6):
                r = self.COMM.isend(smess, rank, 0)
                reqs.append(r)
            for k in range(3):
                rmess = self.COMM.recv(None, rank, 0)
                self.assertEqual(rmess, smess)
            index = MPI.Request.Waitany(reqs)
            self.assertEqual(index, 0)
            indices1 = MPI.Request.Waitsome(reqs)
            if indices1 is None:
                count1 = MPI.UNDEFINED
                indices1 = []
            else:
                count1 = len(indices1)
            for k in range(3):
                rmess = self.COMM.recv(None, rank, 0)
                self.assertEqual(rmess, smess)
            indices2 = MPI.Request.Waitsome(reqs)
            if indices2 is None:
                count2 = MPI.UNDEFINED
                indices2 = []
            else:
                count2 = len(indices2)
            if count1 == MPI.UNDEFINED: count1 = 0
            if count2 == MPI.UNDEFINED: count2 = 0
            self.assertEqual(6, 1+count1+count2)
            indices = [0]+list(indices1)+list(indices2)
            indices.sort()
            self.assertEqual(indices, list(range(6)))
            MPI.Request.Waitall(reqs)

    def testManyISSendAndRecv(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for smess in messages:
            reqs = []
            for k in range(6):
                r = self.COMM.issend(smess, rank, 0)
                reqs.append(r)
            flag = MPI.Request.Testall(reqs)
            self.assertFalse(flag)
            for k in range(3):
                rmess = self.COMM.recv(None, rank, 0)
                self.assertEqual(rmess, smess)
            flag = MPI.Request.Testall(reqs)
            self.assertFalse(flag)
            index, flag = MPI.Request.Testany(reqs)
            if flag:
                self.assertEqual(index, 0)
            indices = MPI.Request.Testsome(reqs)
            if indices is not None:
                target = [0, 1, 2]
                if flag:
                    del target[0]
                for index in indices:
                    self.assertIn(index, target)
            for k in range(3):
                flag = MPI.Request.Testall(reqs)
                self.assertFalse(flag)
                rmess = self.COMM.recv(None, rank, 0)
                self.assertEqual(rmess, smess)
            flag = False
            for k in range(10):
                flag |= MPI.Request.Testall(reqs)
                if flag: break
            if unittest.is_mpi('intelmpi') and sys.platform == 'win32':
                flag |= MPI.Request.Waitall(reqs)
            self.assertTrue(flag)

    def testSSendAndRecv(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for smess in messages:
            self.COMM.ssend(smess, MPI.PROC_NULL)
            rmess = self.COMM.recv(None, MPI.PROC_NULL, 0)
            self.assertIsNone(rmess)
        if size == 1: return
        for smess in messages:
            if rank == 0:
                self.COMM.ssend(smess, rank+1, 0)
                rmess = smess
            elif rank == size - 1:
                rmess = self.COMM.recv(None, rank-1, 0)
            else:
                rmess = self.COMM.recv(None, rank-1, 0)
                self.COMM.ssend(rmess, rank+1, 0)
            self.assertEqual(rmess, smess)

    def testISSendAndRecv(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for smess in messages:
            req = self.COMM.issend(smess, MPI.PROC_NULL)
            self.assertTrue(req)
            req.Wait()
            self.assertFalse(req)
            rmess = self.COMM.recv(None, MPI.PROC_NULL, 0)
            self.assertIsNone(rmess)
        for smess in messages:
            req = self.COMM.issend(smess, rank, 0)
            self.assertTrue(req)
            flag = req.Test()
            self.assertFalse(flag)
            self.assertTrue(req)
            rmess = self.COMM.recv(None, rank, 0)
            self.assertTrue(req)
            flag = False
            while not flag:
                flag = req.Test()
            self.assertTrue(flag)
            self.assertFalse(req)
            self.assertEqual(rmess, smess)
        for smess in messages:
            dst = (rank+1)%size
            src = (rank-1)%size
            req = self.COMM.issend(smess, dst, 0)
            self.assertTrue(req)
            rmess = self.COMM.recv(None, src, 0)
            req.Wait()
            self.assertFalse(req)
            self.assertEqual(rmess, smess)

    def testCancel(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        status = MPI.Status()
        for smess in messages:
            req = self.COMM.issend(smess, rank)
            self.assertTrue(req)
            req.cancel()
            flag = req.get_status(status)
            cancelled = status.Is_cancelled()
            self.assertTrue(req)
            if cancelled:
                self.assertTrue(flag)
                req.Free()
                self.assertFalse(req)
            else:
                self.assertFalse(flag)
                rmess = self.COMM.recv(None, rank, 0)
                flag = req.get_status()
                while not flag: flag = req.get_status()
                self.assertTrue(flag)
                self.assertTrue(req)
                flag, _ = req.test()
                self.assertTrue(flag)
                self.assertFalse(req)
                self.assertEqual(rmess, smess)

    def testIRecvAndBSend(self):
        comm = self.COMM
        rank = comm.Get_rank()
        buf = MPI.Alloc_mem((1<<16)+MPI.BSEND_OVERHEAD)
        MPI.Attach_buffer(buf)
        try:
            for smess in messages:
                src = dst = rank
                req1 = comm.irecv(None, src, 1)
                req2 = comm.irecv(None, src, 2)
                req3 = comm.irecv(None, src, 3)
                comm.bsend(smess, dst, 3)
                comm.bsend(smess, dst, 2)
                comm.bsend(smess, dst, 1)
                self.assertEqual(smess, req3.wait())
                self.assertEqual(smess, req2.wait())
                self.assertEqual(smess, req1.wait())
                comm.bsend(smess, MPI.PROC_NULL, 3)
        finally:
            MPI.Detach_buffer()
            MPI.Free_mem(buf)

    def testIRecvAndIBSend(self):
        comm = self.COMM
        rank = comm.Get_rank()
        buf = MPI.Alloc_mem((1<<16)+MPI.BSEND_OVERHEAD)
        MPI.Attach_buffer(buf)
        try:
            for smess in messages:
                src = dst = rank
                req1 = comm.irecv(None, src, 1)
                req2 = comm.irecv(None, src, 2)
                req3 = comm.irecv(None, src, 3)
                req4 = comm.ibsend(smess, dst, 3)
                req5 = comm.ibsend(smess, dst, 2)
                req6 = comm.ibsend(smess, dst, 1)
                MPI.Request.waitall([req4, req5, req6])
                self.assertEqual(smess, req3.wait())
                self.assertEqual(smess, req2.wait())
                self.assertEqual(smess, req1.wait())
                comm.ibsend(smess, MPI.PROC_NULL, 3).wait()
        finally:
            MPI.Detach_buffer()
            MPI.Free_mem(buf)

    def testIRecvAndSSend(self):
        comm = self.COMM
        rank = comm.Get_rank()
        for smess in messages:
            src = dst = rank
            req1 = comm.irecv(None, src, 1)
            req2 = comm.irecv(None, src, 2)
            req3 = comm.irecv(None, src, 3)
            comm.ssend(smess, dst, 3)
            comm.ssend(smess, dst, 2)
            comm.ssend(smess, dst, 1)
            self.assertEqual(smess, req3.wait())
            self.assertEqual(smess, req2.wait())
            self.assertEqual(smess, req1.wait())
            comm.ssend(smess, MPI.PROC_NULL, 3)

    def testIRecvAndISSend(self):
        comm = self.COMM
        rank = comm.Get_rank()
        for smess in messages:
            src = dst = rank
            req1 = comm.irecv(None, src, 1)
            req2 = comm.irecv(None, src, 2)
            req3 = comm.irecv(None, src, 3)
            req4 = comm.issend(smess, dst, 3)
            req5 = comm.issend(smess, dst, 2)
            req6 = comm.issend(smess, dst, 1)
            MPI.Request.waitall([req4, req5, req6])
            self.assertEqual(smess, req3.wait())
            self.assertEqual(smess, req2.wait())
            self.assertEqual(smess, req1.wait())
            comm.issend(smess, MPI.PROC_NULL, 3).wait()

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
            rmess = self.COMM.sendrecv(None, dest,   0,
                                       None, source, 0)
            self.assertIsNone(rmess)
            rmess = self.COMM.sendrecv(smess, MPI.PROC_NULL, 0,
                                       None,  MPI.PROC_NULL, 0)
            self.assertIsNone(rmess)

    def testMixed(self):
        comm = self.COMM
        rank = comm.Get_rank()
        #
        sreq = comm.Isend([None, 0, 'B'], rank)
        obj = comm.recv(None, rank)
        sreq.Wait()
        self.assertIsNone(obj)
        for smess in messages:
            buf = MPI.pickle.dumps(smess)
            sreq = comm.Isend([buf, 'B'], rank)
            rmess = comm.recv(None, rank)
            sreq.Wait()
            self.assertEqual(rmess, smess)
        #
        sreq = comm.Isend([None, 0, 'B'], rank)
        rreq = comm.irecv(None, rank)
        sreq.Wait()
        obj = rreq.wait()
        self.assertIsNone(obj)
        for smess in messages:
            buf = MPI.pickle.dumps(smess)
            sreq = comm.Isend([buf, 'B'], rank)
            rreq = comm.irecv(None, rank)
            sreq.Wait()
            rmess = rreq.wait()
            self.assertEqual(rmess, smess)

    def testPingPong01(self):
        size = self.COMM.Get_size()
        rank = self.COMM.Get_rank()
        for smess in messages:
            self.COMM.send(smess, MPI.PROC_NULL)
            rmess = self.COMM.recv(None, MPI.PROC_NULL, 0)
            self.assertIsNone(rmess)
        if size == 1: return
        smess = None
        if rank == 0:
            self.COMM.send(smess, rank+1, 0)
            rmess = self.COMM.recv(None, rank+1, 0)
        elif rank == 1:
            rmess = self.COMM.recv(None, rank-1, 0)
            self.COMM.send(smess, rank-1, 0)
        else:
            rmess = smess
        self.assertEqual(rmess, smess)
        for smess in messages:
            if rank == 0:
                self.COMM.send(smess, rank+1, 0)
                rmess = self.COMM.recv(None, rank+1, 0)
            elif rank == 1:
                rmess = self.COMM.recv(None, rank-1, 0)
                self.COMM.send(smess, rank-1, 0)
            else:
                rmess = smess
            self.assertEqual(rmess, smess)

    @unittest.skipMPI('MPICH1')
    def testProbe(self):
        comm = self.COMM.Dup()
        try:
            status = MPI.Status()
            flag = comm.iprobe(MPI.ANY_SOURCE, MPI.ANY_TAG, status)
            self.assertFalse(flag)
            for smess in messages:
                request = comm.issend(smess, comm.rank, 123)
                self.assertTrue(request)
                while not comm.iprobe(MPI.ANY_SOURCE, MPI.ANY_TAG, status): pass
                self.assertEqual(status.source, comm.rank)
                self.assertEqual(status.tag, 123)
                comm.probe(MPI.ANY_SOURCE, MPI.ANY_TAG, status)
                self.assertEqual(status.source, comm.rank)
                self.assertEqual(status.tag, 123)
                self.assertTrue(request)
                flag, obj = request.test()
                self.assertTrue(request)
                self.assertFalse(flag)
                self.assertIsNone(obj)
                obj = comm.recv(None, comm.rank, 123)
                self.assertEqual(obj, smess)
                self.assertTrue(request)
                obj = request.wait()
                self.assertFalse(request)
                self.assertIsNone(obj)
        finally:
            comm.Free()

    def testWaitSomeRecv(self):
        comm = self.COMM.Dup()
        rank = comm.Get_rank()
        reqs = [comm.irecv(source=rank, tag=i) for i in range(6)]
        for indexlist in ([5], [3,1,2], [0,4]):
            for i in indexlist:
                comm.ssend("abc", dest=rank, tag=i)
            statuses = []
            idxs, objs = MPI.Request.waitsome(reqs, statuses)
            self.assertEqual(sorted(idxs), sorted(indexlist))
            self.assertEqual(objs, ["abc"]*len(idxs))
            self.assertFalse(any(reqs[i] for i in idxs))
            self.assertEqual(len(statuses), len(idxs))
            self.assertTrue(all(s.source == rank for s in statuses))
            self.assertTrue(all(s.tag in indexlist for s in statuses))
            self.assertTrue(all(s.error == MPI.SUCCESS for s in statuses))
        idxs, objs = MPI.Request.waitsome(reqs)
        self.assertIsNone(idxs)
        self.assertIsNone(objs)
        self.assertFalse(any(reqs))
        comm.Free()

    def testTestSomeRecv(self):
        comm = self.COMM.Dup()
        rank = comm.Get_rank()
        reqs = [comm.irecv(source=rank, tag=i) for i in range(6)]
        statuses = []
        idxs, objs = MPI.Request.testsome(reqs, statuses)
        self.assertEqual(idxs, [])
        self.assertEqual(objs, [])
        self.assertTrue(all(reqs))
        self.assertEqual(statuses, [])
        for indexlist in ([5], [], [3,1,2], [], [0,4]):
            for i in indexlist:
                comm.ssend("abc", dest=rank, tag=i)
            statuses = []
            idxs, objs = MPI.Request.testsome(reqs, statuses)
            self.assertEqual(sorted(idxs), sorted(indexlist))
            self.assertEqual(objs, ["abc"]*len(idxs))
            self.assertFalse(any(reqs[i] for i in idxs))
            self.assertEqual(len(statuses), len(idxs))
            self.assertTrue(all(s.source == rank for s in statuses))
            self.assertTrue(all(s.tag in indexlist for s in statuses))
            self.assertTrue(all(s.error == MPI.SUCCESS for s in statuses))
        idxs, objs = MPI.Request.testsome(reqs)
        self.assertIsNone(idxs)
        self.assertIsNone(objs)
        self.assertFalse(any(reqs))
        comm.Free()

    def testWaitSomeSend(self):
        comm = self.COMM.Dup()
        rank = comm.Get_rank()
        reqs = [comm.issend("abc", dest=rank, tag=i) for i in range(6)]
        for indexlist in ([5], [3,1,2], [0,4]):
            for i in indexlist:
                msg = comm.recv(source=rank, tag=i)
                self.assertEqual(msg, "abc")
            idxs, objs = MPI.Request.waitsome(reqs)
            while sorted(idxs) != sorted(indexlist):
                i, o = MPI.Request.waitsome(reqs)
                idxs.extend(i)
                objs.extend(o)
            self.assertEqual(sorted(idxs), sorted(indexlist))
            self.assertEqual(objs, [None]*len(idxs))
            self.assertFalse(any(reqs[i] for i in idxs))
        idxs, objs = MPI.Request.waitsome(reqs)
        self.assertIsNone(idxs)
        self.assertIsNone(objs)
        self.assertFalse(any(reqs))
        comm.Free()

    def testTestSomeSend(self):
        comm = self.COMM.Dup()
        rank = comm.Get_rank()
        reqs = [comm.issend("abc", dest=rank, tag=i) for i in range(6)]
        idxs, objs = MPI.Request.testsome(reqs)
        self.assertEqual(idxs, [])
        self.assertEqual(objs, [])
        self.assertTrue(all(reqs))
        for indexlist in ([5], [], [3,1,2], [], [0,4]):
            for i in indexlist:
                msg = comm.recv(source=rank, tag=i)
                self.assertEqual(msg, "abc")
            idxs, objs = MPI.Request.testsome(reqs)
            while sorted(idxs) != sorted(indexlist):
                i, o = MPI.Request.testsome(reqs)
                idxs.extend(i)
                objs.extend(o)
            self.assertEqual(sorted(idxs), sorted(indexlist))
            self.assertEqual(objs, [None]*len(idxs))
            self.assertFalse(any(reqs[i] for i in idxs))
        idxs, objs = MPI.Request.testsome(reqs)
        self.assertIsNone(idxs)
        self.assertIsNone(objs)
        self.assertFalse(any(reqs))
        comm.Free()

    def testRecvObjArg(self):
        comm = self.COMM
        rank = comm.Get_rank()
        req1 = comm.isend("42", rank)
        req2 = comm.isend([42], rank)
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            with self.assertRaises(UserWarning):
                comm.recv(bytearray(0), MPI.PROC_NULL)
            warnings.simplefilter("ignore")
            obj = comm.recv(128, rank)
            self.assertEqual(obj, "42")
            req1.wait()
            obj = comm.recv(bytearray(128), rank)
            self.assertEqual(obj, [42])
            req2.wait()

    def testCommLock(self):
        comm = self.COMM.Dup()
        table = MPI._comm_lock_table(comm)
        self.assertIsInstance(table, dict)
        self.assertNotIn('bcast', table)
        comm.bcast(None, root=0)
        self.assertIn('bcast', table)
        lock = table['bcast']
        lock_type = type(threading.Lock())
        self.assertIsInstance(lock, lock_type)
        comm.Free()


class TestP2PObjSelf(BaseTestP2PObj, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestP2PObjWorld(BaseTestP2PObj, unittest.TestCase):
    COMM = MPI.COMM_WORLD

class TestP2PObjSelfDup(TestP2PObjSelf):
    def setUp(self):
        self.COMM = MPI.COMM_SELF.Dup()
    def tearDown(self):
        self.COMM.Free()

@unittest.skipMPI('openmpi(<1.4.0)', MPI.Query_thread() > MPI.THREAD_SINGLE)
class TestP2PObjWorldDup(TestP2PObjWorld):
    def setUp(self):
        self.COMM = MPI.COMM_WORLD.Dup()
    def tearDown(self):
        self.COMM.Free()



if __name__ == '__main__':
    unittest.main()
