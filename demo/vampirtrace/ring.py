#!/usr/bin/env python

# If you want VampirTrace to log MPI calls, you have to add the two
# lines below at the very beginning of your main bootstrap script.
import mpi4py.rc
mpi4py.rc.threaded = False
mpi4py.rc.profile('vt-mpi', logfile='ring')

from mpi4py import MPI

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

src  = rank-1
dest = rank+1
if rank == 0:
    src = size-1
if rank == size-1:
    dest = 0

try:
    from numpy import zeros
    a1 = zeros(1000000, 'd')
    a2 = zeros(1000000, 'd')
except ImportError:
    from array import array
    a1 = array('d', [0]*1000); a1 *= 1000
    a2 = array('d', [0]*1000); a2 *= 1000

comm.Sendrecv(sendbuf=a1, recvbuf=a2,
              source=src, dest=dest)

MPI.Request.Waitall([
    comm.Isend(a1, dest=dest),
    comm.Irecv(a2, source=src),
    ])
