/* Generated with `python conf/mpiapigen.py` */
#if defined(__linux__) || defined(__APPLE__)

#define _pympi_Pragma(arg) _Pragma(#arg)
#ifdef __linux__
#  define _pympi_WEAK(func) _pympi_Pragma(weak func)
#endif
#ifdef __APPLE__
#  define _pympi_WEAK(func) _pympi_Pragma(weak_import func)
#endif
#define _pympi_CALL(func, ...) \
(func ? func(__VA_ARGS__) : _pympi__##func(__VA_ARGS__))

#ifdef __cplusplus
extern "C"
#endif

#ifdef __cplusplus
}
#endif

#undef _pympi_CALL
#undef _pympi_WEAK
#undef _pympi_Pragma

#endif /* linux || APPLE */
