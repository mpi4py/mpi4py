from libmpi import ffi
from libmpi.mpi import *

def ring(comm, count=1, loop=1, skip=0):

    size_p = ffi.new('int*')
    rank_p = ffi.new('int*')
    MPI_Comm_size(comm, size_p)
    MPI_Comm_rank(comm, rank_p)
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
                tic = MPI_Wtime()
            MPI_Sendrecv(sbuf, count, MPI_BYTE, dest,   0,
                         rbuf, count, MPI_BYTE, source, 0,
                         comm, MPI_STATUS_IGNORE)
    else:
        if rank == 0:
            for i in iterations:
                if i == skip:
                    tic = MPI_Wtime()
                MPI_Send(sbuf, count, MPI_BYTE, dest,   0, comm)
                MPI_Recv(rbuf, count, MPI_BYTE, source, 0, comm, MPI_STATUS_IGNORE)
        else:
            sbuf = rbuf
            for i in iterations:
                if i == skip:
                    tic = MPI_Wtime()
                MPI_Recv(rbuf, count, MPI_BYTE, source, 0, comm, MPI_STATUS_IGNORE)
                MPI_Send(sbuf, count, MPI_BYTE, dest,   0, comm)
    toc = MPI_Wtime()
    if rank == 0 and ffi.string(sbuf) != ffi.string(rbuf):
        import warnings, traceback
        try:
            warnings.warn("received message does not match!")
        except UserWarning:
            traceback.print_exc()
            MPI_Abort(comm, 2)
    return toc - tic

def ringtest(comm):

    size = ( 1 )
    loop = ( 1 )
    skip = ( 0 )

    MPI_Barrier(comm)
    elapsed = ring(comm, size, loop, skip)

    size_p = ffi.new('int*')
    rank_p = ffi.new('int*')
    MPI_Comm_size(comm, size_p)
    MPI_Comm_rank(comm, rank_p)
    comm_size = size_p[0]
    comm_rank = rank_p[0]

    if comm_rank == 0:
        print ("time for %d loops = %g seconds (%d processes, %d bytes)"
               % (loop, elapsed, comm_size, size))

def main():
    MPI_Init(ffi.NULL, ffi.NULL)
    ringtest(MPI_COMM_WORLD)
    MPI_Finalize()

if __name__ == '__main__':
    main()
