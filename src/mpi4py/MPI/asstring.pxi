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
