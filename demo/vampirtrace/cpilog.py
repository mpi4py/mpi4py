#!/usr/bin/env python

# If you want VampirTrace to log MPI calls, you have to add the two
# lines below at the very beginning of your main bootstrap script.
import mpi4py.rc
mpi4py.rc.threaded = False
mpi4py.rc.profile('vt-mpi', logfile='cpilog')

# Import the MPI extension module
from mpi4py import MPI

# Import the 'array' module
from array import array

# This is just to make the logging
# output a bit more interesting
from time import sleep

comm = MPI.COMM_WORLD
nprocs = comm.Get_size()
myrank = comm.Get_rank()

n  = array('i', [0])
pi = array('d', [0])
mypi = array('d', [0])

def comp_pi(n, myrank=0, nprocs=1):
    h = 1.0 / n;
    s = 0.0;
    for i in range(myrank + 1, n + 1, nprocs):
        x = h * (i - 0.5);
        s += 4.0 / (1.0 + x**2);
    return s * h

comm.Barrier()

for N in [10000]*10:

    if myrank == 0:
        n[0] = N

    comm.Bcast([n, MPI.INT], root=0)

    mypi[0] = comp_pi(n[0], myrank, nprocs)

    comm.Reduce([mypi, MPI.DOUBLE],
                [pi, MPI.DOUBLE],
                op=MPI.SUM, root=0)

    comm.Barrier()

    sleep(0.01)
