from mpi4py import MPI
import mpiunittest as unittest
try:
    import socket
except ImportError:
    socket = None

def appnum():
    if MPI.APPNUM == MPI.KEYVAL_INVALID: return None
    return MPI.COMM_WORLD.Get_attr(MPI.APPNUM)

@unittest.skipMPI('openmpi(<2.0.0)')
@unittest.skipMPI('MVAPICH2')
@unittest.skipMPI('msmpi(<8.1.0)')
class TestDPM(unittest.TestCase):

    message = [
        None,
        True, False,
        -7, 0, 7,
        -2**63+1, 2**63-1,
        -2.17, 0.0, 3.14,
        1+2j, 2-3j,
        'mpi4py',
        (1, 2, 3),
        [1, 2, 3],
        {1:2},
    ]

    @unittest.skipMPI('mpich', appnum() is None)
    @unittest.skipMPI('MPICH2', appnum() is None)
    @unittest.skipMPI('MPICH1', appnum() is None)
    @unittest.skipMPI('msmpi(<8.1.0)', appnum() is None)
    @unittest.skipMPI('PlatformMPI')
    def testNamePublishing(self):
        rank = MPI.COMM_WORLD.Get_rank()
        service = "mpi4py-%d" % rank
        port = MPI.Open_port()
        MPI.Publish_name(service, port)
        found =  MPI.Lookup_name(service)
        self.assertEqual(port, found)
        MPI.Unpublish_name(service, port)
        MPI.Close_port(port)

    @unittest.skipIf(MPI.COMM_WORLD.Get_size() < 2, 'mpi-world-size<2')
    def testAcceptConnect(self):
        comm_self  = MPI.COMM_SELF
        comm_world = MPI.COMM_WORLD
        wsize = comm_world.Get_size()
        wrank = comm_world.Get_rank()
        group_world = comm_world.Get_group()
        group = group_world.Excl([0])
        group_world.Free()
        comm = comm_world.Create(group)
        group.Free()
        if wrank == 0:
            self.assertEqual(comm, MPI.COMM_NULL)
        else:
            self.assertNotEqual(comm, MPI.COMM_NULL)
            self.assertEqual(comm.size, comm_world.size-1)
            self.assertEqual(comm.rank, comm_world.rank-1)
        if wrank == 0:
            port = MPI.Open_port()
            comm_world.send(port, dest=1)
            intercomm = comm_self.Accept(port)
            self.assertEqual(intercomm.remote_size, comm_world.size-1)
            self.assertEqual(intercomm.size, 1)
            self.assertEqual(intercomm.rank, 0)
            MPI.Close_port(port)
        else:
            if wrank == 1:
                port = comm_world.recv(source=0)
            else:
                port = None
            intercomm = comm.Connect(port, root=0)
            self.assertEqual(intercomm.remote_size, 1)
            self.assertEqual(intercomm.size, comm_world.size-1)
            self.assertEqual(intercomm.rank, comm.rank)
            comm.Free()
        if wrank == 0:
            message = TestDPM.message
            root = MPI.ROOT
        else:
            message = None
            root = 0
        message = intercomm.bcast(message, root)
        if wrank == 0:
            self.assertEqual(message, None)
        else:
            self.assertEqual(message, TestDPM.message)
        intercomm.Free()

    @unittest.skipIf(MPI.COMM_WORLD.Get_size() < 2, 'mpi-world-size<2')
    def testConnectAccept(self):
        comm_self  = MPI.COMM_SELF
        comm_world = MPI.COMM_WORLD
        wsize = comm_world.Get_size()
        wrank = comm_world.Get_rank()
        group_world = comm_world.Get_group()
        group = group_world.Excl([0])
        group_world.Free()
        comm = comm_world.Create(group)
        group.Free()
        if wrank == 0:
            self.assertEqual(comm, MPI.COMM_NULL)
        else:
            self.assertNotEqual(comm, MPI.COMM_NULL)
            self.assertEqual(comm.size, comm_world.size-1)
            self.assertEqual(comm.rank, comm_world.rank-1)
        if wrank == 0:
            port = comm_world.recv(source=1)
            intercomm = comm_self.Connect(port)
            self.assertEqual(intercomm.remote_size, comm_world.size-1)
            self.assertEqual(intercomm.size, 1)
            self.assertEqual(intercomm.rank, 0)
        else:
            if wrank == 1:
                port = MPI.Open_port()
                comm_world.send(port, dest=0)
            else:
                port = None
            intercomm = comm.Accept(port, root=0)
            if wrank == 1:
                MPI.Close_port(port)
            self.assertEqual(intercomm.remote_size, 1)
            self.assertEqual(intercomm.size, comm_world.size-1)
            self.assertEqual(intercomm.rank, comm.rank)
            comm.Free()
        if wrank == 0:
            message = TestDPM.message
            root = MPI.ROOT
        else:
            message = None
            root = 0
        message = intercomm.bcast(message, root)
        if wrank == 0:
            self.assertEqual(message, None)
        else:
            self.assertEqual(message, TestDPM.message)
        intercomm.Free()

    @unittest.skipIf(MPI.COMM_WORLD.Get_size() < 2, 'mpi-world-size<2')
    @unittest.skipIf(socket is None, 'socket')
    def testJoin(self):
        size = MPI.COMM_WORLD.Get_size()
        rank = MPI.COMM_WORLD.Get_rank()
        server = client = address = None
        # crate server/client sockets
        if rank == 0: # server
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            host = socket.gethostname()
            server.bind((host, 0))
            server.listen(0)
        if rank == 1: # client
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # communicate address
        if rank == 0:
            address = server.getsockname()
            MPI.COMM_WORLD.ssend(address, 1)
        if rank == 1:
            address = MPI.COMM_WORLD.recv(None, 0)
        MPI.COMM_WORLD.Barrier()
        # stablish client/server connection
        connected = False
        if rank == 0: # server
            client = server.accept()[0]
            server.close()
        if rank == 1: # client
            try:
                client.connect(address)
                connected = True
            except socket.error:
                raise
        connected = MPI.COMM_WORLD.bcast(connected, root=1)
        # test Comm.Join()
        MPI.COMM_WORLD.Barrier()
        if client:
            fd = client.fileno()
            intercomm = MPI.Comm.Join(fd)
            client.close()
            if intercomm != MPI.COMM_NULL:
                self.assertEqual(intercomm.remote_size, 1)
                self.assertEqual(intercomm.size, 1)
                self.assertEqual(intercomm.rank, 0)
                if rank == 0:
                    message = TestDPM.message
                    root = MPI.ROOT
                else:
                    message = None
                    root = 0
                message = intercomm.bcast(message, root)
                if rank == 0:
                    self.assertEqual(message, None)
                else:
                    self.assertEqual(message, TestDPM.message)
                intercomm.Free()
        MPI.COMM_WORLD.Barrier()


MVAPICH2 = MPI.get_vendor()[0] == 'MVAPICH2'
try:
    if MVAPICH2: raise NotImplementedError
    MPI.Close_port(MPI.Open_port())
except NotImplementedError:
    unittest.disable(TestDPM, 'mpi-dpm')


if __name__ == '__main__':
    unittest.main()
