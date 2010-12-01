class Seq(object):

    """
    Sequential execution
    """

    def __init__(self, comm, ng=1, tag=0):
        ng = int(ng)
        tag = int(tag)
        assert ng >= 1
        assert ng <= comm.Get_size()
        self.comm = comm
        self.ng = ng
        self.tag = tag

    def __enter__(self):
        self.begin()
        return self

    def __exit__(self, *exc):
        self.end()
        return None

    def begin(self):
        """
        Begin a sequential execution of a section of code
        """
        comm = self.comm
        size = comm.Get_size()
        if size == 1: return
        rank = comm.Get_rank()
        ng = self.ng
        tag = self.tag
        if rank != 0:
            comm.Recv([None, 'B'], rank - 1, tag)
        if rank != (size - 1) and (rank % ng) < (ng - 1):
            comm.Send([None, 'B'], rank + 1, tag)

    def end(self):
        """
        End a sequential execution of a section of code
        """
        comm = self.comm
        size = comm.Get_size()
        if size == 1: return
        rank = comm.Get_rank()
        ng = self.ng
        tag = self.tag
        if rank == (size - 1) or (rank % ng) == (ng - 1):
            comm.Send([None, 'B'], (rank + 1) % size, tag)
        if rank == 0:
            comm.Recv([None, 'B'], size - 1, tag)
