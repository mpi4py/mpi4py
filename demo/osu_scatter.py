# http://mvapich.cse.ohio-state.edu/benchmarks/

from mpi4py import MPI

def osu_bcast(
    BENCHMARH = "MPI Scatter Latency Test",
    skip = 1000,
    loop = 10000,
    skip_large = 10,
    loop_large = 100,
    large_message_size = 8192,
    MAX_MSG_SIZE = 1<<20,
    ):

    comm = MPI.COMM_WORLD
    myid = comm.Get_rank()
    numprocs = comm.Get_size()

    if numprocs < 2:
        if myid == 0:
            errmsg = "This test requires at least two processes"
        else:
            errmsg = None
        raise SystemExit(errmsg)

    if myid == 0:
        s_buf = allocate(MAX_MSG_SIZE*numprocs)
    else:
        r_buf = allocate(MAX_MSG_SIZE)

    if myid == 0:
        print ('# %s' % (BENCHMARH,))
    if myid == 0:
        print ('# %-8s%20s' % ("Size [B]", "Latency [us]"))

    for size in message_sizes(MAX_MSG_SIZE):
        if size > large_message_size:
            skip = skip_large
            loop = loop_large
        iterations = list(range(loop+skip))
        if myid == 0:
            s_msg = [s_buf, size, MPI.BYTE]
            r_msg = MPI.IN_PLACE
        else:
            s_msg = None
            r_msg = [r_buf, size, MPI.BYTE]
        #
        comm.Barrier()
        for i in iterations:
            if i == skip:
                t_start = MPI.Wtime()
            comm.Scatter(s_msg, r_msg, 0)
        t_end = MPI.Wtime()
        comm.Barrier()
        #
        if myid == 0:
            latency = (t_end - t_start) * 1e6 / loop
            print ('%-10d%20.2f' % (size, latency))


def message_sizes(max_size):
    return [0] + [(1<<i) for i in range(30)
                  if (1<<i) <= max_size]

def allocate(n):
    try:
        import mmap
        return mmap.mmap(-1, n)
    except (ImportError, EnvironmentError):
        try:
            from numpy import zeros
            return zeros(n, 'B')
        except ImportError:
            from array import array
            return array('B', [0]) * n


if __name__ == '__main__':
    osu_bcast()
