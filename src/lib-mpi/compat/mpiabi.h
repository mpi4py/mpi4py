#ifndef PyMPI_COMPAT_MPIABI_H
#define PyMPI_COMPAT_MPIABI_H

/* -------------------------------------------------------------------------- */

#undef MPI_Status_c2f
static int PyMPI_Status_c2f(const MPI_Status *c_status, MPI_Fint *f_status)
{
  if (c_status == MPI_STATUS_IGNORE) return MPI_SUCCESS;
  (void) memcpy(f_status, c_status, sizeof(MPI_Status));
  return MPI_SUCCESS;
}
#define MPI_Status_c2f PyMPI_Status_c2f

#undef MPI_Status_f2c
static int PyMPI_Status_f2c(const MPI_Fint *f_status, MPI_Status *c_status)
{
  if (f_status == NULL) return MPI_SUCCESS;
  (void) memcpy(c_status, f_status, sizeof(MPI_Status));
  return MPI_SUCCESS;
}
#define MPI_Status_f2c PyMPI_Status_f2c

/* -------------------------------------------------------------------------- */

#endif /* !PyMPI_COMPAT_MPIABI_H */
