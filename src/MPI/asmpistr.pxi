#---------------------------------------------------------------------

cdef extern from *:
    object PyMPIString_AsStringAndSize(object,char**,Py_ssize_t*)
    object PyMPIString_FromString(char*)
    object PyMPIString_FromStringAndSize(char*,Py_ssize_t)

#---------------------------------------------------------------------

cdef inline object asmpistr(object ob, char **s, Py_ssize_t *n):
    cdef char *sbuf = NULL
    cdef Py_ssize_t slen = 0
    ob = PyMPIString_AsStringAndSize(ob, &sbuf, &slen)
    if s: s[0] = sbuf
    if n: n[0] = slen
    return ob

cdef inline object tompistr(char *s, Py_ssize_t n):
    if n < 0:
        return PyMPIString_FromString(s)
    else:
        return PyMPIString_FromStringAndSize(s, n)

#---------------------------------------------------------------------
