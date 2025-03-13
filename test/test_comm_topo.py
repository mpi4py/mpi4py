from mpi4py import MPI
import mpiunittest as unittest

class TestTopoConstructor(unittest.TestCase):

    def testConstructorTopocomm(self):
        comm = MPI.COMM_SELF
        with self.assertRaises(TypeError):
            MPI.Topocomm(comm)

    def testConstructorCartcomm(self):
        comm = MPI.COMM_SELF
        cart = comm.Create_cart([1])
        with self.assertRaises(TypeError):
            MPI.Graphcomm(cart)
        with self.assertRaises(TypeError):
            MPI.Distgraphcomm(cart)
        cart.Free()

    def testConstructorGraphcomm(self):
        comm = MPI.COMM_SELF
        graph = comm.Create_graph([0, 1], [0])
        with self.assertRaises(TypeError):
            MPI.Cartcomm(graph)
        with self.assertRaises(TypeError):
            MPI.Distgraphcomm(graph)
        graph.Free()

    def testConstructorDistGraphcomm(self):
        comm = MPI.COMM_SELF
        try:
            distgraph = comm.Create_dist_graph([], [], [])
        except NotImplementedError:
            self.skipTest('mpi-comm-create_dist_graph')
        with self.assertRaises(TypeError):
            MPI.Cartcomm(distgraph)
        with self.assertRaises(TypeError):
            MPI.Graphcomm(distgraph)
        distgraph.Free()
        with self.assertRaises(ValueError):
            comm.Create_dist_graph_adjacent(
                [0], [0],
                MPI.WEIGHTS_EMPTY,
                MPI.WEIGHTS_EMPTY,
            )


class BaseTestTopo:

    COMM = MPI.COMM_NULL

    def checkHandle(self, oldcomm):
        cint = oldcomm.toint()
        if cint != -1:
            newcomm = MPI.Comm.fromint(cint)
            self.assertEqual(newcomm, oldcomm)
            self.assertEqual(type(newcomm), type(oldcomm))
        fint = oldcomm.py2f()
        if fint != -1:
            newcomm = MPI.Comm.f2py(fint)
            self.assertEqual(newcomm, oldcomm)
            self.assertEqual(type(newcomm), type(oldcomm))

    def testCartcomm(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        for ndim in (1, 2, 3, 4, 5):
            dims = MPI.Compute_dims(size, [0]*ndim)
            periods = [True] * len(dims)
            topo = comm.Create_cart(dims, periods=periods)
            self.assertTrue(topo.is_topo)
            self.assertEqual(topo.topology, MPI.CART)
            self.checkHandle(topo)
            self.assertEqual(topo.dim, len(dims))
            self.assertEqual(topo.ndim, len(dims))
            coords = topo.coords
            self.assertEqual(coords, topo.Get_coords(topo.rank))
            self.assertEqual(topo.topo,  (dims, periods, coords))
            neighbors = []
            coordinates = topo.Get_coords(topo.rank)
            for i in range(ndim):
                for d in (-1, +1):
                    coord = list(coordinates)
                    coord[i] = (coord[i]+d) % dims[i]
                    neigh = topo.Get_cart_rank(coord)
                    self.assertEqual(coord, topo.Get_coords(neigh))
                    source, dest = topo.Shift(i, d)
                    self.assertEqual(neigh, dest)
                    neighbors.append(neigh)
            self.assertEqual(topo.indegree, len(neighbors))
            self.assertEqual(topo.outdegree, len(neighbors))
            self.assertEqual(topo.inedges, neighbors)
            self.assertEqual(topo.outedges, neighbors)
            inedges, outedges = topo.inoutedges
            self.assertEqual(inedges, neighbors)
            self.assertEqual(outedges, neighbors)
            if ndim == 1:
                topo.Free()
                continue
            for i in range(ndim):
                rem_dims = [1]*ndim
                rem_dims[i] = 0
                sub = topo.Sub(rem_dims)
                if sub != MPI.COMM_NULL:
                    self.assertEqual(sub.dim, ndim-1)
                    dims = topo.dims
                    del dims[i]
                    self.assertEqual(sub.dims, dims)
                    sub.Free()
            topo.Free()
        with self.assertRaises(ValueError):
            topo = comm.Create_cart([comm.Get_size()], [])
        with self.assertRaises(ValueError):
            topo = comm.Create_cart([comm.Get_size()], [0, 0])

    @unittest.skipMPI('MPI(<2.0)')
    def testCartcommZeroDim(self):
        comm = self.COMM
        topo = comm.Create_cart([])
        if topo == MPI.COMM_NULL: return
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
        topo = comm.Create_graph(index[1:], edges)
        self.assertTrue(topo.is_topo)
        self.assertEqual(topo.topology, MPI.GRAPH)
        self.checkHandle(topo)
        topo.Free()
        topo = comm.Create_graph(index, edges)
        self.assertEqual(topo.dims, (len(index)-1, len(edges)))
        self.assertEqual(topo.nnodes, len(index)-1)
        self.assertEqual(topo.nedges, len(edges))
        self.assertEqual(topo.index, index[1:])
        self.assertEqual(topo.edges, edges)
        self.assertEqual(topo.topo, (index[1:], edges))
        neighbors = edges[index[rank]:index[rank+1]]
        self.assertEqual(neighbors, topo.neighbors)
        self.assertEqual(len(neighbors), topo.nneighbors)
        for rank in range(size):
            neighs = topo.Get_neighbors(rank)
            self.assertEqual(neighs, [(rank-1)%size, (rank+1)%size])
        self.assertEqual(topo.indegree, len(neighbors))
        self.assertEqual(topo.outdegree, len(neighbors))
        self.assertEqual(topo.inedges, neighbors)
        self.assertEqual(topo.outedges, neighbors)
        inedges, outedges = topo.inoutedges
        self.assertEqual(inedges, neighbors)
        self.assertEqual(outedges, neighbors)
        topo.Free()

    @unittest.skipMPI('msmpi')
    def testDistgraphcommAdjacent(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        try:
            topo = comm.Create_dist_graph_adjacent(None, None)
            topo.Free()
        except NotImplementedError:
            self.skipTest('mpi-comm-create_dist_graph_adjacent')
        #
        sources = [(rank-2)%size, (rank-1)%size]
        destinations = [(rank+1)%size, (rank+2)%size]
        topo = comm.Create_dist_graph_adjacent(sources, destinations)
        self.assertTrue(topo.is_topo)
        self.assertEqual(topo.topology, MPI.DIST_GRAPH)
        self.checkHandle(topo)
        self.assertEqual(topo.Get_dist_neighbors_count(), (2, 2, False))
        self.assertEqual(topo.Get_dist_neighbors(), (sources, destinations, None))
        self.assertEqual(topo.indegree, len(sources))
        self.assertEqual(topo.outdegree, len(destinations))
        self.assertEqual(topo.inedges, sources)
        self.assertEqual(topo.outedges, destinations)
        inedges, outedges = topo.inoutedges
        self.assertEqual(inedges, sources)
        self.assertEqual(outedges, destinations)
        topo.Free()
        #
        sourceweights = [1, 2]
        destweights   = [3, 4]
        weights = (sourceweights, destweights)
        topo = comm.Create_dist_graph_adjacent(sources, destinations,
                                               sourceweights, destweights)
        self.assertEqual(topo.Get_dist_neighbors_count(), (2, 2, True))
        self.assertEqual(topo.Get_dist_neighbors(), (sources, destinations, weights))
        topo.Free()
        #
        topo = comm.Create_dist_graph_adjacent(sources, None, MPI.UNWEIGHTED, None)
        self.assertEqual(topo.Get_dist_neighbors_count(), (2, 0, False))
        self.assertEqual(topo.Get_dist_neighbors(), (sources, [], None))
        topo.Free()
        topo = comm.Create_dist_graph_adjacent(None, destinations, None, MPI.UNWEIGHTED)
        self.assertEqual(topo.Get_dist_neighbors_count(), (0, 2, False))
        self.assertEqual(topo.Get_dist_neighbors(), ([], destinations, None))
        topo.Free()
        if MPI.Get_version() < (3, 0): return
        topo = comm.Create_dist_graph_adjacent([], [], MPI.WEIGHTS_EMPTY, MPI.WEIGHTS_EMPTY)
        self.assertEqual(topo.Get_dist_neighbors_count(), (0, 0, True))
        self.assertEqual(topo.Get_dist_neighbors(), ([], [], ([], [])))
        topo.Free()

    @unittest.skipMPI('msmpi')
    def testDistgraphcomm(self):
        comm = self.COMM
        size = comm.Get_size()
        rank = comm.Get_rank()
        #
        try:
            topo = comm.Create_dist_graph([], [], [], MPI.UNWEIGHTED)
            topo.Free()
        except NotImplementedError:
            self.skipTest('mpi-comm-create_dist_graph')
        #
        sources = [rank]
        degrees = [3]
        destinations = [(rank-1)%size, rank, (rank+1)%size]
        topo = comm.Create_dist_graph(sources, degrees, destinations, MPI.UNWEIGHTED)
        self.assertTrue(topo.is_topo)
        self.assertEqual(topo.topology, MPI.DIST_GRAPH)
        self.checkHandle(topo)
        self.assertEqual(topo.Get_dist_neighbors_count(), (3, 3, False))
        topo.Free()
        weights = list(range(1,4))
        topo = comm.Create_dist_graph(sources, degrees, destinations, weights)
        self.assertEqual(topo.Get_dist_neighbors_count(), (3, 3, True))
        topo.Free()

    def testCartMap(self):
        comm = self.COMM
        size = comm.Get_size()
        for ndim in (1, 2, 3, 4, 5):
            for periods in (None, True, False):
                dims = MPI.Compute_dims(size, ndim)
                topo = comm.Create_cart(dims, periods, reorder=True)
                rank = comm.Cart_map(dims, periods)
                self.assertEqual(topo.Get_rank(), rank)
                topo.Free()

    def testGraphMap(self):
        comm = self.COMM
        size = comm.Get_size()
        index, edges = [0], []
        for i in range(size):
            pos = index[-1]
            index.append(pos+2)
            edges.append((i-1)%size)
            edges.append((i+1)%size)
        # Version 1
        topo = comm.Create_graph(index, edges, reorder=True)
        rank = comm.Graph_map(index, edges)
        self.assertEqual(topo.Get_rank(), rank)
        topo.Free()
        # Version 2
        topo = comm.Create_graph(index[1:], edges, reorder=True)
        rank = comm.Graph_map(index[1:], edges)
        self.assertEqual(topo.Get_rank(), rank)
        topo.Free()


class TestTopoSelf(BaseTestTopo, unittest.TestCase):
    COMM = MPI.COMM_SELF

class TestTopoWorld(BaseTestTopo, unittest.TestCase):
    COMM = MPI.COMM_WORLD

class TestTopoSelfDup(TestTopoSelf):
    def setUp(self):
        self.COMM = MPI.COMM_SELF.Dup()
    def tearDown(self):
        self.COMM.Free()

class TestTopoWorldDup(TestTopoWorld):
    def setUp(self):
        self.COMM = MPI.COMM_WORLD.Dup()
    def tearDown(self):
        self.COMM.Free()


if __name__ == '__main__':
    unittest.main()
