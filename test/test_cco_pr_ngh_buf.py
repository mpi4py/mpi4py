from mpi4py import MPI
import mpiunittest as unittest
import arrayimpl

def create_topo_comms(comm):
    size = comm.Get_size()
    rank = comm.Get_rank()
    # Cartesian
    n = int(size**1/2.0)
    m = int(size**1/3.0)
    if m*m*m == size:
        dims = [m, m, m]
    elif n*n == size:
        dims = [n, n]
    else:
        dims = [size]
    periods = [True] * len(dims)
    yield comm.Create_cart(dims, periods=periods)
    # Graph
    index, edges = [0], []
    for i in range(size):
        pos = index[-1]
        index.append(pos+2)
        edges.append((i-1)%size)
        edges.append((i+1)%size)
    yield comm.Create_graph(index, edges)
    # Dist Graph
    sources = [(rank-2)%size, (rank-1)%size]
    destinations = [(rank+1)%size, (rank+2)%size]
    yield comm.Create_dist_graph_adjacent(sources, destinations)

def get_neighbors_count(comm):
    topo = comm.Get_topology()
    if topo == MPI.CART:
        ndim = comm.Get_dim()
        return 2*ndim, 2*ndim
    if topo == MPI.GRAPH:
        rank = comm.Get_rank()
        nneighbors = comm.Get_neighbors_count(rank)
        return nneighbors, nneighbors
    if topo == MPI.DIST_GRAPH:
        indeg, outdeg, w = comm.Get_dist_neighbors_count()
        return indeg, outdeg
    return 0, 0

def StartWaitFree(request):
    request.Start()
    request.Wait()
    request.Free()


class BaseTestCCONghBuf(object):

    COMM = MPI.COMM_NULL

    def testNeighborAllgather(self):
        for comm in create_topo_comms(self.COMM):
            rsize, ssize = get_neighbors_count(comm)
            for array, typecode in arrayimpl.subTest(self):
                for v in range(3):
                    sbuf = array( v, typecode, 3)
                    rbuf = array(-1, typecode, (rsize, 3))
                    StartWaitFree(
                    comm.Neighbor_allgather_init(sbuf.as_mpi(), rbuf.as_mpi())
                    )
                    for value in rbuf.flat:
                        self.assertEqual(value, v)
                    sbuf = array( v, typecode, 3)
                    rbuf = array(-1, typecode, (rsize, 3))
                    StartWaitFree(
                    comm.Neighbor_allgatherv_init(sbuf.as_mpi_c(3), rbuf.as_mpi_c(3))
                    )
                    for value in rbuf.flat:
                        self.assertEqual(value, v)
            comm.Free()

    def testNeighborAlltoall(self):
        for comm in create_topo_comms(self.COMM):
            rsize, ssize = get_neighbors_count(comm)
            for array, typecode in arrayimpl.subTest(self):
                for v in range(3):
                    sbuf = array( v, typecode, (ssize, 3))
                    rbuf = array(-1, typecode, (rsize, 3))
                    StartWaitFree(
                    comm.Neighbor_alltoall_init(sbuf.as_mpi(), rbuf.as_mpi_c(3))
                    )
                    for value in rbuf.flat:
                        self.assertEqual(value, v)
                    sbuf = array( v, typecode, (ssize, 3))
                    rbuf = array(-1, typecode, (rsize, 3))
                    StartWaitFree(
                    comm.Neighbor_alltoall_init(sbuf.as_mpi(), rbuf.as_mpi())
                    )
                    for value in rbuf.flat:
                        self.assertEqual(value, v)
                    sbuf = array( v, typecode, (ssize, 3))
                    rbuf = array(-1, typecode, (rsize, 3))
                    StartWaitFree(
                    comm.Neighbor_alltoallv_init(sbuf.as_mpi_c(3), rbuf.as_mpi_c(3))
                    )
                    for value in rbuf.flat:
                        self.assertEqual(value, v)
            comm.Free()

    def testNeighborAlltoallw(self):
        size = self.COMM.Get_size()
        for comm in create_topo_comms(self.COMM):
            rsize, ssize = get_neighbors_count(comm)
            for array, typecode in arrayimpl.subTest(self):
                for n in range(1,4):
                    for v in range(3):
                        sbuf = array( v, typecode, (ssize, n))
                        rbuf = array(-1, typecode, (rsize, n))
                        sdt, rdt = sbuf.mpidtype, rbuf.mpidtype
                        sdsp = list(range(0, ssize*n*sdt.extent, n*sdt.extent))
                        rdsp = list(range(0, rsize*n*rdt.extent, n*rdt.extent))
                        smsg = [sbuf.as_raw(), ([n]*ssize, sdsp), [sdt]*ssize]
                        rmsg = (rbuf.as_raw(), ([n]*rsize, rdsp), [rdt]*rsize)
                        StartWaitFree(
                        comm.Neighbor_alltoallw_init(smsg, rmsg)
                        )
                        for value in rbuf.flat:
                            self.assertEqual(value, v)
            comm.Free()


class TestCCONghBufSelf(BaseTestCCONghBuf, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestCCONghBufWorld(BaseTestCCONghBuf, unittest.TestCase):
    COMM = MPI.COMM_WORLD

class TestCCONghBufSelfDup(TestCCONghBufSelf):
    def setUp(self):
        self.COMM = MPI.COMM_SELF.Dup()
    def tearDown(self):
        self.COMM.Free()

class TestCCONghBufWorldDup(TestCCONghBufWorld):
    def setUp(self):
        self.COMM = MPI.COMM_WORLD.Dup()
    def tearDown(self):
        self.COMM.Free()


try:
    StartWaitFree( MPI.COMM_SELF.Barrier_init() )
except NotImplementedError:
    unittest.disable(BaseTestCCONghBuf, 'mpi-coll-persist')


if __name__ == '__main__':
    unittest.main()
