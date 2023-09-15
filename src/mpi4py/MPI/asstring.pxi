# -----------------------------------------------------------------------------

cdef extern from "Python.h":
    int    PyUnicode_Check(object)
    object PyUnicode_AsUTF8String(object)
    object PyUnicode_FromString(const char[])
    object PyUnicode_FromStringAndSize(const char[],Py_ssize_t)
    object PyBytes_FromString(const char[])
    object PyBytes_FromStringAndSize(const char[],Py_ssize_t)
    int    PyBytes_AsStringAndSize(object,char*[],Py_ssize_t*) except -1

# -----------------------------------------------------------------------------

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

# -----------------------------------------------------------------------------

cdef extern from * nogil:
    """
    static int PyMPI_tolower(int c)
    {
      return (c >= 'A' && c <= 'Z') ? c + ('a' - 'A') : c;
    }
    static int PyMPI_strcasecmp(const char *s1, const char *s2)
    {
      int c1, c2;
      do {
         c1 = PyMPI_tolower((int)*s1++);
         c2 = PyMPI_tolower((int)*s2++);
      } while (c1 && c1 == c2);
      return c1 - c2;
    }
    """
    int PyMPI_strcasecmp(const char[],const char[])

cdef int cstr2bool(const char s[]) noexcept nogil:
    cdef const char **T = [b"true",  b"yes", b"on",  b"y", b"1"], *t = NULL
    cdef const char **F = [b"false", b"no",  b"off", b"n", b"0"], *f = NULL
    if s == NULL: return 0
    if s[0] == 0: return 0
    for f in F[:5]:
        if PyMPI_strcasecmp(s, f) == 0:
            return 0
    for t in T[:5]:
        if PyMPI_strcasecmp(s, t) == 0:
            return 1
    return -1

cdef int cstr_is_bool(const char s[]) noexcept nogil:
    return cstr2bool(s) >= 0

cdef int cstr_is_uint(const char s[]) noexcept nogil:
    if s == NULL: return 0
    if s[0] == 0: return 0
    for i in range(<Py_ssize_t>64):
        if s[i] == c' ' or s[i] == c'\t': continue
        if s[i] >= c'0' and s[i] <= c'9': continue
        if s[i] == 0: return 1
        break
    return 0

# -----------------------------------------------------------------------------
