# Demonstrate how to work with Python GPU arrays using CUDA-aware MPI.
# We choose the CuPy library for simplicity, but any CUDA array which
# has the __cuda_array_interface__ attribute defined will work.
#
# Run this script using the following command:
# mpiexec -n 2 python use_cupy.py

from mpi4py import MPI
import cupy


comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

# Allreduce
sendbuf = cupy.arange(10, dtype='i')
recvbuf = cupy.empty_like(sendbuf)
# always make sure the GPU buffer is ready before any MPI operation
cupy.cuda.get_current_stream().synchronize()
comm.Allreduce(sendbuf, recvbuf)
assert cupy.allclose(recvbuf, sendbuf*size)

# Bcast
if rank == 0:
    buf = cupy.arange(100, dtype=cupy.complex64)
else:
    buf = cupy.empty(100, dtype=cupy.complex64)
cupy.cuda.get_current_stream().synchronize()
comm.Bcast(buf)
assert cupy.allclose(buf, cupy.arange(100, dtype=cupy.complex64))

# Send-Recv
if rank == 0:
    buf = cupy.arange(20, dtype=cupy.float64)
    cupy.cuda.get_current_stream().synchronize()
    comm.Send(buf, dest=1, tag=88)
else:
    buf = cupy.empty(20, dtype=cupy.float64)
    cupy.cuda.get_current_stream().synchronize()
    comm.Recv(buf, source=0, tag=88)
    assert cupy.allclose(buf, cupy.arange(20, dtype=cupy.float64))
