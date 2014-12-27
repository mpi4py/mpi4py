#!/usr/bin/env python

import mpi4py
mpi4py.rc.threads = True
mpi4py.rc.thread_level = "funneled"
mpi4py.profile('vt-hyb', logfile='threads')

from mpi4py import MPI
from threading import Thread

MPI.COMM_WORLD.Barrier()

# Understanding the Python GIL
# David Beazley, http://www.dabeaz.com
# PyCon 2010, Atlanta, Georgia
# http://www.dabeaz.com/python/UnderstandingGIL.pdf

# Consider this trivial CPU-bound function
def countdown(n):
    while n > 0:
        n -= 1

# Run it once with a lot of work
COUNT = 10000000 # 10 millon
tic = MPI.Wtime()
countdown(COUNT)
toc = MPI.Wtime()
print ("sequential: %f seconds" % (toc-tic))

# Now, subdivide the work across two threads
t1 = Thread(target=countdown, args=(COUNT//2,))
t2 = Thread(target=countdown, args=(COUNT//2,))
tic = MPI.Wtime()
for t in (t1, t2): t.start()
for t in (t1, t2): t.join()
toc = MPI.Wtime()
print ("threaded:   %f seconds" % (toc-tic))
