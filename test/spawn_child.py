import importlib
import sys

sys.path.insert(0, sys.argv[1])
MPI = importlib.import_module("mpi4py.MPI")

parent = MPI.Comm.Get_parent()
parent.Barrier()
parent.Disconnect()
assert parent == MPI.COMM_NULL
parent = MPI.Comm.Get_parent()
assert parent == MPI.COMM_NULL
