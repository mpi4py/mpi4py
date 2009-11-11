from mpi4py import MPI

blens = (1, 1)
disps = (0, MPI.DOUBLE.size)
types = (MPI.DOUBLE, MPI.CHAR)
type1 = MPI.Datatype.Create_struct(blens, disps, types)

B = (2, 1, 3)
D = (0, 16, 26)
T = (MPI.FLOAT, type1, MPI.CHAR)
dtype = MPI.Datatype.Create_struct(B, D, T)

type1.Free()
dtype.Free()
