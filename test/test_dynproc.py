from mpi4py import MPI
import mpiunittest as unittest
import os
try:
    import socket
except ImportError:
    socket = None


def github():
    return os.environ.get('GITHUB_ACTIONS') == 'true'

def ch4_ucx():
    return 'ch4:ucx' in MPI.Get_library_version()

def ch4_ofi():
    return 'ch4:ofi' in MPI.Get_library_version()

def appnum():
    if MPI.APPNUM == MPI.KEYVAL_INVALID: return None
    return MPI.COMM_WORLD.Get_attr(MPI.APPNUM)

def badport():
    if MPI.get_vendor()[0] != 'MPICH':
        return False
    try:
        port = MPI.Open_port()
        MPI.Close_port(port)
    except:
        port = ""
    return port == ""

@unittest.skipMPI('mpich(<4.3.0)', badport())
@unittest.skipMPI('openmpi(<2.0.0)')
@unittest.skipMPI('openmpi(>=5.0.0,<5.0.4)')
@unittest.skipMPI('msmpi(<8.1.0)')
@unittest.skipMPI('mvapich(<3.0.0)')
@unittest.skipIf(MPI.COMM_WORLD.Get_size() < 2, 'mpi-world-size<2')
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

    def testNamePublishing(self):
        rank = MPI.COMM_WORLD.Get_rank()
        service = f"mpi4py-{rank}"
        port = MPI.Open_port()
        MPI.Publish_name(service, port)
        found =  MPI.Lookup_name(service)
        self.assertEqual(port, found)
        MPI.Unpublish_name(service, port)
        MPI.Close_port(port)

    @unittest.skipMPI('mpich(==3.4.1)', ch4_ofi())
    @unittest.skipMPI('mvapich', ch4_ofi())
    @unittest.skipMPI('intelmpi', MPI.COMM_WORLD.Get_size() > 2 and github())
    def testAcceptConnect(self):
        comm_self  = MPI.COMM_SELF
        comm_world = MPI.COMM_WORLD
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
            self.assertIsNone(message)
        else:
            self.assertEqual(message, TestDPM.message)
        intercomm.Free()

    def testConnectAccept(self):
        comm_self  = MPI.COMM_SELF
        comm_world = MPI.COMM_WORLD
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
            self.assertIsNone(message)
        else:
            self.assertEqual(message, TestDPM.message)
        intercomm.Free()

    @unittest.skipIf(socket is None, 'socket')
    def testJoin(self):
        size = MPI.COMM_WORLD.Get_size()
        rank = MPI.COMM_WORLD.Get_rank()
        server = client = address = None
        host = socket.gethostname()
        addrinfo = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
        addr_families = [info[0] for info in addrinfo]
        # if both INET and INET6 are available, don't assume the order
        # is the same on both server and client. Prefer INET if available.
        addr_family = None
        if socket.AF_INET in addr_families:
            addr_family = socket.AF_INET
        elif socket.AF_INET6 in addr_families:
            addr_family = socket.AF_INET6
        addr_family = MPI.COMM_WORLD.bcast(addr_family, root=0)
        supported = (addr_family in addr_families)
        supported = MPI.COMM_WORLD.allreduce(supported, op=MPI.LAND)
        if not supported:
            self.skipTest("socket-inet")
        # create server/client sockets
        if rank == 0: # server
            server = socket.socket(addr_family, socket.SOCK_STREAM)
            server.bind((host, 0))
            server.listen(0)
        if rank == 1: # client
            client = socket.socket(addr_family, socket.SOCK_STREAM)
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
            except OSError:
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
                    self.assertIsNone(message)
                else:
                    self.assertEqual(message, TestDPM.message)
                intercomm.Free()
        MPI.COMM_WORLD.Barrier()


if __name__ == '__main__':
    unittest.main()
