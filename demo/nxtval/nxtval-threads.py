# -----------------------------------------------------------------------------

from mpi4py import MPI
from array import array
from threading import Thread

class Counter(object):

    def __init__(self, comm):
        # duplicate communicator
        assert not comm.Is_inter()
        self.comm = comm.Dup()
        # start counter thread
        self.thread = None
        rank = self.comm.Get_rank()
        if rank == 0:
            self.thread = Thread(target=self._counter_thread)
            self.thread.start()

    def _counter_thread(self):
        incr = array('i', [0])
        ival = array('i', [0])
        status = MPI.Status()
        while True: # server loop
            self.comm.Recv([incr, MPI.INT],
                           MPI.ANY_SOURCE, MPI.ANY_TAG,
                           status)
            if status.Get_tag() == 1:
                return
            self.comm.Send([ival, MPI.INT],
                           status.Get_source(), 0)
            ival[0] += incr[0]

    def free(self):
        self.comm.Barrier()
        # stop counter thread
        rank = self.comm.Get_rank()
        if rank == 0:
            self.comm.Send([None, MPI.INT], 0, 1)
            self.thread.join()
        #
        self.comm.Free()

    def next(self):
        incr = array('i', [1])
        ival = array('i', [0])
        self.comm.Send([incr, MPI.INT], 0, 0)
        self.comm.Recv([ival, MPI.INT], 0, 0)
        nxtval = ival[0]
        return nxtval

# -----------------------------------------------------------------------------

def test_thread_level():
    import sys
    flag = (MPI.Query_thread() == MPI.THREAD_MULTIPLE)
    flag = MPI.COMM_WORLD.bcast(flag, root=0)
    if not flag:
        if MPI.COMM_WORLD.Get_rank() == 0:
            sys.stderr.write("MPI does not provide enough thread support\n")
        sys.exit(0)

def test():
    vals = []
    counter = Counter(MPI.COMM_WORLD)
    for i in range(5):
        c = counter.next()
        vals.append(c)
    counter.free()

    vals = MPI.COMM_WORLD.allreduce(vals)
    assert sorted(vals) == list(range(len(vals)))

if __name__ == '__main__':
    test_thread_level()
    test()

# -----------------------------------------------------------------------------
