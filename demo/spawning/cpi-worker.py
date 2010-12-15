from mpi4py import MPI
from array import array

master = MPI.Comm.Get_parent()
nprocs = master.Get_size()
myrank = master.Get_rank()

n  = array('i', [0])
master.Bcast([n, MPI.INT], root=0)
n = n[0]

h = 1.0 / n
s = 0.0
for i in range(myrank+1, n+1, nprocs):
    x = h * (i - 0.5)
    s += 4.0 / (1.0 + x**2)
pi = s * h

pi = array('d', [pi])
master.Reduce(sendbuf=[pi, MPI.DOUBLE],
              recvbuf=None,
              op=MPI.SUM, root=0)

master.Disconnect()
