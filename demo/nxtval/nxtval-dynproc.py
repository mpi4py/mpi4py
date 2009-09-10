# --------------------------------------------------------------------

from mpi4py import MPI
import sys, os

class Counter(object):

    def __init__(self, comm):
        assert not comm.Is_inter()
        self.comm = comm.Dup()
        # start counter process
        script  = os.path.abspath(__file__)
        if script[-4:] in ('.pyc', '.pyo'):
            script = script[:-1]
        self.child = self.comm.Spawn(sys.executable,
                                     [script, '--child'], 1)

    def free(self):
        self.comm.Barrier()
        # stop counter process
        rank = self.child.Get_rank()
        if rank == 0:
            self.child.send(None, 0, 1)
        self.child.Disconnect()
        #
        self.comm.Free()

    def next(self):
        #
        incr = 1
        self.child.send(incr, 0, 0)
        ival = self.child.recv(None, 0, 0)
        nxtval = ival
        #
        return nxtval

# --------------------------------------------------------------------

def _counter_child():
    parent = MPI.Comm.Get_parent()
    assert parent != MPI.COMM_NULL
    try:
        counter = 0
        status = MPI.Status()
        any_src, any_tag = MPI.ANY_SOURCE, MPI.ANY_TAG
        while True: # server loop
            incr = parent.recv(None, any_src, any_tag, status)
            if status.tag == 1: break
            parent.send(counter, status.source, 0)
            counter += incr
    finally:
        parent.Disconnect()

if __name__ == '__main__':
    if (len(sys.argv) > 1 and
        sys.argv[0] == __file__ and
        sys.argv[1] == '--child'):
        _counter_child()
        sys.exit(0)

# --------------------------------------------------------------------

def test():
    vals = []
    counter = Counter(MPI.COMM_WORLD)
    for i in range(5):
        c = counter.next()
        vals.append(c)
    counter.free()
    #
    vals = MPI.COMM_WORLD.allreduce(vals)
    assert sorted(vals) == list(range(len(vals)))

if __name__ == '__main__':
    test()

# --------------------------------------------------------------------
