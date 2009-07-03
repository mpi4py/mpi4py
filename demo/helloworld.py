#!/usr/bin/env python
"""
Parallel Hello World
"""

from mpi4py import MPI
import sys

hwmess = "Hello, World! I am process %d of %d on %s.\n"
myrank = MPI.COMM_WORLD.Get_rank()
nprocs = MPI.COMM_WORLD.Get_size()
procnm = MPI.Get_processor_name()
sys.stdout.write(hwmess % (myrank, nprocs, procnm))
