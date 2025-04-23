# http://mvapich.cse.ohio-state.edu/benchmarks/

from array import array

from mpi4py import MPI


def osu_alltoallv(
    BENCHMARH="MPI Alltoallv Latency Test",
    skip=200,
    loop=1000,
    skip_large=10,
    loop_large=100,
    large_message_size=8192,
    MAX_MSG_SIZE=1 << 20,
):
    comm = MPI.COMM_WORLD
    myid = comm.Get_rank()
    numprocs = comm.Get_size()

    s_buf = allocate(MAX_MSG_SIZE * numprocs)
    r_buf = allocate(MAX_MSG_SIZE * numprocs)
    s_counts = array("i", [0] * numprocs)
    s_displs = array("i", [0] * numprocs)
    r_counts = array("i", [0] * numprocs)
    r_displs = array("i", [0] * numprocs)

    if myid == 0:
        print(f"# {BENCHMARH}")
    if myid == 0:
        print(f"# {'Size [B]':<8s}{'Latency [us]':>20s}")

    for size in message_sizes(MAX_MSG_SIZE):
        if size > large_message_size:
            skip = skip_large
            loop = loop_large
        iterations = list(range(loop + skip))
        disp = 0
        for i in range(numprocs):
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
            print(f"{size:-10d}{latency:20.2f}")


def message_sizes(max_size):
    return [0] + [(1 << i) for i in range(30) if (1 << i) <= max_size]


def allocate(n):
    try:
        import mmap

        return mmap.mmap(-1, n)
    except (ImportError, OSError):
        try:
            from numpy import zeros

            return zeros(n, "B")
        except ImportError:
            from array import array

            return array("B", [0]) * n


if __name__ == "__main__":
    osu_alltoallv()
