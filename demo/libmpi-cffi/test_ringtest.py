from libmpi import ffi, lib

def ring(comm, count=1, loop=1, skip=0):

    size_p = ffi.new('int*')
    rank_p = ffi.new('int*')
    lib.MPI_Comm_size(comm, size_p)
    lib.MPI_Comm_rank(comm, rank_p)
    size = size_p[0]
    rank = rank_p[0]

    source  = (rank - 1) % size
    dest = (rank + 1) % size
    sbuf = ffi.new('unsigned char[]', [42]*count)
    rbuf = ffi.new('unsigned char[]', [ 0]*count)

    iterations = list(range((loop+skip)))

    if size == 1:
        for i in iterations:
            if i == skip:
                tic = lib.MPI_Wtime()
            lib.MPI_Sendrecv(sbuf, count, lib.MPI_BYTE, dest,   0,
                             rbuf, count, lib.MPI_BYTE, source, 0,
                             comm, lib.MPI_STATUS_IGNORE)
    else:
        if rank == 0:
            for i in iterations:
                if i == skip:
                    tic = lib.MPI_Wtime()
                lib.MPI_Send(sbuf, count, lib.MPI_BYTE, dest,   0, comm)
                lib.MPI_Recv(rbuf, count, lib.MPI_BYTE, source, 0, comm, lib.MPI_STATUS_IGNORE)
        else:
            sbuf = rbuf
            for i in iterations:
                if i == skip:
                    tic = lib.MPI_Wtime()
                lib.MPI_Recv(rbuf, count, lib.MPI_BYTE, source, 0, comm, lib.MPI_STATUS_IGNORE)
                lib.MPI_Send(sbuf, count, lib.MPI_BYTE, dest,   0, comm)
    toc = lib.MPI_Wtime()
    if rank == 0 and ffi.string(sbuf) != ffi.string(rbuf):
        import warnings, traceback
        try:
            warnings.warn("received message does not match!")
        except UserWarning:
            traceback.print_exc()
            lib.MPI_Abort(comm, 2)
    return toc - tic

def ringtest(comm):

    size = ( 1 )
    loop = ( 1 )
    skip = ( 0 )

    lib.MPI_Barrier(comm)
    elapsed = ring(comm, size, loop, skip)

    size_p = ffi.new('int*')
    rank_p = ffi.new('int*')
    lib.MPI_Comm_size(comm, size_p)
    lib.MPI_Comm_rank(comm, rank_p)
    comm_size = size_p[0]
    comm_rank = rank_p[0]

    if comm_rank == 0:
        print ("time for %d loops = %g seconds (%d processes, %d bytes)"
               % (loop, elapsed, comm_size, size))

def main():
    lib.MPI_Init(ffi.NULL, ffi.NULL)
    ringtest(lib.MPI_COMM_WORLD)
    lib.MPI_Finalize()

if __name__ == '__main__':
    main()
