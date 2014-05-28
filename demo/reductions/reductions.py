from mpi4py import MPI

class Intracomm(MPI.Intracomm):
    """
    Intracommunicator class with scalable, point-to-point based
    implementations of global reduction operations.
    """

    def __new__(cls, comm=None):
        return super(Intracomm, cls).__new__(cls, comm)

    def reduce(self, sendobj=None, recvobj=None, op=MPI.SUM, root=0):
        size = self.size
        rank = self.rank
        assert 0 <= root < size
        tag = MPI.COMM_WORLD.Get_attr(MPI.TAG_UB)-1

        recvobj = sendobj
        mask = 1

        while mask < size:
            if (mask & rank) != 0:
                target = (rank & ~mask) % size
                self.send(recvobj, dest=target, tag=tag)
            else:
                target = (rank | mask)
                if target < size:
                    tmp = self.recv(None, source=target, tag=tag)
                    recvobj = op(recvobj, tmp)
            mask <<= 1

        if root != 0:
            if rank == 0:
                self.send(recvobj, dest=root, tag=tag)
            elif rank == root:
                recvobj = self.recv(None, source=0, tag=tag)

        if rank != root:
            recvobj = None

        return recvobj

    def allreduce(self, sendobj=None, recvobj=None, op=MPI.SUM):
        recvobj = self.reduce(sendobj, recvobj, op, 0)
        recvobj = self.bcast(recvobj, 0)
        return recvobj

    def scan(self, sendobj=None, recvobj=None, op=MPI.SUM):
        size = self.size
        rank = self.rank
        tag = MPI.COMM_WORLD.Get_attr(MPI.TAG_UB)-1

        recvobj = sendobj
        partial = sendobj
        mask = 1

        while mask < size:
            target = rank ^ mask
            if target < size:
                tmp = self.sendrecv(partial, dest=target, source=target,
                                    sendtag=tag, recvtag=tag)
                if rank > target:
                    partial = op(tmp, partial)
                    recvobj = op(tmp, recvobj)
                else:
                    tmp = op(partial, tmp)
                    partial = tmp
            mask <<= 1

        return recvobj

    def exscan(self, sendobj=None, recvobj=None, op=MPI.SUM):
        size = self.size
        rank = self.rank
        tag = MPI.COMM_WORLD.Get_attr(MPI.TAG_UB)-1

        recvobj = sendobj
        partial = sendobj
        mask = 1
        flag = False

        while mask < size:
            target = rank ^ mask
            if target < size:
                tmp = self.sendrecv(partial, dest=target, source=target,
                                    sendtag=tag, recvtag=tag)
                if rank > target:
                    partial = op(tmp, partial)
                    if rank != 0:
                        if not flag:
                            recvobj = tmp
                            flag = True
                        else:
                            recvobj = op(tmp, recvobj)
                else:
                    tmp = op(partial, tmp)
                    partial = tmp
            mask <<= 1

        if rank == 0:
            recvobj = None

        return recvobj
