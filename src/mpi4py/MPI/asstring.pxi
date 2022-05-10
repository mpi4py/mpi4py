#------------------------------------------------------------------------------

cdef extern from "Python.h":
    int    PyUnicode_Check(object)
    object PyUnicode_AsUTF8String(object)
    object PyUnicode_FromString(const char[])
    object PyUnicode_FromStringAndSize(const char[],Py_ssize_t)
    object PyBytes_FromString(const char[])
    object PyBytes_FromStringAndSize(const char[],Py_ssize_t)
    int    PyBytes_AsStringAndSize(object,char*[],Py_ssize_t*) except -1

#------------------------------------------------------------------------------

cdef inline object asmpistr(object ob, char *s[]):
    if PyUnicode_Check(ob):
        ob = PyUnicode_AsUTF8String(ob)
    PyBytes_AsStringAndSize(ob, s, NULL)
    return ob

cdef inline object tompistr(const char s[], int n):
    return PyUnicode_FromStringAndSize(s, n)

cdef inline object mpistr(const char s[]):
    return PyUnicode_FromString(s)

cdef inline object pystr(const char s[]):
    return PyUnicode_FromString(s)

#------------------------------------------------------------------------------

cdef extern from "Python.h":
    int PyOS_stricmp(const char[],const char[]) nogil

cdef int cstr2bool(const char s[]) nogil:
    cdef const char **T = [b"true",  b"yes", b"on",  b"y", b"1"], *t = NULL
    cdef const char **F = [b"false", b"no",  b"off", b"n", b"0"], *f = NULL
    if s == NULL:
        return 0
    if PyOS_stricmp(s, b"") == 0:
        return 0
    for f in F[:5]:
        if PyOS_stricmp(s, f) == 0:
            return 0
    for t in T[:5]:
        if PyOS_stricmp(s, t) == 0:
            return 1
    return -1

#------------------------------------------------------------------------------
