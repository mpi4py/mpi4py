#!/usr/bin/env python
"""
Parallel Hello World
"""

from mpi4py import MPI

size = MPI.COMM_WORLD.Get_size()
rank = MPI.COMM_WORLD.Get_rank()
name = MPI.Get_processor_name()

print(f"Hello, World! I am process {rank} of {size} on {name}.", flush=True)
