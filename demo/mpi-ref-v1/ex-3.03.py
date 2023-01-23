with open('ex-3.02.py') as source:
    exec(source.read())

assert dtype.size == MPI.DOUBLE.size + MPI.CHAR.size
assert dtype.extent >= dtype.size

dtype.Free()
