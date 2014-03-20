#!/usr/bin/env python
"""
Parallel PI computation using Dynamic Process Management (DPM)
within Python objects exposing memory buffers (requires NumPy).

usage:

  + parent/child model::

      $ mpiexec -n 1 python cpi-dpm.py [nchilds]

  + client/server model::

      $ [xterm -e] mpiexec -n <nprocs> python cpi-dpm.py server [-v] &
      $ [xterm -e] mpiexec -n 1 python cpi-dpm.py client [-v]
"""

import sys
from mpi4py import MPI
import numpy as N

def get_n():
    prompt = "Enter the number of intervals: (0 quits) "
    try:
        n = int(input(prompt))
        if n < 0: n = 0
    except:
        n = 0
    return n

def view(pi, np=None, wt=None):
    from math import pi as PI
    prn = sys.stdout.write
    if pi is not None:
        prn("computed pi is:  %.16f\n"  % pi)
        prn("absolute error:  %.16f\n" % abs(pi - PI))
    if np is not None:
        prn("computing units: %d processes\n" % np)
    if wt is not None:
        prn("wall clock time: %g seconds\n" % wt)
    sys.stdout.flush()

def comp_pi(n, comm, root=0):
    nprocs = comm.Get_size()
    myrank = comm.Get_rank()
    n = N.array(n, 'i')
    comm.Bcast([n, MPI.INT], root=root)
    if n == 0: return 0.0
    h = 1.0 / n;
    s = 0.0;
    for i in range(myrank, n, nprocs):
        x = h * (i + 0.5);
        s += 4.0 / (1.0 + x**2);
    mypi = s * h
    mypi = N.array(mypi, 'd')
    pi   = N.array(0, 'd')
    comm.Reduce([mypi, MPI.DOUBLE],
                [pi,   MPI.DOUBLE],
                root=root, op=MPI.SUM)
    return pi

def master(icomm):
    n = get_n()
    wt = MPI.Wtime()
    n =  N.array(n, 'i')
    icomm.Send([n, MPI.INT], dest=0)
    pi = N.array(0, 'd')
    icomm.Recv([pi, MPI.DOUBLE], source=0)
    wt = MPI.Wtime() - wt
    if n == 0: return
    np = icomm.Get_remote_size()
    view(pi, np, wt)

def worker(icomm):
    myrank = icomm.Get_rank()
    if myrank == 0:
        source = dest = 0
    else:
        source = dest = MPI.PROC_NULL
    n =  N.array(0, 'i')
    icomm.Recv([n, MPI.INT], source=source)
    pi = comp_pi(n, comm=MPI.COMM_WORLD, root=0)
    pi = N.array(pi, 'd')
    icomm.Send([pi, MPI.DOUBLE], dest=dest)


# Parent/Child

def main_parent(nprocs=1):
    assert nprocs > 0
    assert MPI.COMM_WORLD.Get_size() == 1
    icomm = MPI.COMM_WORLD.Spawn(command=sys.executable,
                                 args=[__file__, 'child'],
                                 maxprocs=nprocs)
    master(icomm)
    icomm.Disconnect()

def main_child():
    icomm = MPI.Comm.Get_parent()
    assert icomm != MPI.COMM_NULL
    worker(icomm)
    icomm.Disconnect()

# Client/Server

def main_server(COMM):
    nprocs = COMM.Get_size()
    myrank = COMM.Get_rank()

    service, port, info = None, None, MPI.INFO_NULL
    if myrank == 0:
        port = MPI.Open_port(info)
        log(COMM, "open port '%s'", port)
        service = 'cpi'
        MPI.Publish_name(service, port, info)
        log(COMM, "service '%s' published.", service)
    else:
        port = ''

    log(COMM, "waiting for client connection ...")
    icomm = COMM.Accept(port, info, root=0)
    log(COMM, "client connection accepted.")

    worker(icomm)

    log(COMM, "disconnecting from client ...")
    icomm.Disconnect()
    log(COMM, "client disconnected.")

    if myrank == 0:
        MPI.Unpublish_name(service, port, info)
        log(COMM, "service '%s' unpublished", port)
        MPI.Close_port(port)
        log(COMM, "closed  port '%s' ", port)


def main_client(COMM):
    assert COMM.Get_size() == 1

    service, info = 'cpi', MPI.INFO_NULL
    port = MPI.Lookup_name(service, info)
    log(COMM, "service '%s' found in port '%s'.", service, port)

    log(COMM, "connecting to server ...")
    icomm = COMM.Connect(port, info, root=0)
    log(COMM, "server connected.")

    master(icomm)

    log(COMM, "disconnecting from server ...")
    icomm.Disconnect()
    log(COMM, "server disconnected.")


def main():
    assert len(sys.argv) <= 2

    if 'server' in sys.argv:
        main_server(MPI.COMM_WORLD)
    elif 'client' in sys.argv:
        main_client(MPI.COMM_WORLD)
    elif 'child'  in sys.argv:
        main_child()
    else:
        try:    nchilds = int(sys.argv[1])
        except: nchilds = 2
        main_parent(nchilds)


VERBOSE = False

def log(COMM, fmt, *args):
    if not VERBOSE: return
    if COMM.rank != 0: return
    sys.stdout.write(fmt % args)
    sys.stdout.write('\n')
    sys.stdout.flush()

if __name__ == '__main__':
    if '-v' in sys.argv:
        VERBOSE = True
        sys.argv.remove('-v')
    main()
