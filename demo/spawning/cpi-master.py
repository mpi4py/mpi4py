from mpi4py import MPI
from array import array
from math import pi as PI
from sys import argv

cmd = 'cpi-worker-py.exe'
if len(argv) > 1: cmd = argv[1]
print("%s -> %s" % (argv[0], cmd))

worker = MPI.COMM_SELF.Spawn(cmd, None, 5)

n  = array('i', [100])
worker.Bcast([n,MPI.INT], root=MPI.ROOT)

pi = array('d', [0.0])
worker.Reduce(sendbuf=None,
              recvbuf=[pi, MPI.DOUBLE],
              op=MPI.SUM, root=MPI.ROOT)
pi = pi[0]

worker.Disconnect()

print('pi: %.16f, error: %.16f' % (pi, abs(PI-pi)))
