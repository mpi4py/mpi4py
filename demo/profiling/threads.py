#!/usr/bin/env python

if False:
    import mpi4py
    name = "name" # lib{name}.so
    path = []
    mpi4py.profile(name, path=path)

import threading
from mpi4py import MPI
from array import array

send_msg = array('i', [7]*1000); send_msg *= 1000
recv_msg = array('i', [0]*1000); recv_msg *= 1000

def self_send(comm, rank):
    comm.Send([send_msg, MPI.INT], dest=rank, tag=0)

def self_recv(comm, rank):
    comm.Recv([recv_msg, MPI.INT], source=rank, tag=0)

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
send_thread = threading.Thread(target=self_send, args=(comm, rank))
recv_thread = threading.Thread(target=self_recv, args=(comm, rank))

send_thread.start()
recv_thread.start()
recv_thread.join()
send_thread.join()
