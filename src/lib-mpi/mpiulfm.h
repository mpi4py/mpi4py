#ifndef PyMPI_SKIP_MPIULFM
#define PyMPI_SKIP_MPIULFM 0
#endif

#if MPI_VERSION < 6 && !PyMPI_SKIP_MPIULFM

#if defined(MPICH_NAME) && (MPICH_NAME >= 3)
#if MPICH_NUMVERSION >= 30200000 && 0
#define PyMPI_HAVE_MPIX_ERR_REVOKED 1
#define PyMPI_HAVE_MPIX_ERR_PROC_FAILED 1
#define PyMPI_HAVE_MPIX_ERR_PROC_FAILED_PENDING 1
#define PyMPI_HAVE_MPIX_Comm_revoke 1
#define PyMPI_HAVE_MPIX_Comm_agree 1
#define PyMPI_HAVE_MPIX_Comm_shrink 1
#endif
#if MPICH_NUMVERSION >= 40200000 && 0
#define PyMPI_HAVE_MPIX_Comm_get_failed 1
#define PyMPI_HAVE_MPIX_Comm_ack_failed 1
#define PyMPI_HAVE_MPIX_Comm_iagree 1
#endif
#endif

#if defined(OPEN_MPI)
#include <mpi-ext.h>
#ifdef OMPI_HAVE_MPI_EXT_FTMPI
#define PyMPI_HAVE_MPIX_ERR_REVOKED 1
#define PyMPI_HAVE_MPIX_ERR_PROC_FAILED 1
#define PyMPI_HAVE_MPIX_ERR_PROC_FAILED_PENDING 1
#define PyMPI_HAVE_MPIX_Comm_revoke 1
#define PyMPI_HAVE_MPIX_Comm_is_revoked 1
#define PyMPI_HAVE_MPIX_Comm_agree 1
#define PyMPI_HAVE_MPIX_Comm_iagree 1
#define PyMPI_HAVE_MPIX_Comm_shrink 1
#ifdef  OMPI_HAVE_MPIX_COMM_GET_FAILED
#define PyMPI_HAVE_MPIX_Comm_get_failed 1
#endif
#ifdef  OMPI_HAVE_MPIX_COMM_ACK_FAILED
#define PyMPI_HAVE_MPIX_Comm_ack_failed 1
#endif
#ifdef  OMPI_HAVE_MPIX_COMM_ISHRINK
#define PyMPI_HAVE_MPIX_Comm_ishrink 1
#endif
#endif
#endif

#endif

/* ---------------------------------------------------------------- */

#ifndef PyMPI_HAVE_MPI_ERR_REVOKED
#ifdef  PyMPI_HAVE_MPIX_ERR_REVOKED
#undef  MPI_ERR_REVOKED
#define MPI_ERR_REVOKED MPIX_ERR_REVOKED
#endif
#endif

#ifndef PyMPI_HAVE_MPI_ERR_PROC_FAILED
#ifdef  PyMPI_HAVE_MPIX_ERR_PROC_FAILED
#undef  MPI_ERR_PROC_FAILED
#define MPI_ERR_PROC_FAILED MPIX_ERR_PROC_FAILED
#endif
#endif

#ifndef PyMPI_HAVE_MPI_ERR_PROC_FAILED_PENDING
#ifdef  PyMPI_HAVE_MPIX_ERR_PROC_FAILED_PENDING
#undef  MPI_ERR_PROC_FAILED_PENDING
#define MPI_ERR_PROC_FAILED_PENDING MPIX_ERR_PROC_FAILED_PENDING
#endif
#endif

#ifndef PyMPI_HAVE_MPI_Comm_revoke
#ifdef  PyMPI_HAVE_MPIX_Comm_revoke
#undef  MPI_Comm_revoke
#define MPI_Comm_revoke MPIX_Comm_revoke
#endif
#endif

#ifndef PyMPI_HAVE_MPI_Comm_is_revoked
#ifdef  PyMPI_HAVE_MPIX_Comm_is_revoked
#undef  MPI_Comm_is_revoked
#define MPI_Comm_is_revoked MPIX_Comm_is_revoked
#endif
#endif

#ifndef PyMPI_HAVE_MPI_Comm_get_failed
#ifdef  PyMPI_HAVE_MPIX_Comm_get_failed
#undef  MPI_Comm_get_failed
#define MPI_Comm_get_failed MPIX_Comm_get_failed
#endif
#endif

#ifndef PyMPI_HAVE_MPI_Comm_ack_failed
#ifdef  PyMPI_HAVE_MPIX_Comm_ack_failed
#undef  MPI_Comm_ack_failed
#define MPI_Comm_ack_failed MPIX_Comm_ack_failed
#endif
#endif

#ifndef PyMPI_HAVE_MPI_Comm_agree
#ifdef  PyMPI_HAVE_MPIX_Comm_agree
#undef  MPI_Comm_agree
#define MPI_Comm_agree MPIX_Comm_agree
#endif
#endif

#ifndef PyMPI_HAVE_MPI_Comm_iagree
#ifdef  PyMPI_HAVE_MPIX_Comm_iagree
#undef  MPI_Comm_iagree
#define MPI_Comm_iagree MPIX_Comm_iagree
#endif
#endif

#ifndef PyMPI_HAVE_MPI_Comm_shrink
#ifdef  PyMPI_HAVE_MPIX_Comm_shrink
#undef  MPI_Comm_shrink
#define MPI_Comm_shrink MPIX_Comm_shrink
#endif
#endif

#ifndef PyMPI_HAVE_MPI_Comm_ishrink
#ifdef  PyMPI_HAVE_MPIX_Comm_ishrink
#undef  MPI_Comm_ishrink
#define MPI_Comm_ishrink MPIX_Comm_ishrink
#endif
#endif

/* ---------------------------------------------------------------- */

PyMPI_EXTERN_C_BEGIN

#if !defined(PyMPI_HAVE_MPI_Comm_revoke)  || PyMPI_LEGACY_ABI
#if !defined(PyMPI_HAVE_MPIX_Comm_revoke) || PyMPI_LEGACY_ABI
#undef MPI_Comm_revoke
static int PyMPI_Comm_revoke(MPI_Comm comm)
{
#ifdef PyMPI_HAVE_MPIX_Comm_revoke
  PyMPI_WEAK_CALL(MPIX_Comm_revoke, comm);
#endif
  return PyMPI_UNAVAILABLE("MPI_Comm_revoke", comm);
}
#define MPI_Comm_revoke PyMPI_Comm_revoke
#endif
#endif

#if !defined(PyMPI_HAVE_MPI_Comm_is_revoked)  || PyMPI_LEGACY_ABI
#if !defined(PyMPI_HAVE_MPIX_Comm_is_revoked) || PyMPI_LEGACY_ABI
#undef MPI_Comm_is_revoked
static int PyMPI_Comm_is_revoked(MPI_Comm comm, int *flag)
{
#ifdef PyMPI_HAVE_MPIX_Comm_is_revoked
  PyMPI_WEAK_CALL(MPIX_Comm_is_revoked, comm, flag);
#endif
  {
    int dummy, ierr;
    ierr = MPI_Comm_test_inter(comm, &dummy);
    if (ierr != MPI_SUCCESS) return ierr;
  }
  if (!flag) {
    (void) MPI_Comm_call_errhandler(comm, MPI_ERR_ARG);
    return MPI_ERR_ARG;
  }
  *flag = 0;
  return MPI_SUCCESS;
}
#define MPI_Comm_is_revoked PyMPI_Comm_is_revoked
#endif
#endif

#if !defined(PyMPI_HAVE_MPI_Comm_get_failed)  || PyMPI_LEGACY_ABI
#if !defined(PyMPI_HAVE_MPIX_Comm_get_failed) || PyMPI_LEGACY_ABI
#undef MPI_Comm_get_failed
static int PyMPI_Comm_get_failed(MPI_Comm comm, MPI_Group *group)
{
#ifdef PyMPI_HAVE_MPIX_Comm_get_failed
  PyMPI_WEAK_CALL(MPIX_Comm_get_failed, comm, group);
#endif
  {
    int dummy, ierr;
    ierr = MPI_Comm_test_inter(comm, &dummy);
    if (ierr != MPI_SUCCESS) return ierr;
  }
  if (!group) {
    (void) MPI_Comm_call_errhandler(comm, MPI_ERR_ARG);
    return MPI_ERR_ARG;
  }
  return MPI_Group_union(MPI_GROUP_EMPTY, MPI_GROUP_EMPTY, group);
}
#define MPI_Comm_get_failed PyMPI_Comm_get_failed
#endif
#endif

#if !defined(PyMPI_HAVE_MPI_Comm_ack_failed)  || PyMPI_LEGACY_ABI
#if !defined(PyMPI_HAVE_MPIX_Comm_ack_failed) || PyMPI_LEGACY_ABI
#undef MPI_Comm_ack_failed
static int PyMPI_Comm_ack_failed(MPI_Comm comm,
                                 int num_to_ack,
                                 int *num_acked)
{
#ifdef PyMPI_HAVE_MPIX_Comm_ack_failed
  PyMPI_WEAK_CALL(MPIX_Comm_ack_failed, comm, num_to_ack, num_acked);
#endif
  {
    int dummy, ierr;
    ierr = MPI_Comm_test_inter(comm, &dummy);
    if (ierr != MPI_SUCCESS) return ierr;
  }
  if (!num_acked) {
    (void) MPI_Comm_call_errhandler(comm, MPI_ERR_ARG);
    return MPI_ERR_ARG;
  }
  (void)num_to_ack;
  *num_acked = 0;
  return MPI_SUCCESS;
}
#define MPI_Comm_ack_failed PyMPI_Comm_ack_failed
#endif
#endif

#if !defined(PyMPI_HAVE_MPI_Comm_agree)  || PyMPI_LEGACY_ABI
#if !defined(PyMPI_HAVE_MPIX_Comm_agree) || PyMPI_LEGACY_ABI
#undef MPI_Comm_agree
static int PyMPI_Comm_agree(MPI_Comm comm, int *flag)
{
#ifdef PyMPI_HAVE_MPIX_Comm_agree
  PyMPI_WEAK_CALL(MPIX_Comm_agree, comm, flag);
#endif
  {
    int ibuf = flag ? *flag : 0;
    return MPI_Allreduce_c(&ibuf, flag, 1, MPI_INT, MPI_BAND, comm);
  }
}
#define MPI_Comm_agree PyMPI_Comm_agree
#endif
#endif

#if !defined(PyMPI_HAVE_MPI_Comm_iagree)  || PyMPI_LEGACY_ABI
#if !defined(PyMPI_HAVE_MPIX_Comm_iagree) || PyMPI_LEGACY_ABI
#undef MPI_Comm_iagree
static int MPIAPI PyMPI_iagree_free_fn(MPI_Comm c, int k, void *v, void *xs)
{ return (void) c, (void) xs, PyMPI_FREE(v), MPI_Comm_free_keyval(&k); }
static int PyMPI_Comm_iagree(MPI_Comm comm, int *flag, MPI_Request *request)
{
#ifdef PyMPI_HAVE_MPIX_Comm_iagree
  PyMPI_WEAK_CALL(MPIX_Comm_iagree, comm, flag, request);
#endif
  {
    int ierr, keyval, *ibuf;
    MPI_Comm_copy_attr_function *copy_fn = MPI_COMM_NULL_COPY_FN;
    MPI_Comm_delete_attr_function *free_fn = PyMPI_iagree_free_fn;
    ierr = MPI_Comm_create_keyval(copy_fn, free_fn, &keyval, NULL);
    if (ierr != MPI_SUCCESS) return ierr;
    ibuf = (int *) PyMPI_MALLOC(sizeof(int));
    ierr = MPI_Comm_set_attr(comm, keyval, ibuf);
    if (ierr != MPI_SUCCESS) return PyMPI_FREE(ibuf), ierr;
    ibuf[0] = flag ? *flag : 0;
    return MPI_Iallreduce_c(ibuf, flag, 1, MPI_INT, MPI_BAND, comm, request);
  }
}
#define MPI_Comm_iagree PyMPI_Comm_iagree
#endif
#endif

#if !defined(PyMPI_HAVE_MPI_Comm_shrink)  || PyMPI_LEGACY_ABI
#if !defined(PyMPI_HAVE_MPIX_Comm_shrink) || PyMPI_LEGACY_ABI
#undef MPI_Comm_shrink
static int PyMPI_Comm_shrink(MPI_Comm comm, MPI_Comm *newcomm)
{
#ifdef PyMPI_HAVE_MPIX_Comm_shrink
  PyMPI_WEAK_CALL(MPIX_Comm_shrink, comm, newcomm);
#endif
  return MPI_Comm_dup(comm, newcomm);
}
#define MPI_Comm_shrink PyMPI_Comm_shrink
#endif
#endif

#if !defined(PyMPI_HAVE_MPI_Comm_ishrink)  || PyMPI_LEGACY_ABI
#if !defined(PyMPI_HAVE_MPIX_Comm_ishrink) || PyMPI_LEGACY_ABI
#undef MPI_Comm_ishrink
static int PyMPI_Comm_ishrink(MPI_Comm comm,
                              MPI_Comm *newcomm,
                              MPI_Request *request)
{
#ifdef PyMPI_HAVE_MPIX_Comm_ishrink
  PyMPI_WEAK_CALL(MPIX_Comm_ishrink, comm, newcomm, request);
#endif
  return MPI_Comm_idup(comm, newcomm, request);
}
#define MPI_Comm_ishrink PyMPI_Comm_ishrink
#endif
#endif

PyMPI_EXTERN_C_END

/* ---------------------------------------------------------------- */
