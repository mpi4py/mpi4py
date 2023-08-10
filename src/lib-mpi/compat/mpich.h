#ifndef PyMPI_COMPAT_MPICH_H
#define PyMPI_COMPAT_MPICH_H
#if defined(MPICH_NUMVERSION)

#if (MPICH_NUMVERSION < 40003300) || defined(CIBUILDWHEEL)
static int PyMPI_MPICH_MPI_Status_set_elements_c(MPI_Status *status,
                                                 MPI_Datatype datatype,
                                                 MPI_Count elements)
{
  return MPI_Status_set_elements_x(status, datatype, elements);
}
#define MPI_Status_set_elements_c PyMPI_MPICH_MPI_Status_set_elements_c
#endif

#if defined(CIBUILDWHEEL) && defined(__linux__)
#undef MPI_Status_set_elements_c
extern int MPI_Status_set_elements_c(MPI_Status *, MPI_Datatype, MPI_Count)
__attribute__((weak, alias("PyMPI_MPICH_MPI_Status_set_elements_c")));
#endif

#if (MPICH_NUMVERSION < 40100000) || defined(CIBUILDWHEEL)
static int PyMPI_MPICH_MPI_Reduce_c(const void *sendbuf, void *recvbuf,
                                    MPI_Count count, MPI_Datatype datatype,
                                    MPI_Op op, int root, MPI_Comm comm)
{
  const char dummy[1] = {0};
  if (!sendbuf && (root == MPI_ROOT || root == MPI_PROC_NULL)) sendbuf = dummy;
  return MPI_Reduce_c(sendbuf, recvbuf, count, datatype, op, root, comm);
}
#define MPI_Reduce_c PyMPI_MPICH_MPI_Reduce_c
#endif


#endif /* !MPICH_NUMVERSION      */
#endif /* !PyMPI_COMPAT_MPICH_H */
