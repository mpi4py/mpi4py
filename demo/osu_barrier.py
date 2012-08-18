# http://mvapich.cse.ohio-state.edu/benchmarks/

from mpi4py import MPI

def osu_bcast(
    BENCHMARH = "MPI Barrier Latency Test",
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
        print ('# %s' % (BENCHMARH,))
    if myid == 0:
        print ('# %-8s%20s' % ("Size [B]", "Latency [us]"))

    skip = skip_large
    loop = loop_large
    iterations = list(range(loop+skip))
    #
    comm.Barrier()
    for i in iterations:
        if i == skip:
            t_start = MPI.Wtime()
        comm.Barrier()
    t_end = MPI.Wtime()
    comm.Barrier()
    #
    if myid == 0:
        latency = (t_end - t_start) * 1e6 / loop
        print ('%-10d%20.2f' % (0, latency))


if __name__ == '__main__':
    osu_bcast()
