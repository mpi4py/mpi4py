#ifndef PyMPI_COMPAT_IMPI_H
#define PyMPI_COMPAT_IMPI_H

/* -------------------------------------------------------------------------- */

static int PyMPI_IMPI_MPI_Initialized(int *flag)
{
  int ierr;
  ierr = MPI_Initialized(flag); if (ierr) return ierr;
  if (!flag || *flag) return MPI_SUCCESS;
  ierr = MPI_Finalized(flag); if (ierr) return ierr;
  return MPI_SUCCESS;
}
#define MPI_Initialized PyMPI_IMPI_MPI_Initialized

/* -------------------------------------------------------------------------- */

#if PyMPI_LEGACY_ABI
static int PyMPI_IMPI_MPI_Reduce_c(void *sendbuf, void *recvbuf,
                                    MPI_Count count, MPI_Datatype datatype,
                                    MPI_Op op, int root, MPI_Comm comm)
{
  double dummy[1] = {0};
  if (root == MPI_PROC_NULL) datatype = MPI_UNSIGNED_CHAR;
  if (!sendbuf && (root == MPI_ROOT || root == MPI_PROC_NULL)) sendbuf = dummy;
  return MPI_Reduce_c(sendbuf, recvbuf, count, datatype, op, root, comm);
}
#undef  MPI_Reduce_c
#define MPI_Reduce_c PyMPI_IMPI_MPI_Reduce_c
#endif

/* -------------------------------------------------------------------------- */

#if PyMPI_LEGACY_ABI
static int PyMPI_IMPI_MPI_Win_get_attr(MPI_Win win,
                                       int keyval,
                                       void *attrval,
                                       int *flag)
{
  int ierr;
  static MPI_Aint zero[1] = {0}; zero[0] = 0;
  {ierr = MPI_Win_get_attr(win, keyval, attrval, flag); if (ierr) return ierr;}
#if  PyMPI_LEGACY_ABI
  if (pympi_numversion() >= 40) return MPI_SUCCESS;
#endif
  if (keyval == MPI_WIN_SIZE && flag && *flag && attrval)
    if (**((MPI_Aint**)attrval) == -1) *((void**)attrval) = (void*) zero;
  return MPI_SUCCESS;
}
#undef  MPI_Win_get_attr
#define MPI_Win_get_attr PyMPI_IMPI_MPI_Win_get_attr
#endif

/* -------------------------------------------------------------------------- */

/* https://github.com/mpi4py/mpi4py/issues/418#issuecomment-2026805886 */

#if I_MPI_NUMVERSION == 20211200300
#undef  MPI_Status_c2f
#define MPI_Status_c2f PMPI_Status_c2f
#undef  MPI_Status_f2c
#define MPI_Status_f2c PMPI_Status_f2c
#endif

/* -------------------------------------------------------------------------- */

#endif /* !PyMPI_COMPAT_IMPI_H */
