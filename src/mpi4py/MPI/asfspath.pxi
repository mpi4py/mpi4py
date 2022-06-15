#------------------------------------------------------------------------------

cdef extern from "Python.h":
    object PyOS_FSPath(object)
    object PyUnicode_EncodeFSDefault(object)


cdef object asmpifspath(object path, char *p[]):
    path = PyOS_FSPath(path)
    if PyUnicode_Check(path):
        path = PyUnicode_EncodeFSDefault(path)
    PyBytes_AsStringAndSize(path, p, NULL)
    return path

#------------------------------------------------------------------------------
