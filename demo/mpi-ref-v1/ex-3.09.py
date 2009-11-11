from mpi4py import MPI
try:
    import numpy
except ImportError:
    raise SystemExit

# transpose a matrix a into b

a = numpy.empty((100, 100), dtype=float, order='fortran')
b = numpy.empty((100, 100), dtype=float, order='fortran')
a.flat = numpy.arange(a.size, dtype=float)

lb, sizeofdouble = MPI.DOUBLE.Get_extent()

# create datatype dor one row
# (vector with 100 double entries and stride 100)
row = MPI.DOUBLE.Create_vector(100, 1, 100)

# create datatype for matrix in row-major order

# (one hundred copies of the row datatype, strided one word
#  apart; the succesive row datatypes are interleaved)
xpose = row.Create_hvector(100, 1, sizeofdouble)
xpose.Commit()

# send matrix in row-major order and receive in column major order
abuf = (a, xpose)
bbuf = (b, MPI.DOUBLE)
myrank = MPI.COMM_WORLD.Get_rank()
status = MPI.Status()
MPI.COMM_WORLD.Sendrecv(abuf, myrank, 0, bbuf, myrank, 0, status)

assert numpy.allclose(a, b.transpose())
assert status.Get_count(xpose) == 1
assert status.Get_count(MPI.DOUBLE) == b.size

row.Free()
xpose.Free()

