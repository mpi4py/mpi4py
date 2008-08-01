#---------------------------------------------------------------------

cdef extern from *:
    char*  PyMPIString_AsStringAndSize(object,Py_ssize_t*) except NULL
    char*  PyMPIString_AsString(object) except NULL
    object PyMPIString_FromStringAndSize(char*,Py_ssize_t)
    object PyMPIString_FromString(char*)

#---------------------------------------------------------------------

cdef inline object asmpistr(object ob, char **s, Py_ssize_t *n):
    cdef char *sbuf = NULL
    cdef Py_ssize_t slen = 0
    sbuf = PyMPIString_AsStringAndSize(ob, &slen)
    if s: s[0] = sbuf
    if n: n[0] = slen
    return ob

cdef inline object tompistr(char *s, Py_ssize_t n):
    if n < 0:
        return PyMPIString_FromString(s)
    else:
        return PyMPIString_FromStringAndSize(s, n)

#---------------------------------------------------------------------
