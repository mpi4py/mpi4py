#!/usr/bin/env python
from __future__ import with_statement # Python 2.5 and later

# If you want MPE to log MPI calls, you have to add the two lines
# below at the very beginning of your main bootstrap script.
import mpi4py.rc
mpi4py.rc.profile('MPE', logfile='cpilog')

# Import the MPI extension module
from mpi4py import MPI
if 0: # <- use '1' to disable logging of MPI calls
    MPI.Pcontrol(0)

# Import the MPE extension module
from mpi4py import MPE
if 1: # <- use '0' to disable user-defined logging
    # This has to be explicitly called !
    MPE.initLog(logfile='cpilog')
    # Set the log file name (note: no extension)
    MPE.setLogFileName('cpilog')

# Import the 'array' module
from array import array

# This is just to make the logging
# output a bit more interesting
from time import sleep


# User-defined MPE events
cpi_begin = MPE.newLogEvent("ComputePi-Begin", "yellow")
cpi_end   = MPE.newLogEvent("ComputePi-End",   "pink")
# User-defined MPE states
synchronization = MPE.newLogState("Synchronize", "orange")
communication   = MPE.newLogState("Comunicate",  "red")
computation     = MPE.newLogState("Compute",     "green")

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

with synchronization:
    comm.Barrier()

for N in [10000]*10:

    with cpi_begin: pass

    if myrank == 0:
        n[0] = N

    with communication:
        comm.Bcast([n, MPI.INT], root=0)

    with computation:
        mypi[0] = comp_pi(n[0], myrank, nprocs)

    with communication:
        comm.Reduce([mypi, MPI.DOUBLE],
                    [pi, MPI.DOUBLE],
                    op=MPI.SUM, root=0)

    with cpi_end: pass

    with synchronization:
        comm.Barrier()

    sleep(0.01)

# ----------------------- #
# Python 2.3/2.4 version  #
# ----------------------- #

## synchronization.enter()
## comm.Barrier()
## synchronization.exit()
##
## for N in [50000]*10:
##
##     cpi_begin.log()
##
##     if myrank == 0:
##         n[0] = N
##
##     communication.enter()
##     comm.Bcast([n, MPI.INT], root=0)
##     communication.exit()
##
##     computation.enter()
##     mypi[0] = comp_pi(n[0], myrank, nprocs)
##     computation.exit()
##
##     communication.enter()
##     comm.Reduce([mypi, MPI.DOUBLE],
##                 [pi, MPI.DOUBLE],
##                 op=MPI.SUM, root=0)
##     communication.exit()
##
##     cpi_end.log()
##
##     synchronization.enter()
##     comm.Barrier()
##     synchronization.exit()
##
##     sleep(0.01)
