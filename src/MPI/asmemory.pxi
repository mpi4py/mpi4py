#------------------------------------------------------------------------------

cdef extern from "Python.h":
    object PyLong_FromVoidPtr(void *)
    void*  PyLong_AsVoidPtr(object)

#------------------------------------------------------------------------------

cdef extern from "Python.h":
    object PyMPIMemory_AsMemory(object, void **, Py_ssize_t *)
    object PyMPIMemory_FromMemory(void *, Py_ssize_t)

#------------------------------------------------------------------------------

cdef inline object asmemory(object ob, void **base, MPI_Aint *size):
    cdef void *p = NULL
    cdef Py_ssize_t n = 0
    ob = PyMPIMemory_AsMemory(ob, &p, &n)
    if base: base[0] = p
    if size: size[0] = n
    return ob

cdef inline object tomemory(void *base, MPI_Aint size):
    return PyMPIMemory_FromMemory(base, <Py_ssize_t>size)

#------------------------------------------------------------------------------
