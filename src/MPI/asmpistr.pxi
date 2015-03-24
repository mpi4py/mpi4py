#------------------------------------------------------------------------------

cdef extern from *:
    object PyMPIString_AsStringAndSize(object,const char*[],Py_ssize_t*)
    object PyMPIString_FromString(const char[])
    object PyMPIString_FromStringAndSize(const char[],Py_ssize_t)

#------------------------------------------------------------------------------

cdef inline object asmpistr(object ob, char *s[], int *n):
    cdef const char *sbuf = NULL
    cdef Py_ssize_t slen = 0, *slenp = NULL
    if n != NULL: slenp = &slen
    ob = PyMPIString_AsStringAndSize(ob, &sbuf, slenp)
    if s != NULL: s[0] = <char*> sbuf
    if n != NULL: n[0] = <int>   slen
    return ob

cdef inline object tompistr(const char s[], int n):
    return PyMPIString_FromStringAndSize(s, n)

cdef inline object mpistr(const char s[]):
    return PyMPIString_FromString(s)

#------------------------------------------------------------------------------
