#------------------------------------------------------------------------------

cdef extern from "Python.h":
    object PyOS_FSPath(object)

cdef os_fsencode
from os import fsencode as os_fsencode

cdef object asmpifspath(object path, char *p[]):
    path = PyOS_FSPath(path)
    path = os_fsencode(path)
    PyBytes_AsStringAndSize(path, p, NULL)
    return path

#------------------------------------------------------------------------------
