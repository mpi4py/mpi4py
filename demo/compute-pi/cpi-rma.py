#!/usr/bin/env python
"""
Parallel PI computation using Remote Memory Access (RMA)
within Python objects exposing memory buffers (requires NumPy).

usage::

  $ mpiexec -n <nprocs> python cpi-rma.py
"""

from mpi4py import MPI
from math   import pi as PI
from numpy  import array

def get_n():
    prompt  = "Enter the number of intervals: (0 quits) "
    try:
        n = int(input(prompt));
        if n < 0: n = 0
    except:
        n = 0
    return n

def comp_pi(n, myrank=0, nprocs=1):
    h = 1.0 / n;
    s = 0.0;
    for i in range(myrank + 1, n + 1, nprocs):
        x = h * (i - 0.5);
        s += 4.0 / (1.0 + x**2);
    return s * h

def prn_pi(pi, PI):
    message = "pi is approximately %.16f, error is %.16f"
    print  (message % (pi, abs(pi - PI)))

nprocs = MPI.COMM_WORLD.Get_size()
myrank = MPI.COMM_WORLD.Get_rank()

n    = array(0, dtype=int)
pi   = array(0, dtype=float)
mypi = array(0, dtype=float)

if myrank == 0:
    win_n  = MPI.Win.Create(n,  comm=MPI.COMM_WORLD)
    win_pi = MPI.Win.Create(pi, comm=MPI.COMM_WORLD)
else:
    win_n  = MPI.Win.Create(None, comm=MPI.COMM_WORLD)
    win_pi = MPI.Win.Create(None, comm=MPI.COMM_WORLD)

while True:
    if myrank == 0:
        _n = get_n()
        n.fill(_n)
        pi.fill(0.0)
    win_n.Fence()
    if myrank != 0:
        win_n.Get([n, MPI.INT], 0)
    win_n.Fence()
    if n == 0:
        break
    _mypi = comp_pi(n, myrank, nprocs)
    mypi.fill(_mypi)
    win_pi.Fence()
    win_pi.Accumulate([mypi, MPI.DOUBLE], 0, op=MPI.SUM)
    win_pi.Fence()
    if myrank == 0:
        prn_pi(pi, PI)

win_n.Free()
win_pi.Free()
