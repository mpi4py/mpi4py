from mpi4py import MPI
try:
    import numpy
except ImportError:
    raise SystemExit

# send a upper triangular matrix

N = 10

a = numpy.empty((N, N), dtype=float, order='c')
b = numpy.zeros((N, N), dtype=float, order='c')
a.flat = numpy.arange(a.size, dtype=float)

# compute start and size of each row
i = numpy.arange(N)
blocklen = N - i
disp = N * i + i

# create datatype for upper triangular part
upper = MPI.DOUBLE.Create_indexed(blocklen, disp)
upper.Commit()

# send and recv matrix
myrank = MPI.COMM_WORLD.Get_rank()
MPI.COMM_WORLD.Sendrecv((a, 1, upper), myrank, 0,
                        [b, 1, upper], myrank, 0)

assert numpy.allclose(numpy.triu(b), numpy.triu(a))
assert numpy.allclose(numpy.tril(b, -1), numpy.zeros((N,N)))

upper.Free()

