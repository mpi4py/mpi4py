cdef extern from "MPE/mpe-log.h" nogil:
    ctypedef struct PyMPELogAPI:
        int (*Init)() nogil
        int (*Finish)(char[]) nogil
        int (*Initialized)() nogil
        int (*SyncClocks)() nogil
        int (*Start)() nogil
        int (*Stop)() nogil
        int (*newState)(int, char[], char[], char[], int[2]) nogil
        int (*newEvent)(int, char[], char[], char[], int[1]) nogil
        int (*logEvent)(int, int, char[]) nogil
        int (*packBytes)(char[], int *, char, int, void *) nogil

cdef extern from "MPE/mpe-log.c" nogil:
    PyMPELogAPI *MPELog"(PyMPELog)"
