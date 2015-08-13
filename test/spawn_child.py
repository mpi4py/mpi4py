import sys; sys.path.insert(0, sys.argv[1])
import mpi4py
if len(sys.argv) > 2:
    lfn = "runtests-mpi4py-child"
    mpe = sys.argv[2] == 'mpe'
    vt  = sys.argv[2] == 'vt'
    if mpe: mpi4py.profile('mpe', logfile=lfn)
    if vt:  mpi4py.profile('vt',  logfile=lfn)
from mpi4py import MPI
parent = MPI.Comm.Get_parent()
parent.Barrier()
parent.Disconnect()
assert parent == MPI.COMM_NULL
parent = MPI.Comm.Get_parent()
assert parent == MPI.COMM_NULL
