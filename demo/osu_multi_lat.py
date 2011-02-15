# http://mvapich.cse.ohio-state.edu/benchmarks/

from mpi4py import MPI

def osu_multi_lat(
    BENCHMARH = "MPI Multi Latency Test",
    skip_small = 100,
    loop_small = 10000,
    skip_large = 10,
    loop_large = 1000,
    large_message_size = 8192,
    MAX_MSG_SIZE = 1<<22,
    ):

    comm = MPI.COMM_WORLD
    myid = comm.Get_rank()
    nprocs = comm.Get_size()
    pairs = nprocs/2

    s_buf = allocate(MAX_MSG_SIZE)
    r_buf = allocate(MAX_MSG_SIZE)

    if myid == 0:
        print ('# %s' % (BENCHMARH,))
    if myid == 0:
        print ('# %-8s%20s' % ("Size [B]", "Latency [us]"))

    message_sizes = [0] + [2**i for i in range(30)]
    for size in message_sizes:
        if size > MAX_MSG_SIZE:
            break
        if size > large_message_size:
            skip = skip_large
            loop = loop_large
        else:
            skip = skip_small
            loop = loop_small
        iterations = list(range(loop+skip))
        s_msg = [s_buf, size, MPI.BYTE]
        r_msg = [r_buf, size, MPI.BYTE]
        #
        comm.Barrier()
        if myid < pairs:
            partner = myid + pairs
            for i in iterations:
                if i == skip:
                    t_start = MPI.Wtime()
                comm.Send(s_msg, partner, 1)
                comm.Recv(r_msg, partner, 1)
            t_end = MPI.Wtime()
        else:
            partner = myid - pairs
            for i in iterations:
                if i == skip:
                    t_start = MPI.Wtime()
                comm.Recv(r_msg, partner, 1)
                comm.Send(s_msg, partner, 1)
            t_end = MPI.Wtime()
        #
        latency = (t_end - t_start) * 1e6 / (2 * loop)
        total_lat = comm.reduce(latency, root=0, op=MPI.SUM)
        if myid == 0:
            avg_lat = total_lat/(pairs * 2)
            print ('%-10d%20.2f' % (size, avg_lat))


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
    osu_multi_lat()
