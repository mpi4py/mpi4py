# http://mvapich.cse.ohio-state.edu/benchmarks/

from mpi4py import MPI

def osu_latency(
    BENCHMARH = "MPI Latency Test",
    skip = 1000,
    loop = 10000,
    skip_large = 10,
    loop_large = 100,
    large_message_size = 8192,
    MAX_MSG_SIZE = 1<<22,
    ):

    comm = MPI.COMM_WORLD
    myid = comm.Get_rank()
    numprocs = comm.Get_size()

    if numprocs != 2:
        if myid == 0:
            errmsg = "This test requires exactly two processes"
        else:
            errmsg = None
        raise SystemExit(errmsg)

    s_buf = allocate(MAX_MSG_SIZE)
    r_buf = allocate(MAX_MSG_SIZE)

    if myid == 0:
        print (f'# {BENCHMARH}')
    if myid == 0:
        print ('# %-8s%20s' % ("Size [B]", "Latency [us]"))

    message_sizes = [0] + [2**i for i in range(30)]
    for size in message_sizes:
        if size > MAX_MSG_SIZE:
            break
        if size > large_message_size:
            skip = skip_large
            loop = loop_large
        iterations = list(range(loop+skip))
        s_msg = [s_buf, size, MPI.BYTE]
        r_msg = [r_buf, size, MPI.BYTE]
        #
        comm.Barrier()
        if myid == 0:
            for i in iterations:
                if i == skip:
                    t_start = MPI.Wtime()
                comm.Send(s_msg, 1, 1)
                comm.Recv(r_msg, 1, 1)
            t_end = MPI.Wtime()
        elif myid == 1:
            for i in iterations:
                comm.Recv(r_msg, 0, 1)
                comm.Send(s_msg, 0, 1)
        #
        if myid == 0:
            latency = (t_end - t_start) * 1e6 / (2 * loop)
            print ('%-10d%20.2f' % (size, latency))


def allocate(n):
    try:
        import mmap
        return mmap.mmap(-1, n)
    except (ImportError, OSError):
        try:
            from numpy import zeros
            return zeros(n, 'B')
        except ImportError:
            from array import array
            return array('B', [0]) * n


if __name__ == '__main__':
    osu_latency()
