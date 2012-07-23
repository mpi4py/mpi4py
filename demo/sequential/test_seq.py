#import mpi4py
#mpi4py.profile("mpe")
from mpi4py import MPI

import unittest

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from seq import Seq
del sys.path[0]

def test():
    size = MPI.COMM_WORLD.Get_size()
    rank = MPI.COMM_WORLD.Get_rank()
    name = MPI.Get_processor_name()
    with Seq(MPI.COMM_WORLD, 1, 10):
        print(
            "Hello, World! I am process %d of %d on %s."
            % (rank, size, name))

if __name__ == "__main__":
    test()
