#if defined(CIBUILDWHEEL) && !defined(MS_WINDOWS)
#  if defined(MPI_ABI_VERSION) && MPI_ABI_VERSION >= 1
#    define PyMPI_STANDARD_ABI 1
#  else
#    define PyMPI_LEGACY_ABI 1
#  endif
#endif
#ifndef PyMPI_STANDARD_ABI
#  define PyMPI_STANDARD_ABI 0
#endif
#ifndef PyMPI_LEGACY_ABI
#  define PyMPI_LEGACY_ABI 0
#endif


#define PyMPI_Pragma(arg) _Pragma(#arg)
#if PyMPI_STANDARD_ABI || PyMPI_LEGACY_ABI
#  if defined(__linux__)
#    define PyMPI_WEAK(sym) PyMPI_Pragma(weak sym)
#  endif
#  if defined(__APPLE__)
#    define PyMPI_WEAK(sym) PyMPI_Pragma(weak sym)
#  endif
#  if defined(__linux__) || defined(__APPLE__)
#    define PyMPI_CALL(fn, ...) do {if (fn) return fn(__VA_ARGS__);} while (0)
#  endif
#endif
#ifndef PyMPI_WEAK
#  define PyMPI_WEAK(sym)
#endif
#ifndef PyMPI_CALL
#  define PyMPI_CALL(fn, ...) do {} while (0)
#endif
#define PyMPI_WEAK_CALL(fn, ...) PyMPI_WEAK(fn) PyMPI_CALL(fn, __VA_ARGS__)


#if PyMPI_STANDARD_ABI || PyMPI_LEGACY_ABI
PyMPI_EXTERN_C_BEGIN

#if PyMPI_STANDARD_ABI
#include "mpiabi1.h"
#endif

#if PyMPI_LEGACY_ABI
#include "mpiabi0.h"
#endif

#if PyMPI_LEGACY_ABI
PyMPI_LOCAL int pympi_numversion(void)
{
  static int numversion = 0;
  if (!numversion) {
    int ierr, version = 0, subversion = 0;
    ierr = MPI_Get_version(&version, &subversion);
    if (ierr == MPI_SUCCESS)
      numversion = 10 * version + subversion;
  }
  return numversion;
}
#endif

PyMPI_EXTERN_C_END
#endif /* PyMPI_STANDARD_ABI || PyMPI_LEGACY_ABI */
