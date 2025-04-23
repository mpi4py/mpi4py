# Demonstrate how to work with Python GPU arrays using CUDA-aware MPI.
# A GPU array is allocated and manipulated through Numba, which is
# compliant with the __cuda_array_interface__ standard.
#
# Run this script using the following command:
# mpiexec -n 2 python use_cupy.py

import numpy
from numba import cuda

from mpi4py import MPI


@cuda.jit()
def add_const(arr, value):
    x = cuda.grid(1)
    if x < arr.size:
        arr[x] += value


comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

# Send-Recv
if rank == 0:
    buf = cuda.device_array((20,), dtype="f")
    buf[:] = range(20)
    block = 32
    grid = (buf.size + block - 1) // block
    add_const[grid, block](buf, 100)
    # always make sure the GPU buffer is ready before any MPI operation
    cuda.default_stream().synchronize()
    comm.Send(buf, dest=1, tag=77)
else:
    buf = cuda.device_array((20,), dtype="f")
    cuda.default_stream().synchronize()
    comm.Recv(buf, source=0, tag=77)
    buf = buf.copy_to_host()
    assert numpy.allclose(buf, 100 + numpy.arange(20, dtype="f"))
