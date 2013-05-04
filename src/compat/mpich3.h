#ifndef PyMPI_COMPAT_MPICH3_H
#define PyMPI_COMPAT_MPICH3_H

#if defined(MPICH_NUMVERSION)
#if (MPICH_NUMVERSION < 30100000)

static int PyMPI_MPICH3_MPI_Type_size_x(MPI_Datatype datatype, MPI_Count *size)
{
  int ierr = MPI_Type_commit(&datatype); if (ierr) return ierr;
  return MPI_Type_size_x(datatype,size);
}
#define MPI_Type_size_x PyMPI_MPICH3_MPI_Type_size_x

static int PyMPI_MPICH3_MPI_Type_get_extent_x(MPI_Datatype datatype, MPI_Count *lb, MPI_Count *extent)
{
  int ierr = MPI_Type_commit(&datatype); if (ierr) return ierr;
  return MPI_Type_get_extent_x(datatype,lb,extent);
}
#define MPI_Type_get_extent_x PyMPI_MPICH3_MPI_Type_get_extent_x

static int PyMPI_MPICH3_MPI_Type_get_true_extent_x(MPI_Datatype datatype, MPI_Count *lb, MPI_Count *extent)
{
  int ierr = MPI_Type_commit(&datatype); if (ierr) return ierr;
  return MPI_Type_get_true_extent_x(datatype,lb,extent);
}
#define MPI_Type_get_true_extent_x PyMPI_MPICH3_MPI_Type_get_true_extent_x

#endif
#endif

#endif /* !PyMPI_COMPAT_MPICH3_H */
