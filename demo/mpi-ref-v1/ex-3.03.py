execfile('ex-3.02.py')

assert dtype.size == MPI.DOUBLE.size + MPI.CHAR.size
assert dtype.extent >= dtype.size

dtype.Free()
