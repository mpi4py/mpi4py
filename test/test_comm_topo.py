from mpi4py import MPI
import mpiunittest as unittest

class BaseTestTopo(object):

    COMM = MPI.COMM_NULL

    def testCartcomm(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        for ndim in (1,2,3,4,5):
            dims = [0]*ndim
            dims = MPI.Compute_dims(size, [0]*ndim)
            periods = [True] * len(dims)
            topo = comm.Create_cart(dims, periods=periods)
            dim = topo.dim
            self.assertEqual(dim, len(dims))
            coordinates = topo.coords
            neighbors = []
            for i in range(dim):
                for d in (-1, +1):
                    coord = list(coordinates)
                    coord[i] = (coord[i]+d) % dims[i]
                    neigh = topo.Get_cart_rank(coord)
                    neighbors.append(neigh)
            inedges, outedges = topo.inoutedges
            self.assertEqual(inedges, neighbors)
            self.assertEqual(outedges, neighbors)
            topo.Free()
        if size > 1: return
        if MPI.VERSION < 2: return
        topo = comm.Create_cart([])
        self.assertEqual(topo.dim, 0)
        self.assertEqual(topo.dims, [])
        self.assertEqual(topo.periods, [])
        self.assertEqual(topo.coords, [])
        rank = topo.Get_cart_rank([])
        self.assertEqual(rank, 0)
        inedges, outedges = topo.inoutedges
        self.assertEqual(inedges, [])
        self.assertEqual(outedges, [])
        topo.Free()

    def testGraphcomm(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        index, edges = [0], []
        for i in range(size):
            pos = index[-1]
            index.append(pos+2)
            edges.append((i-1)%size)
            edges.append((i+1)%size)
        topo = comm.Create_graph(index, edges)
        neighbors = edges[index[rank]:index[rank+1]]
        inedges, outedges = topo.inoutedges
        self.assertEqual(inedges, neighbors)
        self.assertEqual(outedges, neighbors)
        topo.Free()

    def testDistgraphcomm(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        sources = [(rank-2)%size, (rank-1)%size]
        destinations = [(rank+1)%size, (rank+2)%size]
        try:
            topo = comm.Create_dist_graph_adjacent(sources, destinations)
        except NotImplementedError:
            return
        inedges, outedges = topo.inoutedges
        self.assertEqual(inedges, sources)
        self.assertEqual(outedges, destinations)
        topo.Free()


class TestTopoSelf(BaseTestTopo, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestTopoWorld(BaseTestTopo, unittest.TestCase):
    COMM = MPI.COMM_WORLD

class TestTopoSelfDup(BaseTestTopo, unittest.TestCase):
    def setUp(self):
        self.COMM = MPI.COMM_SELF.Dup()
    def tearDown(self):
        self.COMM.Free()

class TestTopoWorldDup(BaseTestTopo, unittest.TestCase):
    def setUp(self):
        self.COMM = MPI.COMM_WORLD.Dup()
    def tearDown(self):
        self.COMM.Free()


if __name__ == '__main__':
    unittest.main()
