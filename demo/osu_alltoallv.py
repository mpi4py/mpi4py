# http://mvapich.cse.ohio-state.edu/benchmarks/

from mpi4py import MPI
from array import array

def osu_alltoall(
    BENCHMARH = "MPI Alltoallv Latency Test",
    skip = 200,
    loop = 1000,
    skip_large = 10,
    loop_large = 100,
    large_message_size = 8192,
    MAX_MSG_SIZE = 1<<20,
    ):

    comm = MPI.COMM_WORLD
    myid = comm.Get_rank()
    numprocs = comm.Get_size()

    s_buf = allocate(MAX_MSG_SIZE*numprocs)
    r_buf = allocate(MAX_MSG_SIZE*numprocs)
    array_int = lambda n: array('i', [0]*n) 
    s_counts = array_int(numprocs) 
    s_displs = array_int(numprocs)
    r_counts = array_int(numprocs)
    r_displs = array_int(numprocs)

    if myid == 0:
        print ('# %s' % (BENCHMARH,))
    if myid == 0:
        print ('# %-8s%20s' % ("Size [B]", "Latency [us]"))

    for size in message_sizes(MAX_MSG_SIZE):
        if size > large_message_size:
            skip = skip_large
            loop = loop_large
        iterations = list(range(loop+skip))
        disp = 0
        for i in range (numprocs):
            s_counts[i] = r_counts[i] = size
            s_displs[i] = r_displs[i] = disp
            disp += size
        s_msg = [s_buf, (s_counts, s_displs), MPI.BYTE]
        r_msg = [r_buf, (r_counts, r_displs), MPI.BYTE]
        #
        comm.Barrier()
        for i in iterations:
            if i == skip:
                t_start = MPI.Wtime()
            comm.Alltoallv(s_msg, r_msg)
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
    osu_alltoall()
