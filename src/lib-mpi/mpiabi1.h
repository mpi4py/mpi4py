/* Generated with `python conf/mpiapigen.py` */

#if defined(__linux__) || defined(__APPLE__)

#define _pympi_CALL(fn, ...) \
PyMPI_WEAK_CALL(fn, __VA_ARGS__); \
return _pympi__##fn(__VA_ARGS__)

#undef _pympi_CALL

#endif /* linux || APPLE */
