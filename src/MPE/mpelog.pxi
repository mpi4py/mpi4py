cdef extern from "MPE/mpelog.h" nogil:

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

    PyMPELogAPI *MPELog"(PyMPELog)"

assert MPELog!=NULL

cdef int MPELog_INIT = (MPELog.Initialized()==0)
cdef int MPELog_EXIT = 0
