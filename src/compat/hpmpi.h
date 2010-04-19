#ifndef PyMPI_COMPAT_HPMPI_H
#define PyMPI_COMPAT_HPMPI_H

/* ---------------------------------------------------------------- */

#ifndef MPI_INTEGER1
#define MPI_INTEGER1 ((MPI_Datatype)MPI_Type_f2c(MPIF_INTEGER1))
#endif
#ifndef MPI_INTEGER2
#define MPI_INTEGER2 ((MPI_Datatype)MPI_Type_f2c(MPIF_INTEGER2))
#endif
#ifndef MPI_INTEGER4
#define MPI_INTEGER4 ((MPI_Datatype)MPI_Type_f2c(MPIF_INTEGER4))
#endif
#ifndef MPI_REAL4
#define MPI_REAL4    ((MPI_Datatype)MPI_Type_f2c(MPIF_REAL4))
#endif
#ifndef MPI_REAL8
#define MPI_REAL8    ((MPI_Datatype)MPI_Type_f2c(MPIF_REAL8))
#endif

/* ---------------------------------------------------------------- */

#endif /* !PyMPI_COMPAT_HPMPI_H */
