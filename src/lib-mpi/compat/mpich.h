#ifndef PyMPI_COMPAT_MPICH_H
#define PyMPI_COMPAT_MPICH_H
#if defined(MPICH_NUMVERSION)

/* -------------------------------------------------------------------------- */

#define PyMPI_MPICH4_LT(NUMVERSION) \
  ((MPICH_NUMVERSION >= 40000000) && (MPICH_NUMVERSION < NUMVERSION))

#define PyMPI_MPICH3_GE(NUMVERSION) \
  ((MPICH_NUMVERSION >= NUMVERSION) && (MPICH_NUMVERSION < 40000000))

/* -------------------------------------------------------------------------- */

/* https://github.com/pmodels/mpich/pull/5467 */

#undef  MPI_MAX_PORT_NAME
#define MPI_MAX_PORT_NAME 1024

static int PyMPI_MPICH_port_info(MPI_Info info, MPI_Info *port_info)
{
  int ierr;
# define pympi_str_(s) #s
# define pympi_str(s) pympi_str_(s)
  char key[] = "port_name_size";
  char val[] = pympi_str(MPI_MAX_PORT_NAME);
# undef pympi_str_
# undef pympi_str
  if (info == MPI_INFO_NULL) {
    ierr = MPI_Info_create(port_info); if (ierr) return ierr;
  } else {
    ierr = MPI_Info_dup(info, port_info); if (ierr) return ierr;
  }
  ierr = MPI_Info_set(*port_info, key, val);
  if (ierr) (void) MPI_Info_free(port_info);
  return ierr;
}

static int PyMPI_MPICH_MPI_Open_port(MPI_Info info, char *port_name)
{
  int ierr;
  ierr = PyMPI_MPICH_port_info(info, &info); if (ierr) return ierr;
  ierr = MPI_Open_port(info, port_name);
  (void) MPI_Info_free(&info);
  return ierr;
}
#undef  MPI_Open_port
#define MPI_Open_port PyMPI_MPICH_MPI_Open_port

static int PyMPI_MPICH_MPI_Lookup_name(char     *service_name,
                                       MPI_Info info,
                                       char     *port_name)
{
  int ierr;
  ierr = PyMPI_MPICH_port_info(info, &info); if (ierr) return ierr;
  ierr = MPI_Lookup_name(service_name, info, port_name);
  (void) MPI_Info_free(&info);
  return ierr;
}
#undef  MPI_Lookup_name
#define MPI_Lookup_name PyMPI_MPICH_MPI_Lookup_name

/* -------------------------------------------------------------------------- */

/* https://github.com/pmodels/mpich/issues/6981 */

#if PyMPI_MPICH4_LT(40300300) || PyMPI_LEGACY_ABI
static int PyMPI_MPICH_MPI_Info_free(MPI_Info *info)
{
#if PyMPI_LEGACY_ABI
  if (pympi_numversion() >= 40 && pympi_numversion() <= 41)
#endif
  if (info && *info == MPI_INFO_ENV) {
    (void) MPI_Comm_call_errhandler(MPI_COMM_SELF, MPI_ERR_INFO);
    return MPI_ERR_INFO;
  }
  return MPI_Info_free(info);
}
#undef  MPI_Info_free
#define MPI_Info_free PyMPI_MPICH_MPI_Info_free
#endif

/* -------------------------------------------------------------------------- */

/* https://github.com/pmodels/mpich/issues/6351 */
/* https://github.com/pmodels/mpich/pull/6354   */

#if PyMPI_MPICH4_LT(40100300) || PyMPI_LEGACY_ABI || PyMPI_MPICH3_GE(30000000)
static int PyMPI_MPICH_MPI_Reduce_c(void *sendbuf, void *recvbuf,
                                    MPI_Count count, MPI_Datatype datatype,
                                    MPI_Op op, int root, MPI_Comm comm)
{
  double dummy[1] = {0};
#if PyMPI_LEGACY_ABI
  if (pympi_numversion() < 40)
#endif
#if PyMPI_LEGACY_ABI || PyMPI_MPICH3_GE(30000000)
  if (root == MPI_PROC_NULL) datatype = MPI_UNSIGNED_CHAR;
#endif
#if PyMPI_LEGACY_ABI
  if (pympi_numversion() == 40)
#endif
  if (!sendbuf && (root == MPI_ROOT || root == MPI_PROC_NULL)) sendbuf = dummy;
  return MPI_Reduce_c(sendbuf, recvbuf, count, datatype, op, root, comm);
}
#undef  MPI_Reduce_c
#define MPI_Reduce_c PyMPI_MPICH_MPI_Reduce_c
#endif

/* -------------------------------------------------------------------------- */

/* https://github.com/pmodels/mpich/issues/5413 */
/* https://github.com/pmodels/mpich/pull/6146   */

#if PyMPI_MPICH4_LT(40100300) && !PyMPI_LEGACY_ABI
static int PyMPI_MPICH_MPI_Status_set_elements_c(MPI_Status *status,
                                                 MPI_Datatype datatype,
                                                 MPI_Count elements)
{
  return MPI_Status_set_elements_x(status, datatype, elements);
}
#undef  MPI_Status_set_elements_c
#define MPI_Status_set_elements_c PyMPI_MPICH_MPI_Status_set_elements_c
#endif

/* -------------------------------------------------------------------------- */

#if PyMPI_LEGACY_ABI
#include "mpich3.h"
#endif

/* -------------------------------------------------------------------------- */

#endif /* !MPICH_NUMVERSION      */
#endif /* !PyMPI_COMPAT_MPICH_H */
