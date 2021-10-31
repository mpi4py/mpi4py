#!/usr/bin/env python

if False:
    import mpi4py
    name = "name" # lib{name}.so
    path = []
    mpi4py.profile(name, path=path)

# Import the MPI extension module
from mpi4py import MPI

if False: # set to True to disable profiling
    MPI.Pcontrol(0)

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
