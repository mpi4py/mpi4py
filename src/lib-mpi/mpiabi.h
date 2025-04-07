#if defined(PYMPIABI)
#  if defined(MPI_ABI_VERSION) && MPI_ABI_VERSION >= 1
#    define PyMPI_STANDARD_ABI 1
#  else
#    define PyMPI_LEGACY_ABI 1
#  endif
#endif
#if defined(MSMPI_VER)
#  undef PyMPI_LEGACY_ABI
#endif
#ifndef PyMPI_STANDARD_ABI
#  define PyMPI_STANDARD_ABI 0
#endif
#ifndef PyMPI_LEGACY_ABI
#  define PyMPI_LEGACY_ABI 0
#endif

#if PyMPI_STANDARD_ABI || PyMPI_LEGACY_ABI
#if defined(__linux__) || defined(__APPLE__)
#define PyMPI_Pragma(arg) _Pragma(#arg)
#define PyMPI_WEAK_LOAD(symbol) PyMPI_Pragma(weak symbol)
#define PyMPI_WEAK_CALL(fn, ...) \
PyMPI_WEAK_LOAD(fn) do { if (fn) return fn(__VA_ARGS__); } while (0)
#endif /* Linux || macOS */
#endif

#if PyMPI_STANDARD_ABI || PyMPI_LEGACY_ABI
#if defined(MS_WINDOWS)
#include <windows.h>
static FARPROC _pympi_GetProcAddress(const char *symbol)
{
  static HMODULE hModule = NULL;
  if (!hModule)
    GetModuleHandleEx(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS |
                      GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
                      (LPCSTR) MPI_Init, &hModule);
  return GetProcAddress(hModule, symbol);
}
#define PyMPI_WEAK_LOAD(symbol)
#define PyMPI_WEAK_CALL(fn, ...) do \
{ \
  static __typeof__(&fn) _pympi_fp_##fn = (__typeof__(&fn)) -1; \
  if (_pympi_fp_##fn == (__typeof__(&fn)) -1) \
    _pympi_fp_##fn = (__typeof__(&fn)) _pympi_GetProcAddress(#fn); \
  if (_pympi_fp_##fn) return (*_pympi_fp_##fn)(__VA_ARGS__); \
} while (0)
#endif /* Windows */
#endif

#ifndef PyMPI_WEAK_LOAD
#  define PyMPI_WEAK_LOAD(sym)
#endif
#ifndef PyMPI_WEAK_CALL
#  define PyMPI_WEAK_CALL(fn, ...) do {} while (0)
#endif

#if PyMPI_STANDARD_ABI || PyMPI_LEGACY_ABI
PyMPI_EXTERN_C_BEGIN

#if PyMPI_STANDARD_ABI
#include "mpiabi1.h"
#endif

#if PyMPI_LEGACY_ABI
#include "mpiabi0.h"
#endif

#if PyMPI_STANDARD_ABI || PyMPI_LEGACY_ABI
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
