import sys
sys.path.insert(0, sys.argv[1])

from mpi4py import MPI
parent = MPI.Comm.Get_parent()
parent.Barrier()
parent.Disconnect()
assert parent == MPI.COMM_NULL
parent = MPI.Comm.Get_parent()
assert parent == MPI.COMM_NULL
