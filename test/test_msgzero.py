from mpi4py import MPI
import mpiunittest as unittest


class BaseTestMessageZero(object):

    null_b = [None, MPI.INT]
    null_v = [None, (0, None), MPI.INT]

    def testPointToPoint(self):
        comm = self.COMM
        comm.Sendrecv(sendbuf=self.null_b,   dest=comm.rank,
                      recvbuf=self.null_b, source=comm.rank)
        r2 = comm.Irecv(self.null_b, comm.rank)
        r1 = comm.Isend(self.null_b, comm.rank)
        MPI.Request.Waitall([r1, r2])

    def testCollectivesBlock(self):
        comm = self.COMM
        comm.Bcast(self.null_b)
        comm.Gather(self.null_b, self.null_b)
        comm.Scatter(self.null_b, self.null_b)
        comm.Allgather(self.null_b, self.null_b)
        comm.Alltoall(self.null_b, self.null_b)

    def testCollectivesVector(self):
        comm = self.COMM
        comm.Gatherv(self.null_b, self.null_v)
        comm.Scatterv(self.null_v, self.null_b)
        comm.Allgatherv(self.null_b, self.null_v)
        comm.Alltoallv(self.null_v, self.null_v)

    @unittest.skipMPI('openmpi')
    @unittest.skipMPI('SpectrumMPI')
    def testReductions(self):
        comm = self.COMM
        comm.Reduce(self.null_b, self.null_b)
        comm.Allreduce(self.null_b, self.null_b)
        comm.Reduce_scatter_block(self.null_b, self.null_b)
        rcnt = [0]*comm.Get_size()
        comm.Reduce_scatter(self.null_b, self.null_b, rcnt)
        try: comm.Scan(self.null_b, self.null_b)
        except NotImplementedError: pass
        try: comm.Exscan(self.null_b, self.null_b)
        except NotImplementedError: pass

class TestMessageZeroSelf(BaseTestMessageZero, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestMessageZeroWorld(BaseTestMessageZero, unittest.TestCase):
    COMM = MPI.COMM_WORLD


if __name__ == '__main__':
    unittest.main()
