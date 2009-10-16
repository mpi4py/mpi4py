#------------------------------------------------------------------------------

cdef extern from "Python.h":
    void *PyMem_Malloc(size_t)
    void *PyMem_Realloc(void *, size_t)
    void PyMem_Free(void *)

cdef extern from "Python.h":
    object PyLong_FromVoidPtr(void *)
    void*  PyLong_AsVoidPtr(object)

#------------------------------------------------------------------------------

cdef extern from *:
    object allocate"PyMPI_Allocate"(size_t, void **)

cdef extern from *:
    int asmemory"PyMPIMemory_AsMemory"(object, void **, MPI_Aint *) except -1
    object tomemory"PyMPIMemory_FromMemory"(void *, MPI_Aint)

#------------------------------------------------------------------------------
