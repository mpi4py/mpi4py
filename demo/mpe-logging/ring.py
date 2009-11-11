#!/usr/bin/env python
import mpi4py.rc
mpi4py.rc.profile('MPE', logfile='ring')

from mpi4py import MPI
from array import array

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

src  = rank-1
dest = rank+1
if rank == 0:
    src = size-1
elif rank == size-1:
    dest = 0

a1 = array('d', [0]*1000); a1 *= 1000
a2 = array('d', [0]*1000); a2 *= 1000

comm.Sendrecv(sendbuf=a1, recvbuf=a2,
              source=src, dest=dest)
