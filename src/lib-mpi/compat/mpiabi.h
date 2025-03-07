#ifndef PyMPI_COMPAT_MPIABI_H
#define PyMPI_COMPAT_MPIABI_H

/* -------------------------------------------------------------------------- */

#undef MPI_Status_c2f
static int PyMPI_ABI_Status_c2f(const MPI_Status *c_status, MPI_Fint *f_status)
{
  if (c_status == NULL || f_status == NULL) return MPI_ERR_ARG;
  *(MPI_Status *)(char *)f_status = *c_status;
  return MPI_SUCCESS;
}
#define MPI_Status_c2f PyMPI_ABI_Status_c2f

#undef MPI_Status_f2c
static int PyMPI_ABI_Status_f2c(const MPI_Fint *f_status, MPI_Status *c_status)
{
  if (c_status == NULL || f_status == NULL) return MPI_ERR_ARG;
  *c_status = *(MPI_Status *)(char *)f_status;
  return MPI_SUCCESS;
}
#define MPI_Status_f2c PyMPI_ABI_Status_f2c

/* -------------------------------------------------------------------------- */

#endif /* !PyMPI_COMPAT_MPIABI_H */
