#include <stdlib.h>
#include <string.h>

#if !defined(PyMPI_EXTERN)
#  define PyMPI_EXTERN extern
#endif
#if !defined(PyMPI_STATIC)
#  define PyMPI_STATIC static
#endif
#if !defined(PyMPI_INLINE)
#  if defined(__cplusplus)
#    define PyMPI_INLINE inline
#  elif (defined(__STDC_VERSION__) && __STDC_VERSION__ >= 199901L)
#    define PyMPI_INLINE inline
#  else
#    define PyMPI_INLINE
#  endif
#endif
#if !defined(PyMPI_LOCAL)
#  define PyMPI_LOCAL PyMPI_STATIC
#endif

#if defined(__cplusplus)
#  define PyMPI_EXTERN_C_BEGIN extern "C" {
#  define PyMPI_EXTERN_C_END   }
#else
#  define PyMPI_EXTERN_C_BEGIN
#  define PyMPI_EXTERN_C_END
#endif

#ifndef PyMPI_MALLOC
  #define PyMPI_MALLOC malloc
#endif
#ifndef PyMPI_FREE
  #define PyMPI_FREE free
#endif
#ifndef PyMPI_MEMCPY
  #define PyMPI_MEMCPY memcpy
#endif

#define PyMPI_NUMVERSION (10 * MPI_VERSION + MPI_SUBVERSION)

#define PyMPI_ERR_UNAVAILABLE (-1431655766) /*0xAAAAAAAA*/

PyMPI_LOCAL int PyMPI_UNAVAILABLE(const char *name, ...)
{ (void)name; return PyMPI_ERR_UNAVAILABLE; }
