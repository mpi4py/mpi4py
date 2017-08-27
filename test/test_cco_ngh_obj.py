from mpi4py import MPI
import mpiunittest as unittest

_basic = [None,
          True, False,
          -7, 0, 7, 2**31,
          -2**63+1, 2**63-1,
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
messages = messages + [messages]

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

def have_feature():
    cartcomm = MPI.COMM_SELF.Create_cart([1], periods=[0])
    try:
        cartcomm.neighbor_allgather(None)
        return True
    except NotImplementedError:
        return False
    finally:
        cartcomm.Free()


@unittest.skipIf(not have_feature(), 'mpi-neighbor')
class BaseTestCCONghObj(object):

    COMM = MPI.COMM_NULL

    @unittest.skipMPI('openmpi(<2.2.0)')
    def testNeighborAllgather(self):
        for comm in create_topo_comms(self.COMM):
            rsize, ssize = get_neighbors_count(comm)
            for smess in messages:
                rmess = comm.neighbor_allgather(smess)
                self.assertEqual(rmess, [smess] * rsize)
            comm.Free()

    def testNeighborAlltoall(self):
        for comm in create_topo_comms(self.COMM):
            rsize, ssize = get_neighbors_count(comm)
            for smess in messages:
                rmess = comm.neighbor_alltoall([smess] * ssize)
                self.assertEqual(rmess, [smess] * rsize)
            comm.Free()


class TestCCONghObjSelf(BaseTestCCONghObj, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestCCONghObjWorld(BaseTestCCONghObj, unittest.TestCase):
    COMM = MPI.COMM_WORLD

class TestCCONghObjSelfDup(TestCCONghObjSelf):
    def setUp(self):
        self.COMM = MPI.COMM_SELF.Dup()
    def tearDown(self):
        self.COMM.Free()

class TestCCONghObjWorldDup(TestCCONghObjWorld):
    def setUp(self):
        self.COMM = MPI.COMM_WORLD.Dup()
    def tearDown(self):
        self.COMM.Free()


name, version = MPI.get_vendor()
if name == 'Open MPI' and version < (1,8,4):
    _create_topo_comms = create_topo_comms
    def create_topo_comms(comm):
        for c in _create_topo_comms(comm):
            if c.size * 2 < sum(c.degrees):
                c.Free(); continue
            yield c


if __name__ == '__main__':
    unittest.main()
