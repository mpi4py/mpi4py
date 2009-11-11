from mpi4py import MPI

# Type = { (double, 0), (char, 8) }

blens = (1, 1)
disps = (0, MPI.DOUBLE.size)
types = (MPI.DOUBLE, MPI.CHAR)

dtype = MPI.Datatype.Create_struct(blens, disps, types)

if 'ex-3.02' in __file__:
    dtype.Free()
